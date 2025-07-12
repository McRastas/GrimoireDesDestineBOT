"""Commande de test simple."""

import discord
from .base import BaseCommand


class TestCommand(BaseCommand):

    @property
    def name(self) -> str:
        return "test"

    @property
    def description(self) -> str:
        return "Commande de test simple"

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message("✅ Le bot fonctionne !",
                                                ephemeral=True)
