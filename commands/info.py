"""Commande d'informations sur le bot."""

import discord
from .base import BaseCommand


class InfoCommand(BaseCommand):

    @property
    def name(self) -> str:
        return "info"

    @property
    def description(self) -> str:
        return "Informations sur le bot"

    async def callback(self, interaction: discord.Interaction):
        embed = discord.Embed(title="🤖 Informations du Bot",
                              description="Bot Faerûn - Calendrier D&D",
                              color=0x00ff00)
        embed.add_field(name="Guildes",
                        value=len(self.bot.guilds),
                        inline=True)
        embed.add_field(name="Utilisateurs",
                        value=len(self.bot.users),
                        inline=True)
        embed.add_field(name="Commandes",
                        value=len(self.bot.tree.get_commands()),
                        inline=True)

        await interaction.response.send_message(embed=embed, ephemeral=True)
