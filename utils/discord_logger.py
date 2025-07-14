"""
Système de logging Discord pour le Bot Faerûn.

Ce module permet d'envoyer les logs importantes dans un canal Discord
configuré (généralement bot-admin) en plus des logs système classiques.
"""

import discord
import logging
import traceback
import asyncio
from datetime import datetime, timezone
from typing import Optional, Union, Set
from utils.channels import ChannelHelper
from config import Config

logger = logging.getLogger(__name__)


class DiscordLogger:
    """Gestionnaire de logs Discord pour le bot."""

    def __init__(self, bot):
        self.bot = bot
        self._log_cache = []  # Cache pour les logs avant que le bot soit prêt
        self._bot_ready = False
        self._sending_logs = False  # Flag pour éviter les boucles
        self._sent_messages = set()  # Cache des messages déjà envoyés

    def set_ready(self):
        """Marque le bot comme prêt et vide le cache de logs."""
        self._bot_ready = True
        if self._log_cache:
            logger.info(f"Envoi de {len(self._log_cache)} logs en cache...")
            for log_entry in self._log_cache:
                self._send_log_async(log_entry)
            self._log_cache.clear()

    def _get_admin_channel(
            self, guild: discord.Guild) -> Optional[discord.TextChannel]:
        """Récupère le canal admin configuré."""
        if not guild:
            return None

        admin_channel = Config.get_channel(guild, 'admin')
        return admin_channel

    def _create_log_embed(self, level: str, message: str,
                          **kwargs) -> discord.Embed:
        """Crée un embed pour un log."""

        # Couleurs selon le niveau
        colors = {
            'DEBUG': 0x95a5a6,  # Gris
            'INFO': 0x3498db,  # Bleu
            'WARNING': 0xf39c12,  # Orange
            'ERROR': 0xe74c3c,  # Rouge
            'CRITICAL': 0x8e44ad  # Violet
        }

        # Emojis selon le niveau
        emojis = {
            'DEBUG': '🔍',
            'INFO': 'ℹ️',
            'WARNING': '⚠️',
            'ERROR': '❌',
            'CRITICAL': '🚨'
        }

        embed = discord.Embed(
            title=f"{emojis.get(level, '📝')} Log {level}",
            description=message[:2000],  # Limite Discord
            color=colors.get(level, 0x95a5a6),
            timestamp=datetime.now(timezone.utc))

        # Ajouter des champs supplémentaires si fournis
        if 'user' in kwargs:
            embed.add_field(name="👤 Utilisateur",
                            value=kwargs['user'],
                            inline=True)

        if 'guild' in kwargs:
            embed.add_field(name="🏰 Serveur",
                            value=kwargs['guild'],
                            inline=True)

        if 'command' in kwargs:
            embed.add_field(name="⚡ Commande",
                            value=kwargs['command'],
                            inline=True)

        if 'channel' in kwargs:
            embed.add_field(name="📍 Canal",
                            value=kwargs['channel'],
                            inline=True)

        if 'error' in kwargs:
            error_text = str(kwargs['error'])[:1000]  # Limiter la taille
            embed.add_field(name="🐛 Erreur",
                            value=f"```\n{error_text}\n```",
                            inline=False)

        if 'traceback' in kwargs:
            tb_text = kwargs['traceback'][:1000]  # Limiter la taille
            embed.add_field(name="📚 Traceback",
                            value=f"```python\n{tb_text}\n```",
                            inline=False)

        embed.set_footer(text=f"Bot Faerûn • {Config.ADMIN_ROLE_NAME}")
        return embed

    def _create_message_hash(self, log_entry: dict) -> str:
        """Crée un hash unique pour éviter les doublons."""
        import hashlib
        content = f"{log_entry.get('level')}-{log_entry.get('message')}-{log_entry.get('user', '')}"
        return hashlib.md5(content.encode()).hexdigest()[:8]

    def _send_log_async(self, log_entry: dict):
        """Envoie un log de manière asynchrone."""
        if self.bot.loop and not self.bot.loop.is_closed():
            # CORRECTION : Eviter les doublons avec un hash
            message_hash = self._create_message_hash(log_entry)
            if message_hash not in self._sent_messages:
                self._sent_messages.add(message_hash)
                # Nettoyer le cache périodiquement (garder seulement les 100 derniers)
                if len(self._sent_messages) > 100:
                    old_messages = list(self._sent_messages)[:50]
                    for old_hash in old_messages:
                        self._sent_messages.discard(old_hash)

                asyncio.create_task(self._send_log_to_discord(log_entry))

    async def _send_log_to_discord(self, log_entry: dict):
        """Envoie effectivement le log dans Discord."""
        try:
            if not self._bot_ready or self._sending_logs:
                return

            self._sending_logs = True  # Flag pour éviter les boucles

            # CORRECTION : Envoyer seulement dans le serveur principal ou configuré
            target_guild = None

            # Si Config.GUILD_ID est défini, utiliser ce serveur
            if Config.GUILD_ID:
                target_guild = self.bot.get_guild(Config.GUILD_ID)

            # Sinon, prendre le premier serveur qui a un canal admin
            if not target_guild:
                for guild in self.bot.guilds:
                    admin_channel = self._get_admin_channel(guild)
                    if admin_channel:
                        target_guild = guild
                        break

            # Envoyer seulement dans le serveur cible
            if target_guild:
                admin_channel = self._get_admin_channel(target_guild)
                if admin_channel:
                    try:
                        embed = self._create_log_embed(**log_entry)
                        await admin_channel.send(embed=embed)
                    except discord.Forbidden:
                        logger.warning(
                            f"Pas de permission pour envoyer dans {admin_channel.name}"
                        )
                    except discord.HTTPException as e:
                        logger.warning(f"Erreur HTTP envoi log: {e}")
                    except Exception as e:
                        logger.error(f"Erreur inattendue envoi log: {e}")

        except Exception as e:
            logger.error(f"Erreur critique dans _send_log_to_discord: {e}")
        finally:
            self._sending_logs = False  # Libérer le flag

    def log(self, level: str, message: str, **kwargs):
        """
        Envoie un log dans Discord.

        Args:
            level: Niveau du log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            message: Message principal
            **kwargs: Champs supplémentaires (user, guild, command, channel, error, traceback)
        """
        # CORRECTION : Filtrer certains logs pour éviter le spam
        if self._sending_logs:
            return  # Eviter les boucles

        log_entry = {'level': level.upper(), 'message': message, **kwargs}

        if self._bot_ready:
            self._send_log_async(log_entry)
        else:
            # Mettre en cache si le bot n'est pas encore prêt
            self._log_cache.append(log_entry)

    def info(self, message: str, **kwargs):
        """Log de niveau INFO."""
        self.log('INFO', message, **kwargs)

    def warning(self, message: str, **kwargs):
        """Log de niveau WARNING."""
        self.log('WARNING', message, **kwargs)

    def error(self, message: str, **kwargs):
        """Log de niveau ERROR."""
        self.log('ERROR', message, **kwargs)

    def critical(self, message: str, **kwargs):
        """Log de niveau CRITICAL."""
        self.log('CRITICAL', message, **kwargs)

    def command_used(self,
                     interaction: discord.Interaction,
                     command_name: str,
                     success: bool = True):
        """Log l'utilisation d'une commande - FILTRE pour éviter le spam."""
        # CORRECTION : Logger seulement les commandes importantes
        important_commands = [
            'config-channels', 'test-logs', 'sync_bot', 'reload_commands',
            'debug_bot'
        ]

        if command_name not in important_commands:
            return  # Ne pas logger les commandes normales

        level = 'INFO' if success else 'WARNING'
        status = '✅' if success else '❌'

        message = f"{status} Commande admin utilisée: `/{command_name}`"

        self.log(
            level,
            message,
            user=f"{interaction.user.display_name} ({interaction.user.id})",
            guild=f"{interaction.guild.name} ({interaction.guild.id})"
            if interaction.guild else "DM",
            command=f"/{command_name}",
            channel=f"#{interaction.channel.name}" if hasattr(
                interaction.channel, 'name') else str(interaction.channel))

    def bot_event(self,
                  event_name: str,
                  message: str,
                  level: str = 'INFO',
                  **kwargs):
        """Log un événement du bot."""
        self.log(level, f"🤖 {event_name}: {message}", **kwargs)

    def error_with_traceback(self, message: str, error: Exception, **kwargs):
        """Log une erreur avec traceback complet."""
        tb = traceback.format_exc()
        self.log('ERROR', message, error=str(error), traceback=tb, **kwargs)

    def admin_action(self,
                     action: str,
                     user: discord.Member,
                     details: str = "",
                     **kwargs):
        """Log une action d'administration."""
        message = f"🔧 Action admin: {action}"
        if details:
            message += f" - {details}"

        self.log('INFO',
                 message,
                 user=f"{user.display_name} ({user.id})",
                 guild=f"{user.guild.name} ({user.guild.id})",
                 **kwargs)

    async def test_logging(self, guild: discord.Guild) -> dict:
        """Teste le système de logging pour un serveur."""
        admin_channel = self._get_admin_channel(guild)

        result = {
            'channel_found': admin_channel is not None,
            'channel_name': admin_channel.name if admin_channel else None,
            'can_send': False,
            'test_sent': False
        }

        if admin_channel:
            try:
                # Tester les permissions
                permissions = admin_channel.permissions_for(guild.me)
                result[
                    'can_send'] = permissions.send_messages and permissions.embed_links

                if result['can_send']:
                    # Envoyer un message de test
                    embed = discord.Embed(
                        title="🧪 Test du Système de Logs",
                        description=
                        "Ce message confirme que le système de logs fonctionne correctement.",
                        color=0x00ff00,
                        timestamp=datetime.now(timezone.utc))
                    embed.add_field(name="📍 Canal",
                                    value=admin_channel.mention,
                                    inline=True)
                    embed.add_field(name="🏰 Serveur",
                                    value=guild.name,
                                    inline=True)
                    embed.add_field(name="✅ Statut",
                                    value="Logs opérationnels",
                                    inline=True)
                    embed.add_field(name="🔧 Anti-doublons",
                                    value="Activé",
                                    inline=True)
                    embed.set_footer(
                        text="Test effectué par le système de logs Discord")

                    await admin_channel.send(embed=embed)
                    result['test_sent'] = True

            except discord.Forbidden:
                result['can_send'] = False
            except Exception as e:
                logger.error(f"Erreur test logging: {e}")
                result['error'] = str(e)

        return result

    def clear_cache(self):
        """Nettoie le cache de messages pour libérer la mémoire."""
        self._sent_messages.clear()
        logger.info("Cache de logs nettoyé")


# Instance globale (sera initialisée dans le bot principal)
discord_logger: Optional[DiscordLogger] = None


def init_discord_logger(bot):
    """Initialise le logger Discord."""
    global discord_logger
    discord_logger = DiscordLogger(bot)
    logger.info("Discord Logger initialisé avec protection anti-doublons")
    return discord_logger


def get_discord_logger() -> Optional[DiscordLogger]:
    """Récupère l'instance du logger Discord."""
    return discord_logger
