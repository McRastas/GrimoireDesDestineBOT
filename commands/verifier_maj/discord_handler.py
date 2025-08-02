# commands/verifier_maj/discord_handler.py
"""Gestionnaire des interactions Discord pour verifier_maj."""

import discord
import re
import logging
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


class MessageHandler:
    """Gère le parsing des liens Discord et la récupération des messages."""
    
    def __init__(self, bot):
        self.bot = bot
    
    def parse_discord_link(self, link: str) -> Optional[Tuple[int, int, int]]:
        """Parse un lien Discord et retourne (guild_id, channel_id, message_id)."""
        # Nettoyer le lien
        link = link.strip().strip('<>')
        
        # Ajouter https:// si manquant
        if not link.startswith(('http://', 'https://')):
            if link.startswith('discord'):
                link = 'https://' + link
            else:
                return None
        
        # Patterns pour différents formats Discord
        patterns = [
            r'https?://(?:www\.)?discord(?:app)?\.com/channels/(\d+)/(\d+)/(\d+)',
            r'https?://(?:www\.)?discord\.com/channels/(\d+)/(\d+)/(\d+)',
            r'discord\.com/channels/(\d+)/(\d+)/(\d+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, link)
            if match:
                try:
                    return tuple(int(x) for x in match.groups())
                except ValueError:
                    continue
        
        return None
    
    async def get_message_from_link(self, link: str) -> Optional[discord.Message]:
        """Récupère un message Discord à partir d'un lien."""
        parsed = self.parse_discord_link(link)
        if not parsed:
            logger.warning(f"Impossible de parser le lien: {link}")
            return None
        
        guild_id, channel_id, message_id = parsed
        
        try:
            # Récupérer la guilde
            guild = self.bot.get_guild(guild_id)
            if not guild:
                logger.warning(f"Guilde {guild_id} non trouvée")
                return None
            
            # Récupérer le canal
            channel = guild.get_channel(channel_id)
            if not channel or not isinstance(channel, discord.TextChannel):
                logger.warning(f"Canal {channel_id} non trouvé ou non accessible")
                return None
            
            # Vérifier les permissions
            bot_member = guild.get_member(self.bot.user.id)
            if not bot_member:
                logger.warning(f"Bot non membre de la guilde {guild_id}")
                return None
            
            permissions = channel.permissions_for(bot_member)
            if not permissions.read_messages or not permissions.read_message_history:
                logger.warning(f"Permissions insuffisantes pour le canal {channel_id}")
                return None
            
            # Récupérer le message
            message = await channel.fetch_message(message_id)
            logger.info(f"Message {message_id} récupéré avec succès")
            return message
            
        except discord.NotFound:
            logger.warning(f"Message {message_id} non trouvé")
            return None
        except discord.Forbidden:
            logger.warning(f"Accès refusé pour le message {message_id}")
            return None
        except discord.HTTPException as e:
            logger.error(f"Erreur HTTP lors de la récupération du message {message_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Erreur inattendue lors de la récupération du message: {e}")
            return None
    
    def validate_link_format(self, link: str) -> bool:
        """Valide le format d'un lien Discord."""
        return self.parse_discord_link(link) is not None
    
    def get_link_info(self, link: str) -> Optional[dict]:
        """Retourne des informations sur un lien Discord."""
        parsed = self.parse_discord_link(link)
        if not parsed:
            return None
        
        guild_id, channel_id, message_id = parsed
        return {
            'guild_id': guild_id,
            'channel_id': channel_id,
            'message_id': message_id,
            'valid': True
        }