"""
Commande Discord : /recapmj [membre]

DESCRIPTION:
    Compte les messages dans #recompenses où un MJ mentionne au moins 2 personnes différentes

FONCTIONNEMENT:
    - Paramètre optionnel : membre à analyser (par défaut l'auteur de la commande)
    - Parcourt #recompenses sur 30 jours pour les messages de ce membre
    - Pour chaque message, compte les mentions uniques (excluant l'auteur)
    - Ne retient que les messages avec 2+ mentions différentes
    - Affiche le total de ces "messages de récompense multi-joueurs"

UTILISATION:
    /recapmj
    /recapmj membre:@MaitreJeu
"""

import discord
from discord import app_commands
from datetime import datetime, timezone, timedelta
from .base import BaseCommand


class RecapMjCommand(BaseCommand):

    @property
    def name(self) -> str:
        return "recapmj"

    @property
    def description(self) -> str:
        return "Compte le nombre de messages dans #recompenses sur 30j où le MJ mentionne au moins 2 personnes"

    def register(self, tree: app_commands.CommandTree):
        """Enregistrement spécial pour cette commande avec paramètre optionnel."""

        @tree.command(name=self.name, description=self.description)
        @app_commands.describe(
            membre="Le membre dont on veut la stat (par défaut toi)")
        async def recap_mj_command(interaction: discord.Interaction,
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

        now = datetime.now(timezone.utc)
        thirty_days_ago = now - timedelta(days=30)
        nb_messages = 0
        total_mentions = 0

        async for message in channel.history(limit=1000,
                                             after=thirty_days_ago):
            if message.author.id == cible.id:
                mentions_uniques = set(user.id for user in message.mentions
                                       if user.id != cible.id)
                if len(mentions_uniques) >= 2:
                    nb_messages += 1
                    total_mentions += len(mentions_uniques)

        embed = discord.Embed(
            title="📋 Messages multi-mentions dans #recompenses",
            description=
            (f"**{cible.display_name}** a posté **{nb_messages} poste de récompense** "
             f"dans #recompenses (sur 30j) où il/elle mentionne au moins deux personnes différentes."
             ),
            color=0x7289DA)
        await interaction.response.send_message(embed=embed, ephemeral=True)