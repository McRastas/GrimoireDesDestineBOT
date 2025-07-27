"""
Système de logging Discord pour le Bot Faerûn.

Ce module permet d'envoyer les logs importantes dans un canal Discord
configuré (généralement bot-admin) en plus des logs système classiques.

VERSION CORRIGÉE - Résout les problèmes de boucles infinies et améliore la gestion d'erreurs.
"""

import discord
import logging
import traceback
import asyncio
from datetime import datetime, timezone
from typing import Optional, Set
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
        
        # NOUVEAU : Gestion d'erreurs avancée
        self._error_count = 0  # Compteur d'erreurs pour éviter le spam
        self._max_errors = 5  # Nombre max d'erreurs avant arrêt temporaire
        self._last_error_time = None
        self._cooldown_duration = 300  # 5 minutes de cooldown après trop d'erreurs

    def set_ready(self):
        """Marque le bot comme prêt et vide le cache de logs."""
        self._bot_ready = True
        if self._log_cache:
            logger.info(f"Envoi de {len(self._log_cache)} logs en cache...")
            for log_entry in self._log_cache:
                self._send_log_async(log_entry)
            self._log_cache.clear()

    def _is_in_cooldown(self) -> bool:
        """NOUVEAU : Vérifie si on est en période de cooldown après trop d'erreurs."""
        if self._error_count < self._max_errors:
            return False
        
        if self._last_error_time is None:
            return False
        
        time_since_error = (datetime.now(timezone.utc) - self._last_error_time).total_seconds()
        if time_since_error > self._cooldown_duration:
            # Reset du compteur après cooldown
            self._error_count = 0
            self._last_error_time = None
            return False
        
        return True

    def _increment_error_count(self):
        """NOUVEAU : Incrémente le compteur d'erreurs et gère le cooldown."""
        self._error_count += 1
        self._last_error_time = datetime.now(timezone.utc)
        
        if self._error_count >= self._max_errors:
            logger.warning(
                f"Discord Logger en cooldown après {self._error_count} erreurs. "
                f"Reprise dans {self._cooldown_duration} secondes."
            )

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

        # CORRECTION : Limiter la taille du message principal pour éviter les erreurs Discord
        safe_message = str(message)[:1500] if message else "Message vide"

        embed = discord.Embed(
            title=f"{emojis.get(level, '📝')} Log {level}",
            description=safe_message,
            color=colors.get(level, 0x95a5a6),
            timestamp=datetime.now(timezone.utc))

        # Ajouter des champs supplémentaires si fournis (avec protection de taille)
        if 'user' in kwargs and kwargs['user']:
            user_info = str(kwargs['user'])[:100]
            embed.add_field(name="👤 Utilisateur",
                            value=user_info,
                            inline=True)

        if 'guild' in kwargs and kwargs['guild']:
            guild_info = str(kwargs['guild'])[:100]
            embed.add_field(name="🏰 Serveur",
                            value=guild_info,
                            inline=True)

        if 'command' in kwargs and kwargs['command']:
            command_info = str(kwargs['command'])[:50]
            embed.add_field(name="⚡ Commande",
                            value=command_info,
                            inline=True)

        if 'channel' in kwargs and kwargs['channel']:
            channel_info = str(kwargs['channel'])[:50]
            embed.add_field(name="📍 Canal",
                            value=channel_info,
                            inline=True)

        if 'error' in kwargs and kwargs['error']:
            error_text = str(kwargs['error'])[:800]  # Limiter la taille
            embed.add_field(name="🐛 Erreur",
                            value=f"```\n{error_text}\n```",
                            inline=False)

        if 'traceback' in kwargs and kwargs['traceback']:
            tb_text = str(kwargs['traceback'])[:800]  # Limiter la taille
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
        if self.bot.loop and not self.bot.loop.is_closed() and not self._is_in_cooldown():
            # Éviter les doublons avec un hash
            message_hash = self._create_message_hash(log_entry)
            if message_hash not in self._sent_messages:
                self._sent_messages.add(message_hash)
                # CORRECTION : Nettoyer le cache périodiquement (garder seulement les 50 derniers)
                if len(self._sent_messages) > 50:
                    old_messages = list(self._sent_messages)[:25]
                    for old_hash in old_messages:
                        self._sent_messages.discard(old_hash)

                asyncio.create_task(self._send_log_to_discord(log_entry))

    async def _send_log_to_discord(self, log_entry: dict):
        """Envoie effectivement le log dans Discord."""
        # CORRECTION : Vérifications multiples pour éviter les boucles
        if not self._bot_ready or self._sending_logs or self._is_in_cooldown():
            return

        self._sending_logs = True  # Flag pour éviter les boucles

        try:
            # CORRECTION : Envoyer seulement dans le serveur principal ou configuré
            target_guild = None

            # Si Config.GUILD_ID est défini, utiliser ce serveur
            if Config.GUILD_ID:
                target_guild = self.bot.get_guild(Config.GUILD_ID)

            # Sinon, prendre le premier serveur qui a un canal admin (limité à 3 max)
            if not target_guild:
                for guild in self.bot.guilds[:3]:  # CORRECTION : Limiter à 3 serveurs max
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
                        # NOUVEAU : Reset du compteur d'erreurs si succès
                        if self._error_count > 0:
                            self._error_count = max(0, self._error_count - 1)
                    except discord.Forbidden:
                        logger.warning(
                            f"Pas de permission pour envoyer dans {admin_channel.name}"
                        )
                        self._increment_error_count()
                    except discord.HTTPException as e:
                        logger.warning(f"Erreur HTTP envoi log: {e}")
                        self._increment_error_count()
                    except Exception as e:
                        logger.error(f"Erreur inattendue envoi log: {e}")
                        self._increment_error_count()

        except Exception as e:
            logger.error(f"Erreur critique dans _send_log_to_discord: {e}")
            self._increment_error_count()
        finally:
            # CORRECTION CRITIQUE : Toujours libérer le flag, même en cas d'exception
            self._sending_logs = False

    def log(self, level: str, message: str, **kwargs):
        """
        Envoie un log dans Discord.
        """
        # CORRECTION : Filtrer certains logs pour éviter le spam
        if self._sending_logs or self._is_in_cooldown():
            return  # Eviter les boucles et respecter le cooldown

        # NOUVEAU : Validation et nettoyage des paramètres
        safe_message = str(message) if message else "Message vide"
        safe_level = str(level).upper() if level else "INFO"
        
        # Nettoyer les kwargs
        safe_kwargs = {}
        for key, value in kwargs.items():
            if value is not None:
                safe_kwargs[key] = str(value)

        log_entry = {'level': safe_level, 'message': safe_message, **safe_kwargs}

        if self._bot_ready:
            self._send_log_async(log_entry)
        else:
            # CORRECTION : Limiter la taille du cache
            if len(self._log_cache) < 20:
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
        # CORRECTION : Logger seulement les commandes importantes pour éviter le spam
        important_commands = [
            'config-channels', 'test-logs', 'stats-logs', 'sync_bot', 
            'reload_commands', 'debug_bot'
        ]

        if command_name not in important_commands:
            return  # Ne pas logger les commandes normales

        level = 'INFO' if success else 'WARNING'
        status = '✅' if success else '❌'

        message = f"{status} Commande admin utilisée: `/{command_name}`"

        try:
            self.log(
                level,
                message,
                user=f"{interaction.user.display_name} ({interaction.user.id})",
                guild=f"{interaction.guild.name} ({interaction.guild.id})"
                if interaction.guild else "DM",
                command=f"/{command_name}",
                channel=f"#{interaction.channel.name}" if hasattr(
                    interaction.channel, 'name') else str(interaction.channel))
        except Exception as e:
            logger.error(f"Erreur logging commande {command_name}: {e}")

    def bot_event(self,
                  event_name: str,
                  message: str,
                  level: str = 'INFO',
                  **kwargs):
        """Log un événement du bot."""
        try:
            self.log(level, f"🤖 {event_name}: {message}", **kwargs)
        except Exception as e:
            logger.error(f"Erreur logging événement {event_name}: {e}")

    def error_with_traceback(self, message: str, error: Exception, **kwargs):
        """Log une erreur avec traceback complet."""
        try:
            tb = traceback.format_exc()
            self.log('ERROR', message, error=str(error), traceback=tb, **kwargs)
        except Exception as e:
            logger.error(f"Erreur logging traceback: {e}")

    def admin_action(self,
                     action: str,
                     user: discord.Member,
                     details: str = "",
                     **kwargs):
        """Log une action d'administration."""
        try:
            message = f"🔧 Action admin: {action}"
            if details:
                message += f" - {details}"

            self.log('INFO',
                     message,
                     user=f"{user.display_name} ({user.id})",
                     guild=f"{user.guild.name} ({user.guild.id})",
                     **kwargs)
        except Exception as e:
            logger.error(f"Erreur logging action admin {action}: {e}")

    async def test_logging(self, guild: discord.Guild) -> dict:
        """Teste le système de logging pour un serveur."""
        admin_channel = self._get_admin_channel(guild)

        result = {
            'channel_found': admin_channel is not None,
            'channel_name': admin_channel.name if admin_channel else None,
            'can_send': False,
            'test_sent': False,
            'in_cooldown': self._is_in_cooldown(),  # NOUVEAU
            'error_count': self._error_count  # NOUVEAU
        }

        if admin_channel:
            try:
                # Tester les permissions
                permissions = admin_channel.permissions_for(guild.me)
                result['can_send'] = permissions.send_messages and permissions.embed_links

                if result['can_send'] and not self._is_in_cooldown():
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
                    embed.add_field(name="🔧 Protection",
                                    value=f"Anti-doublons activé\nErreurs: {self._error_count}/{self._max_errors}",
                                    inline=True)
                    
                    if self._is_in_cooldown():
                        embed.add_field(name="⏸️ Cooldown",
                                       value="Système en pause temporaire",
                                       inline=True)
                    
                    embed.set_footer(
                        text="Test effectué par le système de logs Discord")

                    await admin_channel.send(embed=embed)
                    result['test_sent'] = True

            except discord.Forbidden:
                result['can_send'] = False
                self._increment_error_count()
            except Exception as e:
                logger.error(f"Erreur test logging: {e}")
                result['error'] = str(e)
                self._increment_error_count()

        return result

    def get_status(self) -> dict:
        """NOUVEAU : Retourne le statut actuel du Discord Logger."""
        return {
            'ready': self._bot_ready,
            'sending': self._sending_logs,
            'error_count': self._error_count,
            'max_errors': self._max_errors,
            'in_cooldown': self._is_in_cooldown(),
            'cache_size': len(self._log_cache),
            'sent_messages_cache': len(self._sent_messages),
            'last_error': self._last_error_time.isoformat() if self._last_error_time else None
        }

    def reset_errors(self):
        """NOUVEAU : Reset manuel du compteur d'erreurs."""
        self._error_count = 0
        self._last_error_time = None
        logger.info("Compteur d'erreurs Discord Logger remis à zéro")

    def clear_cache(self):
        """Nettoie le cache de messages pour libérer la mémoire."""
        cache_size = len(self._sent_messages)
        self._sent_messages.clear()
        self._log_cache.clear()
        logger.info(f"Cache de logs nettoyé ({cache_size} messages supprimés)")


# Instance globale (sera initialisée dans le bot principal)
discord_logger: Optional[DiscordLogger] = None


def init_discord_logger(bot):
    """Initialise le logger Discord."""
    global discord_logger
    discord_logger = DiscordLogger(bot)
    logger.info("Discord Logger initialisé avec protection anti-doublons et gestion d'erreurs avancée")
    return discord_logger


def get_discord_logger() -> Optional[DiscordLogger]:
    """Récupère l'instance du logger Discord."""
    return discord_logger