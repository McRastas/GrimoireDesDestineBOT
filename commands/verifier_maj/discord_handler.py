"""Gestionnaire des interactions Discord pour verifier_maj."""

import discord
import re
from typing import Optional, Tuple

class MessageHandler:
    """Gère le parsing des liens Discord et la récupération des messages."""
    
    def __init__(self, bot):
        self.bot = bot
    
    def parse_discord_link(self, link: str) -> Optional[Tuple[int, int, int]]:
        """Parse un lien Discord et retourne (guild_id, channel_id, message_id)."""
        # Nettoyer le lien
        link = link.strip().strip('<>')
        
        if not link.startswith(('http://', 'https://')):
            if link.startswith('discord'):
                link = 'https://' + link
            else:
                return None
        
        # Pattern simplifié
        pattern = r'https?://(?:www\.)?discord(?:app)?\.com/channels/(\d+)/(\d+)/(\d+)'
        match = re.search(pattern, link)
        
        if match:
            return tuple(int(x) for x in match.groups())
        return None
    
    async def get_message_from_link(self, link: str) -> Optional[discord.Message]:
        """Récupère un message Discord à partir d'un lien."""
        parsed = self.parse_discord_link(link)
        if not parsed:
            return None
        
        guild_id, channel_id, message_id = parsed
        
        try:
            guild = self.bot.get_guild(guild_id)
            if not guild:
                return None
            
            channel = guild.get_channel(channel_id)
            if not channel or not isinstance(channel, discord.TextChannel):
                return None
            
            message = await channel.fetch_message(message_id)
            return message
            
        except (discord.NotFound, discord.Forbidden, discord.HTTPException):
            return None