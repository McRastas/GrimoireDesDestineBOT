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
            str: Message d'erreur formaté avec conseils de configuration
        """
        config = Config.get_channel_config(channel_key)

        if config.get('name') or config.get('id'):
            # Canal configuré mais introuvable
            if config.get('id'):
                return (
                    f"❌ Le canal '{channel_key}' configuré avec l'ID `{config['id']}` est introuvable.\n"
                    f"💡 Vérifiez que le canal existe et que le bot y a accès.\n"
                    f"🔧 Utilisez `/config-channels` pour voir la configuration."
                )
            else:
                return (
                    f"❌ Le canal '{channel_key}' configuré (#{config['name']}) est introuvable.\n"
                    f"💡 Vérifiez que le canal #{config['name']} existe sur ce serveur.\n"
                    f"🔧 Utilisez `/config-channels` pour voir la configuration."
                )
        else:
            # Canal pas configuré du tout
            suggestions = ChannelHelper._get_channel_suggestions(channel_key)
            return (
                f"❌ Le canal '{channel_key}' n'est pas configuré.\n"
                f"💡 {suggestions}\n"
                f"🔧 Utilisez `/config-channels` pour voir comment configurer les canaux."
            )

    @staticmethod
    def _get_channel_suggestions(channel_key: str) -> str:
        """Génère des suggestions de configuration pour un canal."""
        default_names = {
            ChannelHelper.RECOMPENSES: "recompenses",
            ChannelHelper.QUETES: "départ-à-l-aventure",
            ChannelHelper.LOGS: "bot-logs",
            ChannelHelper.ADMIN: "bot-admin"
        }

        default_name = default_names.get(channel_key, channel_key)

        return (f"Configurez la variable d'environnement :\n"
                f"`CHANNEL_{channel_key.upper()}_NAME={default_name}` ou\n"
                f"`CHANNEL_{channel_key.upper()}_ID=123456789`")

    @staticmethod
    def log_channel_access(guild: discord.Guild, channel_key: str,
                           success: bool):
        """Log les accès aux canaux pour le debugging."""
        if success:
            logger.debug(f"Canal '{channel_key}' trouvé dans {guild.name}")
        else:
            config = Config.get_channel_config(channel_key)
            logger.warning(
                f"Canal '{channel_key}' introuvable dans {guild.name}. Config: {config}"
            )

    @staticmethod
    def test_all_channels(guild: discord.Guild) -> dict:
        """
        Teste tous les canaux configurés et retourne un rapport de statut.

        Returns:
            dict: Rapport avec le statut de chaque canal
        """
        rapport = {
            'total': 0,
            'fonctionnels': 0,
            'manquants': 0,
            'details': {}
        }

        all_channels = ChannelHelper.get_all_configured_channels(guild)
        rapport['total'] = len(all_channels)

        for channel_key, info in all_channels.items():
            if info['found']:
                rapport['fonctionnels'] += 1
                rapport['details'][channel_key] = {
                    'status': 'OK',
                    'channel': info['channel'].mention,
                    'name': info['channel'].name,
                    'id': info['channel'].id
                }
            else:
                rapport['manquants'] += 1
                rapport['details'][channel_key] = {
                    'status': 'MANQUANT',
                    'config': info['config'],
                    'error':
                    ChannelHelper.get_channel_error_message(channel_key)
                }

        return rapport

    @staticmethod
    def format_channel_list(guild: discord.Guild,
                            include_ids: bool = False) -> str:
        """
        Formate une liste des canaux du serveur pour affichage.

        Args:
            guild: Le serveur Discord
            include_ids: Si True, inclut les IDs des canaux

        Returns:
            str: Liste formatée des canaux
        """
        channels = sorted(guild.text_channels, key=lambda c: c.name)

        if include_ids:
            return "\n".join(
                [f"#{c.name} (ID: `{c.id}`)" for c in channels[:20]])
        else:
            return "\n".join([f"#{c.name}" for c in channels[:20]])

    @staticmethod
    def suggest_channel_config(guild: discord.Guild) -> str:
        """
        Suggère une configuration complète basée sur les canaux existants du serveur.

        Returns:
            str: Configuration JSON suggérée
        """
        suggestions = {}

        # Rechercher des canaux qui correspondent aux noms par défaut
        channel_mappings = {
            'recompenses': ['recompenses', 'récompenses', 'rewards'],
            'quetes': [
                'départ-à-l-aventure', 'depart-aventure', 'quetes', 'quêtes',
                'aventure'
            ],
            'logs': ['logs', 'bot-logs', 'log'],
            'admin': ['bot-admin', 'admin', 'moderation']
        }

        for channel_key, possible_names in channel_mappings.items():
            for channel in guild.text_channels:
                if any(name.lower() in channel.name.lower()
                       for name in possible_names):
                    suggestions[channel_key] = {
                        'name': channel.name,
                        'id': channel.id
                    }
                    break

        if suggestions:
            import json
            return f"Configuration suggérée :\n```json\n{json.dumps(suggestions, indent=2, ensure_ascii=False)}\n```"
        else:
            return "Aucune suggestion automatique possible. Configurez manuellement les canaux."
