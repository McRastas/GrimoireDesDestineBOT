"""
Commande Discord : /mentionsomeone [membre]

DESCRIPTION:
    Compte et liste les mentions d'un utilisateur dans le canal récompenses sur 30 jours

FONCTIONNEMENT:
    - Paramètre optionnel : si aucun membre spécifié, utilise l'auteur de la commande
    - Recherche le canal récompenses configuré dans la guilde
    - Parcourt l'historique des 30 derniers jours (max 1000 messages)
    - Liste tous les messages où l'utilisateur cible est mentionné
    - Affiche avec liens cliquables vers les messages originaux

UTILISATION:
    /mentionsomeone
    /mentionsomeone membre:@JoueurX
"""

import discord
from discord import app_commands
from datetime import datetime, timezone, timedelta
import logging
from .base import BaseCommand
from utils.channels import ChannelHelper

logger = logging.getLogger(__name__)


class MentionSomeoneCommand(BaseCommand):

    @property
    def name(self) -> str:
        return "mentionsomeone"

    @property
    def description(self) -> str:
        return "Compte et liste les mentions dans le canal récompenses sur 30j"

    def register(self, tree: app_commands.CommandTree):
        """Enregistrement spécial pour cette commande avec paramètre optionnel."""

        @tree.command(name=self.name, description=self.description)
        @app_commands.describe(membre="Le membre dont on veut les mentions")
        async def mentions_command(interaction: discord.Interaction,
                                   membre: discord.Member = None):
            await interaction.response.defer(ephemeral=True)
            await self.callback(interaction, membre)

    async def callback(self,
                       interaction: discord.Interaction,
                       membre: discord.Member = None):
        cible = membre or interaction.user
        channel = ChannelHelper.get_recompenses_channel(interaction.guild)

        if not channel:
            error_msg = ChannelHelper.get_channel_error_message(
                ChannelHelper.RECOMPENSES)
            await interaction.followup.send(error_msg)
            return

        now = datetime.now(timezone.utc)
        thirty_days_ago = now - timedelta(days=30)

        # Collecter tous les messages avec mentions
        mentions_trouvees = []
        messages_parcourus = 0

        async for message in channel.history(limit=1000,
                                             after=thirty_days_ago):
            messages_parcourus += 1
            if cible in message.mentions:
                # Créer le lien vers le message
                message_url = f"https://discord.com/channels/{interaction.guild.id}/{channel.id}/{message.id}"

                # Prendre la première ligne du message pour l'aperçu
                premiere_ligne = message.content.split('\n', 1)[0].strip()
                if not premiere_ligne:
                    premiere_ligne = "*[Message vide ou embed]*"

                # Tronquer si trop long
                apercu = premiere_ligne[:60] + ('...' if len(premiere_ligne)
                                                > 60 else '')

                # Ajouter info sur la date relative
                delta = now - message.created_at
                if delta.days == 0:
                    when = "Aujourd'hui"
                elif delta.days == 1:
                    when = "Hier"
                elif delta.days <= 7:
                    when = f"Il y a {delta.days} jours"
                else:
                    when = f"Il y a {delta.days} jours"

                mentions_trouvees.append({
                    'apercu': apercu,
                    'url': message_url,
                    'when': when,
                    'author': message.author.display_name,
                    'date': message.created_at
                })

        # Trier par date (plus récent en premier)
        mentions_trouvees.sort(key=lambda x: x['date'], reverse=True)

        # Construire l'embed
        embed = discord.Embed(
            title=f"📢 Mentions de {cible.display_name}",
            description=
            f"**{len(mentions_trouvees)} mentions** trouvées sur 30 jours dans {channel.mention}",
            color=0x7289DA)

        if mentions_trouvees:
            # Afficher jusqu'à 8 mentions récentes (pour éviter dépassement)
            desc_mentions = []
            char_count = 0
            max_chars = 900  # Limite de sécurité pour éviter les erreurs Discord

            for mention in mentions_trouvees[:10]:  # Max 10 pour avoir du choix
                # Raccourcir pour économiser l'espace
                apercu_court = mention['apercu'][:50] + ('...' if len(
                    mention['apercu']) > 50 else '')

                line = (f"• **{mention['when']}** par {mention['author']}\n"
                        f"  └─ [{apercu_court}]({mention['url']})")

                # Vérifier si on peut ajouter cette ligne
                if char_count + len(line) + 2 > max_chars:  # +2 pour \n\n
                    break

                desc_mentions.append(line)
                char_count += len(line) + 2

            embed.add_field(
                name=f"📋 Mentions récentes ({len(desc_mentions)} affichées)",
                value="\n\n".join(desc_mentions),
                inline=False)

            # Statistiques générales
            if len(mentions_trouvees) > len(desc_mentions):
                remaining = len(mentions_trouvees) - len(desc_mentions)
                embed.add_field(
                    name="📊 Informations supplémentaires",
                    value=f"**Non affichées :** {remaining} mentions supplémentaires",
                    inline=False)

        else:
            embed.add_field(
                name="❌ Aucune mention trouvée",
                value=
                f"Aucune mention de {cible.display_name} dans {channel.mention} sur 30 jours",
                inline=False)

        # Footer avec infos de recherche
        embed.set_footer(
            text=f"Analysé {messages_parcourus} messages sur 30 jours")

        await interaction.followup.send(embed=embed)