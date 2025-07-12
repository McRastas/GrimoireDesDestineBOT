"""Commandes liées au calendrier Faerûn."""

import discord
from discord import app_commands
from datetime import datetime, timezone, timedelta
from .base import BaseCommand
from calendar_faerun import FaerunDate


class FaerunCommand(BaseCommand):

    @property
    def name(self) -> str:
        return "faerun"

    @property
    def description(self) -> str:
        return "Affiche la date Faerûnienne complète"

    async def callback(self, interaction: discord.Interaction):
        fae = FaerunDate(datetime.now(timezone.utc))
        embed = discord.Embed(title="📅 Date de Faerûn",
                              description=fae.to_locale_string(),
                              color=0x8B4513)
        embed.set_footer(text="Calendrier de Harptos")
        await interaction.response.send_message(embed=embed, ephemeral=True)


class FaerunFestivalCommand(BaseCommand):

    @property
    def name(self) -> str:
        return "faerunfestival"

    @property
    def description(self) -> str:
        return "Affiche le prochain festival"

    async def callback(self, interaction: discord.Interaction):
        now = datetime.now()
        for jours_test in range(366):
            test_date = now + timedelta(days=jours_test)
            fae = FaerunDate.from_datetime(test_date)
            festival = fae.get_festival()
            if festival:
                embed = discord.Embed(
                    title="🎊 Prochain festival de Faerûn",
                    description=
                    f"**{festival}**, le {test_date.day} {fae.get_month()} {fae.get_dr_year()} DR ({test_date.strftime('%d/%m/%Y')})",
                    color=0xFFD700)
                await interaction.response.send_message(embed=embed,
                                                        ephemeral=True)
                return

        await interaction.response.send_message(
            "Aucun festival trouvé cette année (bizarre).", ephemeral=True)


class FaerunCompletCommand(BaseCommand):

    @property
    def name(self) -> str:
        return "faeruncomplet"

    @property
    def description(self) -> str:
        return "Affiche toutes les infos de date Faerûnienne"

    async def callback(self, interaction: discord.Interaction):
        fae = FaerunDate(datetime.now(timezone.utc))
        embed = discord.Embed(title="📅 Infos complètes de Faerûn",
                              color=0x8B4513)
        embed.add_field(name="📅 Date",
                        value=fae.to_locale_string(),
                        inline=True)
        embed.add_field(name="🗓️ Année",
                        value=f"{fae.get_dr_year()} DR",
                        inline=True)
        embed.add_field(name="🌍 Saison", value=fae.get_season(), inline=True)
        embed.add_field(name="📊 Semaine",
                        value=f"Semaine {fae.get_week_of_year()}",
                        inline=True)
        embed.set_footer(text="Calendrier de Harptos • Forgotten Realms")

        await interaction.response.send_message(embed=embed, ephemeral=True)


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
