"""
Commande Discord : /mentionlist

DESCRIPTION:
    Liste les joueurs du canal et leur activité récompenses/quêtes MJ.
    Met en avant les joueurs oubliés (ni récompense ni quête MJ).

FONCTIONNEMENT:
    - Récupère les auteurs actifs du canal actuel (1000 derniers messages)
    - Parcourt le canal #recompenses depuis la date choisie pour compter les mentions
    - Parcourt le canal #quêtes depuis la date choisie pour trouver les quêtes MJ
    - Affiche TOUS les joueurs, en mettant en avant ceux sans activité

UTILISATION:
    /mentionlist
    /mentionlist public:True
    /mentionlist periode:30j
    /mentionlist public:True periode:30j
    /mentionlist date_debut:15/04/2024
    /mentionlist public:True date_debut:2024-04-15
"""

import discord
from discord import app_commands
from datetime import datetime, timezone, timedelta
import logging
from typing import Optional
from .base import BaseCommand
from utils.channels import ChannelHelper

logger = logging.getLogger(__name__)


class MentionListCommand(BaseCommand):
    """Commande pour lister les mentions et quêtes MJ des utilisateurs du canal."""

    @property
    def name(self) -> str:
        return "mentionlist"

    @property
    def description(self) -> str:
        return "Liste les joueurs du canal avec leurs récompenses et quêtes MJ"

    def register(self, tree: app_commands.CommandTree):
        """Enregistre la commande dans l'arbre des commandes Discord."""

        @tree.command(name=self.name, description=self.description)
        @app_commands.choices(periode=[
            app_commands.Choice(name="📅 Depuis la création du canal", value="creation"),
            app_commands.Choice(name="🕐 30 derniers jours", value="30j"),
        ])
        @app_commands.describe(
            public="Afficher publiquement (visible par tous) - défaut: non",
            periode="Période d'analyse prédéfinie - ignorée si date_debut est fournie",
            date_debut="Date de début personnalisée (ex: 15/04/2024 ou 2024-04-15) - priorité sur période"
        )
        async def mentionlist_command(
            interaction: discord.Interaction,
            public: Optional[bool] = False,
            periode: str = "creation",
            date_debut: Optional[str] = None
        ):
            await self.callback(interaction, public, periode, date_debut)

    async def callback(self, interaction: discord.Interaction, public: Optional[bool] = False, periode: str = "creation", date_debut: Optional[str] = None):
        """
        Exécute la commande mentionlist.

        Args:
            interaction: Interaction Discord
            public: Si True, le message sera visible par tous, sinon temporaire (défaut: False)
            periode: Période d'analyse - 'creation' (depuis création du canal) ou '30j' (30 derniers jours)
        """
        try:
            is_ephemeral = not public
            await interaction.response.defer(ephemeral=is_ephemeral)

            # Récupérer les canaux configurables
            recompenses_channel = ChannelHelper.get_recompenses_channel(interaction.guild)
            if not recompenses_channel:
                error_msg = ChannelHelper.get_channel_error_message(
                    ChannelHelper.RECOMPENSES)
                await interaction.followup.send(error_msg)
                return

            quetes_channel = ChannelHelper.get_quetes_channel(interaction.guild)

            now = datetime.now(timezone.utc)

            # Calculer la date de début
            if date_debut:
                # Date libre saisie par l'utilisateur - formats acceptés
                formats = ["%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%d/%m/%y"]
                parsed = None
                for fmt in formats:
                    try:
                        parsed = datetime.strptime(date_debut.strip(), fmt)
                        break
                    except ValueError:
                        continue
                if not parsed:
                    await interaction.followup.send(
                        f"❌ Format de date invalide : `{date_debut}`\n"
                        "Formats acceptés : `JJ/MM/AAAA` (ex: `15/04/2024`) ou `AAAA-MM-JJ` (ex: `2024-04-15`)",
                        ephemeral=True
                    )
                    return
                start_date = parsed.replace(tzinfo=timezone.utc)
                periode_label = f"depuis le {parsed.strftime('%d/%m/%Y')}"
            elif periode == "creation":
                start_date = interaction.channel.created_at
                periode_label = "depuis la création du canal"
            else:
                start_date = now - timedelta(days=30)
                periode_label = "30 derniers jours"

            # Récupérer les auteurs du canal actuel
            auteurs = {}
            async for msg in interaction.channel.history(limit=1000, oldest_first=True):
                if msg.author.bot:
                    continue
                auteurs[msg.author.id] = msg.author

            # Exclure le créateur du thread si c'est un thread
            if isinstance(interaction.channel, discord.Thread) and interaction.channel.owner_id:
                auteurs.pop(interaction.channel.owner_id, None)

            if not auteurs:
                await interaction.followup.send(
                    "Aucun utilisateur actif trouvé dans ce canal.")
                return

            # --- Compter mentions dans #recompenses ---
            mentions_count = {user_id: 0 for user_id in auteurs.keys()}
            posts_mj_count = {user_id: 0 for user_id in auteurs.keys()}

            async for msg in recompenses_channel.history(limit=1000, after=start_date):
                for mentioned in msg.mentions:
                    if mentioned.id in mentions_count:
                        mentions_count[mentioned.id] += 1

                if msg.author.id in posts_mj_count:
                    mentions_uniques = set(
                        u.id for u in msg.mentions if u.id != msg.author.id
                    )
                    if len(mentions_uniques) >= 2:
                        posts_mj_count[msg.author.id] += 1

            # --- Compter quêtes MJ dans #quêtes ---
            quetes_count = {user_id: 0 for user_id in auteurs.keys()}

            if quetes_channel:
                async for msg in quetes_channel.history(limit=1000, after=start_date):
                    if msg.author.bot:
                        continue
                    for mentioned in msg.mentions:
                        if mentioned.id in quetes_count:
                            quetes_count[mentioned.id] += 1

            # --- Tri : joueurs oubliés d'abord, puis par mentions croissantes ---
            def sort_key(item):
                user_id, mention_count = item
                quetes = quetes_count.get(user_id, 0)
                has_nothing = (mention_count == 0 and quetes == 0)
                return (0 if has_nothing else 1, mention_count, quetes)

            sorted_users = sorted(mentions_count.items(), key=sort_key)

            # --- Construction du message ---
            lines_oublies = []
            lines_actifs = []

            for user_id, mention_count in sorted_users:
                user = auteurs.get(user_id)
                if not user:
                    continue

                posts_mj = posts_mj_count.get(user_id, 0)
                quetes = quetes_count.get(user_id, 0)

                is_oublie = (mention_count == 0 and quetes == 0)

                if is_oublie:
                    line = f"⚠️ **{user.display_name}** - aucune récompense, aucune quête MJ"
                    lines_oublies.append(line)
                else:
                    parts = []
                    if mention_count > 0:
                        parts.append(f"{mention_count} récompense{'s' if mention_count > 1 else ''}")
                    else:
                        parts.append("0 récompense")
                    if quetes > 0:
                        parts.append(f"{quetes} quête{'s' if quetes > 1 else ''} MJ")
                    if posts_mj > 0:
                        parts.append(f"{posts_mj} post{'s' if posts_mj > 1 else ''} MJ")

                    line = f"✅ **{user.display_name}** - {' | '.join(parts)}"
                    lines_actifs.append(line)

            # Assembler la description
            description_parts = []

            if lines_oublies:
                description_parts.append(
                    f"**__Joueurs sans activité ({periode_label}) :__**\n" + "\n".join(lines_oublies)
                )

            if lines_actifs:
                description_parts.append(
                    f"**__Joueurs avec activité :__**\n" + "\n".join(lines_actifs)
                )

            description = "\n\n".join(description_parts) if description_parts else "Aucun joueur trouvé dans ce canal."

            # Embed
            embed = discord.Embed(
                title=f"📊 Suivi joueurs - récompenses & quêtes MJ ({periode_label})",
                description=description,
                color=0xff9900 if lines_oublies else 0x00b0f4)

            embed.add_field(
                name="Canal source",
                value=interaction.channel.mention,
                inline=True
            )

            joueurs_total = len(lines_oublies) + len(lines_actifs)
            embed.add_field(
                name="Joueurs",
                value=f"{joueurs_total} listés ({len(lines_oublies)} sans activité)",
                inline=True
            )

            # Footer
            footer_text = "Récompenses = mentions dans #recompenses | Quêtes MJ = mentions dans #quêtes"
            if not quetes_channel:
                footer_text = "⚠️ Canal quêtes non configuré - seules les récompenses sont vérifiées | " + footer_text
            if public:
                footer_text += f" • Partagé par {interaction.user.display_name}"

            embed.set_footer(text=footer_text)

            await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error(f"Erreur dans la commande /mentionlist : {e}", exc_info=True)
            try:
                if interaction.response.is_done():
                    await interaction.followup.send(
                        "❌ Une erreur inattendue est survenue.")
                else:
                    await interaction.response.send_message(
                        "❌ Une erreur inattendue est survenue.",
                        ephemeral=True)
            except Exception:
                pass
