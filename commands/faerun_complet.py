"""
Commande Discord : /faeruncomplet

DESCRIPTION:
    Affiche toutes les informations détaillées sur la date Faerûnienne actuelle

FONCTIONNEMENT:
    - Récupère la date actuelle et la convertit en Faerûnien
    - Extrait plusieurs informations : date complète, année DR, saison, semaine
    - Présente tout dans un embed structuré avec des champs séparés
    - Plus détaillé que la commande /faerun basique

UTILISATION:
    /faeruncomplet
"""

import discord
from datetime import datetime, timezone
from .base import BaseCommand
from calendar_faerun import FaerunDate


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