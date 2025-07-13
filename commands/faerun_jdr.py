"""
Commande Discord : /faerunjdr <date_str>

DESCRIPTION:
    Convertit une date grégorienne spécifique en date Faerûnienne

FONCTIONNEMENT:
    - Prend en paramètre une date au format JJ-MM-AAAA
    - Parse la chaîne avec datetime.strptime()
    - Convertit cette date en équivalent Faerûnien
    - Gestion d'erreur si le format est incorrect

UTILISATION:
    /faerunjdr date_str:15-02-2023
"""

import discord
from discord import app_commands
from datetime import datetime
from .base import BaseCommand
from calendar_faerun import FaerunDate


class FaerunJdrCommand(BaseCommand):

    @property
    def name(self) -> str:
        return "faerunjdr"

    @property
    def description(self) -> str:
        return "Convertit une date (JJ-MM-AAAA) en date Faerûnienne"

    def register(self, tree: app_commands.CommandTree):
        """Enregistrement spécial pour cette commande avec paramètre."""

        @tree.command(name=self.name, description=self.description)
        @app_commands.describe(date_str="Date au format JJ-MM-AAAA")
        async def faerunjdr_command(interaction: discord.Interaction,
                                    date_str: str):
            await self.callback(interaction, date_str)

    async def callback(self, interaction: discord.Interaction, date_str: str):
        try:
            target_date = datetime.strptime(date_str, "%d-%m-%Y")
        except ValueError:
            await interaction.response.send_message(
                "❌ Format de date invalide. Utilisez JJ-MM-AAAA (ex: 15-02-2023)",
                ephemeral=True)
            return

        fae = FaerunDate(target_date)
        embed = discord.Embed(title="📅 Conversion de date Faerûnienne",
                              description=fae.to_locale_string(),
                              color=0x8B4513)
        await interaction.response.send_message(embed=embed, ephemeral=True)
