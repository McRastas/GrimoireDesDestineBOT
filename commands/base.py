"""Classe de base pour toutes les commandes."""

import discord
from discord import app_commands
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


class BaseCommand(ABC):
    """Classe de base pour toutes les commandes slash."""

    def __init__(self, bot):
        self.bot = bot

    @property
    @abstractmethod
    def name(self) -> str:
        """Nom de la commande."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Description de la commande."""
        pass

    @abstractmethod
    async def callback(self, interaction: discord.Interaction, *args,
                       **kwargs):
        """Fonction appelée lors de l'exécution de la commande."""
        pass

    def register(self, tree: app_commands.CommandTree):
        """Enregistre la commande dans l'arbre des commandes."""
        try:
            command = app_commands.Command(name=self.name,
                                           description=self.description,
                                           callback=self.callback)
            tree.add_command(command)
        except Exception as e:
            logger.error(f"Erreur enregistrement '{self.name}': {e}")
