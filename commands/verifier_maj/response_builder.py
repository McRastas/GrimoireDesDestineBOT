# commands/verifier_maj/response_builder.py
"""Constructeur de réponses Discord pour verifier_maj."""

import discord
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class ResponseBuilder:
    """Construit et envoie les réponses Discord avec gestion des limites."""
    
    def __init__(self):
        self.colors = {
            'success': 0x00ff00,
            'warning': 0xffaa00,
            'error': 0xff0000,
            'info': 0x3498db
        }
        
        # Limites Discord
        self.FIELD_VALUE_LIMIT = 1024
        self.EMBED_DESCRIPTION_LIMIT = 4096
        self.MESSAGE_CONTENT_LIMIT = 2000
    
    def _safe_field_value(self, text: str, max_length: int = None) -> str:
        """Tronque un texte pour qu'il respecte les limites Discord."""
        if max_length is None:
            max_length = self.FIELD_VALUE_LIMIT - 50  # Marge de sécurité
        
        if len(text) <= max_length:
            return text
        
        # Tronquer intelligemment
        truncated = text[:max_length-10]
        if '\n' in truncated:
            # Couper à la dernière ligne complète
            truncated = truncated.rsplit('\n', 1)[0]
        
        return truncated + "\n... (tronqué)"
    
    async def send_validation_result(self, interaction: discord.Interaction, 
                                   message: discord.Message, result: Dict[str, Any], 
                                   include_suggestions: bool = True):
        """Envoie le résultat de validation complet."""
        
        try:
            # Créer l'embed principal
            embed = self._create_validation_embed(message, result)
            
            # S'assurer qu'on n'a pas déjà répondu
            if not interaction.response.is_done():
                await interaction.response.defer(ephemeral=True)
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
            # Envoyer les corrections si disponibles
            if result.get('corrections_generated') and result.get('corrected_content'):
                await self._send_corrections(interaction, result['corrected_content'])
                
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi du résultat de validation: {e}")
            await self._safe_error_response(interaction, "Erreur lors de l'affichage des résultats")
    
    def _create_validation_embed(self, message: discord.Message, result: Dict[str, Any]) -> discord.Embed:
        """Crée l'embed de validation avec protection des limites."""
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
            title="🔍 Vérification de template",
            description=status,
            color=color
        )
        
        # Statistiques de base
        score_text = (
            f"**{result['score']}/{result['total_checks']}** sections obligatoires\n"
            f"**{completion:.1f}%** de conformité"
        )
        
        placeholders_count = len(result.get('placeholders', []))
        if placeholders_count > 0:
            score_text += f"\n**{placeholders_count}** placeholders à compléter"
        
        embed.add_field(
            name="📊 Analyse détaillée",
            value=score_text,
            inline=True
        )
        
        # Informations du personnage détectées (avec limite)
        details = result.get('details', {})
        if details.get('nom_pj') or details.get('classe'):
            char_info = []
            if details.get('nom_pj'):
                char_info.append(f"**PJ :** {details['nom_pj']}")
            if details.get('classe'):
                char_info.append(f"**Classe :** {details['classe']}")
            
            embed.add_field(
                name="🎭 Personnage",
                value=self._safe_field_value("\n".join(char_info)),
                inline=True
            )
        
        # Informations du message
        embed.add_field(
            name="📝 Message analysé",
            value=f"Par {message.author.mention}\nDans {message.channel.mention}",
            inline=True
        )
        
        # Sections manquantes (limitées pour l'affichage)
        if result.get('sections_missing'):
            missing_labels = []
            section_labels = {
                'nom_pj': 'Nom PJ', 'classe': 'Classe', 'quete': 'Quête',
                'solde_xp': 'Solde XP', 'gain_niveau': 'Gain niveau',
                'capacites': 'Capacités', 'solde_final': 'Solde final'
            }
            
            # Limiter à 5 sections pour éviter de dépasser la limite
            sections_to_show = result['sections_missing'][:5]
            for section in sections_to_show:
                label = section_labels.get(section, section)
                missing_labels.append(f"• {label}")
            
            if len(result['sections_missing']) > 5:
                missing_labels.append(f"• ... et {len(result['sections_missing']) - 5} autres")
            
            missing_text = "\n".join(missing_labels)
            embed.add_field(
                name="❌ Sections manquantes",
                value=self._safe_field_value(missing_text),
                inline=False
            )
        
        # Corrections disponibles
        if result.get('corrections_generated'):
            embed.add_field(
                name="🔧 Corrections",
                value="✅ Template corrigé disponible ci-dessous",
                inline=False
            )
        
        # Avertissements (avec limite)
        warnings = result.get('warnings', [])
        if warnings:
            warnings_text = "\n".join([f"⚠️ {w}" for w in warnings[:3]])
            if len(warnings) > 3:
                warnings_text += f"\n... et {len(warnings) - 3} autres avertissements"
            
            embed.add_field(
                name="⚠️ Avertissements",
                value=self._safe_field_value(warnings_text),
                inline=False
            )
        
        return embed
    
    async def _send_corrections(self, interaction: discord.Interaction, corrected_content: str):
        """Envoie le template corrigé en gérant les limites Discord."""
        try:
            # Vérifier si le contenu est trop long pour un embed
            if len(corrected_content) > 1800:  # Marge de sécurité pour l'embed
                # Diviser en plusieurs messages
                parts = self._split_content(corrected_content)
                for i, part in enumerate(parts):
                    embed = discord.Embed(
                        title=f"🔧 Template corrigé (partie {i+1}/{len(parts)})",
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
                
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi des corrections: {e}")
            await interaction.followup.send(
                "❌ Erreur lors de l'envoi du template corrigé.", 
                ephemeral=True
            )
    
    def _split_content(self, content: str, max_length: int = 1800) -> List[str]:
        """Divise le contenu en parties gérables pour Discord."""
        if len(content) <= max_length:
            return [content]
        
        parts = []
        lines = content.split('\n')
        current_part = ""
        
        for line in lines:
            # Vérifier si ajouter cette ligne dépasserait la limite
            if len(current_part) + len(line) + 1 <= max_length:
                current_part += line + '\n'
            else:
                # Sauvegarder la partie actuelle
                if current_part:
                    parts.append(current_part.rstrip())
                
                # Commencer une nouvelle partie
                current_part = line + '\n'
                
                # Si une seule ligne est trop longue, la tronquer
                if len(current_part) > max_length:
                    parts.append(line[:max_length-10] + "... (tronqué)")
                    current_part = ""
        
        # Ajouter la dernière partie
        if current_part:
            parts.append(current_part.rstrip())
        
        return parts
    
    async def send_error(self, interaction: discord.Interaction, error_message: str, 
                        title: str = "❌ Erreur"):
        """Envoie un message d'erreur de manière sécurisée."""
        await self._safe_error_response(interaction, error_message, title)
    
    async def _safe_error_response(self, interaction: discord.Interaction, 
                                  error_message: str, title: str = "❌ Erreur"):
        """Envoie une réponse d'erreur en gérant les états d'interaction."""
        embed = discord.Embed(
            title=title,
            description=self._safe_field_value(error_message, self.EMBED_DESCRIPTION_LIMIT),
            color=self.colors['error']
        )
        
        try:
            if not interaction.response.is_done():
                await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                await interaction.followup.send(embed=embed, ephemeral=True)
        except discord.InteractionResponded:
            # L'interaction a déjà été traitée
            try:
                await interaction.followup.send(embed=embed, ephemeral=True)
            except Exception as e:
                logger.error(f"Impossible d'envoyer le message d'erreur: {e}")
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi de la réponse d'erreur: {e}")
            # Fallback: essayer un message simple
            try:
                simple_message = f"{title}: {error_message[:500]}"
                if not interaction.response.is_done():
                    await interaction.response.send_message(simple_message, ephemeral=True)
                else:
                    await interaction.followup.send(simple_message, ephemeral=True)
            except:
                # Dernier recours: log l'erreur
                logger.error(f"Impossible d'envoyer une réponse à l'utilisateur")
    
    async def send_link_validation_error(self, interaction: discord.Interaction, link: str):
        """Envoie un message d'erreur spécifique pour les liens invalides."""
        error_message = (
            f"Le lien fourni n'est pas valide ou accessible.\n\n"
            f"**Lien fourni :** `{link[:100]}{'...' if len(link) > 100 else ''}`\n\n"
            f"💡 **Solutions :**\n"
            f"• Vérifiez que le lien est correct et complet\n"
            f"• Assurez-vous que le bot a accès au canal\n"
            f"• Utilisez 'Copier le lien du message' (clic droit)\n"
            f"• Réessayez dans quelques instants"
        )
        await self.send_error(interaction, error_message, "🔗 Lien invalide")
    
    async def send_message_not_found_error(self, interaction: discord.Interaction):
        """Envoie un message d'erreur quand le message n'est pas trouvé."""
        error_message = (
            f"Le message n'a pas pu être récupéré.\n\n"
            f"💡 **Causes possibles :**\n"
            f"• Message supprimé\n"
            f"• Canal privé ou inaccessible\n"
            f"• Permissions insuffisantes\n"
            f"• Serveur différent"
        )
        await self.send_error(interaction, error_message, "📝 Message introuvable")