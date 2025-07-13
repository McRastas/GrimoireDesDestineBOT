"""
Commande Discord : /faerunfestival

DESCRIPTION:
    Trouve et affiche le prochain festival du calendrier Faerûnien

FONCTIONNEMENT:
    - Itère sur les 366 prochains jours à partir d'aujourd'hui
    - Pour chaque jour, vérifie s'il y a un festival via FaerunDate.get_festival()
    - Dès qu'un festival est trouvé, l'affiche avec la date DR et grégorienne
    - S'arrête au premier festival trouvé (le plus proche)

UTILISATION:
    /faerunfestival
"""

import discord
from datetime import datetime, timedelta
from .base import BaseCommand
from calendar_faerun import FaerunDate


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
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return

        await interaction.response.send_message(
            "Aucun festival trouvé cette année (bizarre).", ephemeral=True)