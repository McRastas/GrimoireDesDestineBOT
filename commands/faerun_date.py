"""
Commande Discord : /faerun

DESCRIPTION:
    Affiche la date Faerûnienne actuelle au format complet

FONCTIONNEMENT:
    - Récupère la date/heure actuelle système (UTC)
    - Convertit en date Faerûnienne via la classe FaerunDate
    - Affiche dans un embed Discord avec formatage localisé
    - Réponse éphémère (visible uniquement par l'utilisateur)

UTILISATION:
    /faerun
"""

import discord
from datetime import datetime, timezone
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