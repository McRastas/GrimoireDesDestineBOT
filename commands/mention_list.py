"""
Commande Discord : /mentionlist

DESCRIPTION:
    Réunit les infos de /mentionsomeone et /recapmj pour chaque joueur du canal.
    Liste TOUS les joueurs avec leurs récompenses reçues et quêtes MJ menées.
    Met en avant les joueurs oubliés (ni récompense ni quête MJ sur 30 jours).

FONCTIONNEMENT:
    - Récupère les auteurs actifs du canal actuel (1000 derniers messages)
    - Parcourt le canal #recompenses (configuré) sur 30 jours
    - Pour chaque joueur : compte les mentions reçues (récompenses)
    - Pour chaque joueur : compte les posts avec 2+ mentions uniques (quêtes MJ)
    - Affiche TOUS les joueurs, oubliés en premier

UTILISATION:
    /mentionlist
    /mentionlist public:True
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
    """Combine mentionsomeone + recapmj pour tous les joueurs du canal."""

    @property
    def name(self) -> str:
        return "mentionlist"

    @property
    def description(self) -> str:
        return "Liste les joueurs du canal avec récompenses reçues et quêtes MJ (30 jours)"

    def register(self, tree: app_commands.CommandTree):
        """Enregistre la commande dans l'arbre des commandes Discord."""

        @tree.command(name=self.name, description=self.description)
        @app_commands.describe(
            public="Afficher publiquement (visible par tous) - défaut: non"
        )
        async def mentionlist_command(
            interaction: discord.Interaction,
            public: Optional[bool] = False
        ):
            await self.callback(interaction, public)

    async def callback(self, interaction: discord.Interaction, public: Optional[bool] = False):
        try:
            is_ephemeral = not public
            await interaction.response.defer(ephemeral=is_ephemeral)

            # Canal #recompenses via config
            recompenses_channel = ChannelHelper.get_recompenses_channel(interaction.guild)
            if not recompenses_channel:
                error_msg = ChannelHelper.get_channel_error_message(
                    ChannelHelper.RECOMPENSES)
                await interaction.followup.send(error_msg)
                return

            now = datetime.now(timezone.utc)
            thirty_days_ago = now - timedelta(days=30)

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

            # --- Parcours unique de #recompenses (30j) ---
            # mentionsomeone : combien de fois chaque joueur est mentionné
            mentions_count = {uid: 0 for uid in auteurs}
            # recapmj : combien de posts avec 2+ mentions uniques chaque joueur a fait
            posts_mj_count = {uid: 0 for uid in auteurs}
            messages_parcourus = 0

            async for msg in recompenses_channel.history(limit=1000, after=thirty_days_ago):
                messages_parcourus += 1

                # Compter les mentions reçues par chaque joueur (logique mentionsomeone)
                for mentioned in msg.mentions:
                    if mentioned.id in mentions_count:
                        mentions_count[mentioned.id] += 1

                # Compter les posts MJ : posts avec 2+ mentions uniques hors auteur (logique recapmj)
                if msg.author.id in posts_mj_count:
                    mentions_uniques = set(
                        u.id for u in msg.mentions if u.id != msg.author.id
                    )
                    if len(mentions_uniques) >= 2:
                        posts_mj_count[msg.author.id] += 1

            # --- Tri : joueurs oubliés d'abord, puis par mentions croissantes ---
            def sort_key(item):
                uid, mentions = item
                mj = posts_mj_count.get(uid, 0)
                # 0 = oublié en premier, 1 = actif après
                return (0 if (mentions == 0 and mj == 0) else 1, mentions, mj)

            sorted_users = sorted(mentions_count.items(), key=sort_key)

            # --- Construction de l'affichage ---
            lines_oublies = []
            lines_actifs = []

            for uid, mentions in sorted_users:
                user = auteurs.get(uid)
                if not user:
                    continue

                mj = posts_mj_count.get(uid, 0)

                if mentions == 0 and mj == 0:
                    lines_oublies.append(
                        f"⚠️ **{user.display_name}** - aucune récompense, aucune quête MJ"
                    )
                else:
                    parts = []
                    parts.append(f"{mentions} récompense{'s' if mentions != 1 else ''}")
                    if mj > 0:
                        parts.append(f"{mj} quête{'s' if mj != 1 else ''} MJ")
                    lines_actifs.append(
                        f"✅ **{user.display_name}** - {' | '.join(parts)}"
                    )

            # Assembler la description
            description_parts = []
            if lines_oublies:
                description_parts.append(
                    f"**__Joueurs sans activité (30j) :__**\n" + "\n".join(lines_oublies)
                )
            if lines_actifs:
                description_parts.append(
                    f"**__Joueurs avec activité :__**\n" + "\n".join(lines_actifs)
                )

            description = "\n\n".join(description_parts) if description_parts else "Aucun joueur trouvé."

            # Embed
            embed = discord.Embed(
                title=f"📊 Suivi joueurs - récompenses & quêtes MJ (30 jours)",
                description=description,
                color=0xff9900 if lines_oublies else 0x00b0f4
            )

            embed.add_field(
                name="Canal source",
                value=interaction.channel.mention,
                inline=True
            )
            embed.add_field(
                name="Canal analysé",
                value=recompenses_channel.mention,
                inline=True
            )

            joueurs_total = len(lines_oublies) + len(lines_actifs)
            embed.add_field(
                name="Joueurs",
                value=f"{joueurs_total} listés ({len(lines_oublies)} sans activité)",
                inline=True
            )

            footer_text = (
                f"{messages_parcourus} messages analysés"
                f" | Récompenses = mentions reçues | Quêtes MJ = posts avec 2+ mentions"
            )
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
