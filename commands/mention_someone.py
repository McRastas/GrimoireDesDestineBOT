"""
Commande Discord : /mentionsomeone [membre]

DESCRIPTION:
    Compte le nombre de mentions d'un utilisateur dans le canal #recompenses sur 30 jours

FONCTIONNEMENT:
    - Paramètre optionnel : si aucun membre spécifié, utilise l'auteur de la commande
    - Recherche le canal #recompenses dans la guilde
    - Parcourt l'historique des 30 derniers jours (max 1000 messages)
    - Compte les messages où l'utilisateur cible est mentionné
    - Affiche le résultat dans un embed

UTILISATION:
    /mentionsomeone
    /mentionsomeone membre:@JoueurX
"""

import discord
from discord import app_commands
from datetime import datetime, timezone, timedelta
import logging
from .base import BaseCommand

logger = logging.getLogger(__name__)


class MentionSomeoneCommand(BaseCommand):

    @property
    def name(self) -> str:
        return "mentionsomeone"

    @property
    def description(self) -> str:
        return "Compte les mentions dans #recompenses sur 30j"

    def register(self, tree: app_commands.CommandTree):
        """Enregistrement spécial pour cette commande avec paramètre optionnel."""

        @tree.command(name=self.name, description=self.description)
        @app_commands.describe(
            membre="Le membre dont on veut le nombre de mentions")
        async def mentions_command(interaction: discord.Interaction,
                                   membre: discord.Member = None):
            await self.callback(interaction, membre)

    async def callback(self,
                       interaction: discord.Interaction,
                       membre: discord.Member = None):
        cible = membre or interaction.user
        channel = discord.utils.get(interaction.guild.text_channels,
                                    name='recompenses')

        if not channel:
            await interaction.response.send_message(
                "❌ Le canal #recompenses est introuvable.", ephemeral=True)
            return

        count = 0
        now = datetime.now(timezone.utc)
        thirty_days_ago = now - timedelta(days=30)

        async for message in channel.history(limit=1000,
                                             after=thirty_days_ago):
            if cible in message.mentions:
                count += 1

        embed = discord.Embed(
            title="📢 Statistiques de mentions",
            description=
            f"**{cible.display_name}** a été mentionné **{count} fois** dans #recompenses sur 30 jours.",
            color=0x7289DA)
        await interaction.response.send_message(embed=embed, ephemeral=True)
