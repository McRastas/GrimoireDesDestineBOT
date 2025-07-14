"""
Helper générique pour la gestion des canaux configurés du bot.

Ce module centralise la logique d'accès aux canaux Discord configurés
via les variables d'environnement, avec fallback intelligent entre ID et nom.
"""

import discord
from config import Config
import logging

logger = logging.getLogger(__name__)


class ChannelHelper:
    """Helper générique pour la gestion des canaux configurés."""

    # Constantes pour les types de canaux
    RECOMPENSES = 'recompenses'
    QUETES = 'quetes'
    LOGS = 'logs'
    ADMIN = 'admin'

    @staticmethod
    def get_channel(guild: discord.Guild,
                    channel_key: str) -> discord.TextChannel:
        """
        Récupère un canal configuré de manière générique.

        Args:
            guild: Le serveur Discord
            channel_key: Clé du canal ('recompenses', 'quetes', etc.)

        Returns:
            discord.TextChannel: Le canal trouvé ou None
        """
        channel = Config.get_channel(guild, channel_key)
        if not channel:
            config = Config.get_channel_config(channel_key)
            channel_name = config.get('name', channel_key)
            logger.warning(
                f"Canal '{channel_key}' ({channel_name}) introuvable dans {guild.name}"
            )
        return channel

    @staticmethod
    def get_recompenses_channel(guild: discord.Guild) -> discord.TextChannel:
        """Récupère le canal récompenses."""
        return ChannelHelper.get_channel(guild, ChannelHelper.RECOMPENSES)

    @staticmethod
    def get_quetes_channel(guild: discord.Guild) -> discord.TextChannel:
        """Récupère le canal quêtes."""
        return ChannelHelper.get_channel(guild, ChannelHelper.QUETES)

    @staticmethod
    def get_logs_channel(guild: discord.Guild) -> discord.TextChannel:
        """Récupère le canal logs."""
        return ChannelHelper.get_channel(guild, ChannelHelper.LOGS)

    @staticmethod
    def get_admin_channel(guild: discord.Guild) -> discord.TextChannel:
        """Récupère le canal admin."""
        return ChannelHelper.get_channel(guild, ChannelHelper.ADMIN)

    @staticmethod
    def get_all_configured_channels(guild: discord.Guild) -> dict:
        """
        Récupère tous les canaux configurés avec leur statut.

        Returns:
            dict: {channel_key: {'config': dict, 'channel': discord.TextChannel, 'found': bool}}
        """
        result = {}

        for channel_key in Config.CHANNELS_CONFIG.keys():
            config = Config.get_channel_config(channel_key)
            channel = ChannelHelper.get_channel(guild, channel_key)

            result[channel_key] = {
                'config': config,
                'channel': channel,
                'found': channel is not None
            }

        return result

    @staticmethod
    def get_channel_error_message(channel_key: str) -> str:
        """
        Génère un message d'erreur informatif pour un canal manquant.

        Args:
            channel_key: Clé du canal manquant

        Returns:
            str: Message d'erreur formaté
        """
        config = Config.get_channel_config(channel_key)
        if config.get('name'):
            return f"❌ Le canal '{channel_key}' configuré (#{config['name']}) est introuvable."
        else:
            return f"❌ Le canal '{channel_key}' n'est pas configuré."
