"""Constructeur de réponses Discord pour verifier_maj."""

import discord
from typing import Dict, Any

class ResponseBuilder:
    """Construit et envoie les réponses Discord."""
    
    def __init__(self):
        self.colors = {
            'success': 0x00ff00,
            'warning': 0xffaa00,
            'error': 0xff0000,
            'info': 0x3498db
        }
    
    async def send_validation_result(self, interaction: discord.Interaction, 
                                   message: discord.Message, result: Dict[str, Any], 
                                   include_suggestions: bool = True):
        """Envoie le résultat de validation complet."""
        
        # Créer l'embed principal
        embed = self._create_validation_embed(message, result)
        await interaction.followup.send(embed=embed, ephemeral=True)
        
        # Envoyer les corrections si disponibles
        if result.get('corrections_generated') and result.get('corrected_content'):
            await self._send_corrections(interaction, result['corrected_content'])
    
    def _create_validation_embed(self, message: discord.Message, result: Dict[str, Any]) -> discord.Embed:
        """Crée l'embed de validation."""
        completion = result.get('completion_percentage', 0)
        
        # Couleur basée sur le score
        if completion >= 80:
            color = self.colors['success']
            status = "✅ Template conforme"
        elif completion >= 50:
            color = self.colors['warning'] 
            status = "⚠️ Template à améliorer"
        else:
            color = self.colors['error']
            status = "❌ Template incomplet"
        
        embed = discord.Embed(
            title=f"🔍 Vérification de template",
            description=status,
            color=color
        )
        
        # Statistiques
        embed.add_field(
            name="📊 Score",
            value=f"{result['score']}/{result['total_checks']} sections\n{completion:.1f}% conforme",
            inline=True
        )
        
        # Informations du message
        embed.add_field(
            name="📝 Message analysé",
            value=f"Par {message.author.mention}\nDans {message.channel.mention}",
            inline=True
        )
        
        # Corrections disponibles
        if result.get('corrections_generated'):
            embed.add_field(
                name="🔧 Corrections",
                value="✅ Template corrigé disponible ci-dessous",
                inline=False
            )
        
        return embed
    
    async def _send_corrections(self, interaction: discord.Interaction, corrected_content: str):
        """Envoie le template corrigé."""
        if len(corrected_content) > 1900:  # Limite Discord
            # Diviser en plusieurs messages
            parts = self._split_content(corrected_content)
            for i, part in enumerate(parts):
                embed = discord.Embed(
                    title=f"🔧 Template corrigé ({i+1}/{len(parts)})",
                    description=f"```\n{part}\n```",
                    color=self.colors['info']
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
        else:
            embed = discord.Embed(
                title="🔧 Template corrigé",
                description=f"```\n{corrected_content}\n```",
                color=self.colors['info']
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
    
    def _split_content(self, content: str, max_length: int = 1800) -> List[str]:
        """Divise le contenu en parties gérables."""
        if len(content) <= max_length:
            return [content]
        
        parts = []
        lines = content.split('\n')
        current_part = ""
        
        for line in lines:
            if len(current_part) + len(line) + 1 <= max_length:
                current_part += line + '\n'
            else:
                if current_part:
                    parts.append(current_part.rstrip())
                current_part = line + '\n'
        
        if current_part:
            parts.append(current_part.rstrip())
        
        return parts
    
    async def send_error(self, interaction: discord.Interaction, error_message: str):
        """Envoie un message d'erreur."""
        embed = discord.Embed(
            title="❌ Erreur",
            description=error_message,
            color=self.colors['error']
        )
        
        try:
            if not interaction.response.is_done():
                await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                await interaction.followup.send(embed=embed, ephemeral=True)
        except:
            # Fallback silencieux
            pass