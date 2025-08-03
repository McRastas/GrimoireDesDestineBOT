# commands/boutique/response_builder.py
"""
Constructeur de réponses Discord pour la commande boutique.
"""

import discord
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class BoutiqueResponseBuilder:
    """
    Classe pour construire les réponses Discord de la boutique.
    """
    
    def __init__(self):
        """Initialise le constructeur de réponses."""
        self.max_field_length = 1024  # Limite Discord pour les champs d'embed
        self.max_embed_length = 6000  # Limite Discord pour la longueur totale d'un embed
    
    def create_boutique_embed(self, items: List[Dict[str, str]], stats: Dict[str, any] = None) -> discord.Embed:
        """
        Crée l'embed principal de la boutique.
        
        Args:
            items: Liste des objets sélectionnés
            stats: Statistiques optionnelles
            
        Returns:
            discord.Embed: Embed formaté pour Discord
        """
        # Couleur aléatoire pour l'embed
        colors = [0x3498db, 0xe74c3c, 0x2ecc71, 0xf39c12, 0x9b59b6, 0x1abc9c]
        embed_color = colors[hash(str(len(items))) % len(colors)]
        
        embed = discord.Embed(
            title="🏪 Boutique Magique - Objets Disponibles",
            description=f"Voici {len(items)} objets magiques disponibles aujourd'hui !",
            color=embed_color
        )
        
        # Ajout des objets comme champs
        for i, item in enumerate(items, 1):
            name = self._get_item_name(item, i)
            value = self._format_item_details(item)
            
            # Vérifier la longueur du champ
            if len(value) > self.max_field_length:
                value = self._truncate_field_value(value)
            
            embed.add_field(
                name=name,
                value=value,
                inline=False
            )
        
        # Ajout du footer avec des statistiques
        footer_text = self._create_footer_text(stats)
        embed.set_footer(text=footer_text)
        
        return embed
    
    def _get_item_name(self, item: Dict[str, str], index: int) -> str:
        """
        Formate le nom d'un objet pour l'affichage.
        
        Args:
            item: Objet à formatter
            index: Index de l'objet
            
        Returns:
            str: Nom formaté
        """
        # Utiliser le nom d'affichage calculé lors de la validation
        name = item.get("Nom de l'objet_display") or item.get("Nom de l'objet_1") or item.get("Nom de l'objet", f"Objet #{index}")
        rarity = item.get("Rareté", "")
        
        # Emoji selon la rareté
        rarity_emojis = {
            'commun': '⚪',
            'peu commun': '🟢',
            'rare': '🔵',
            'très rare': '🟣',
            'légendaire': '🟡',
            'artefact': '🔴'
        }
        
        rarity_lower = rarity.lower().strip()
        emoji = rarity_emojis.get(rarity_lower, '✨')
        
        return f"{emoji} {name}"
    
    def _format_item_details(self, item: Dict[str, str]) -> str:
        """
        Formate les détails d'un objet.
        
        Args:
            item: Objet à formatter
            
        Returns:
            str: Détails formatés
        """
        details = []
        
        # Rareté
        rarity = item.get("Rareté", "Inconnue")
        if rarity:
            details.append(f"**Rareté:** {rarity}")
        
        # Type
        item_type = item.get("Type", "")
        if item_type:
            details.append(f"**Type:** {item_type}")
        
        # Information sur le lien (colonne G)
        link_info = item.get("Lien", "").strip()
        if link_info:
            # Normaliser les valeurs possibles
            link_normalized = link_info.lower()
            if link_normalized in ["oui", "yes"]:
                details.append("📖 **Objet avec lien source**")
            elif link_normalized in ["non", "no"]:
                details.append("📝 **Objet sans lien source**")
            elif link_normalized == "maudit":
                details.append("💀 **Objet maudit**")
            else:
                details.append(f"**Lien:** {link_info}")
        else:
            details.append("📝 **Objet sans lien source**")
        
        # Prix d'achat
        buy_price = item.get("Prix achat", "")
        if buy_price and buy_price != "Non spécifié":
            details.append(f"**Prix:** {buy_price}")
        
        # Spécificités
        specs = item.get("Spécificités", "")
        if specs:
            details.append(f"**Spécificités:** {specs}")
        
        # Effet (tronqué si trop long)
        effect = item.get("Effet", "")
        if effect and effect != "Effet mystérieux":
            if len(effect) > 200:
                effect = effect[:197] + "..."
            details.append(f"**Effet:** {effect}")
        
        return '\n'.join(details) if details else "Informations non disponibles"
    
    def _truncate_field_value(self, value: str) -> str:
        """
        Tronque la valeur d'un champ si elle est trop longue.
        
        Args:
            value: Valeur à tronquer
            
        Returns:
            str: Valeur tronquée
        """
        if len(value) <= self.max_field_length:
            return value
        
        # Tronquer en gardant une marge pour "..."
        truncated = value[:self.max_field_length - 50]
        
        # Essayer de couper à un endroit logique (fin de ligne)
        last_newline = truncated.rfind('\n')
        if last_newline > self.max_field_length // 2:
            truncated = truncated[:last_newline]
        
        return truncated + "\n\n*[Informations tronquées]*"
    
    def _create_footer_text(self, stats: Dict[str, any] = None) -> str:
        """
        Crée le texte du footer.
        
        Args:
            stats: Statistiques optionnelles
            
        Returns:
            str: Texte du footer
        """
        footer_parts = ["Boutique magique de Faerûn"]
        
        if stats:
            if 'total_items' in stats:
                footer_parts.append(f"• {stats['total_items']} objets en base")
            if 'filtered_items' in stats:
                footer_parts.append(f"• {stats['filtered_items']} objets disponibles")
        
        return " ".join(footer_parts)
    
    def create_error_embed(self, error_message: str, details: str = None) -> discord.Embed:
        """
        Crée un embed d'erreur.
        
        Args:
            error_message: Message d'erreur principal
            details: Détails optionnels sur l'erreur
            
        Returns:
            discord.Embed: Embed d'erreur
        """
        embed = discord.Embed(
            title="❌ Erreur - Boutique Indisponible",
            description=error_message,
            color=0xe74c3c  # Rouge
        )
        
        if details:
            embed.add_field(
                name="Détails techniques",
                value=details,
                inline=False
            )
        
        embed.add_field(
            name="Solutions possibles",
            value="• Vérifiez que le Google Sheets est accessible\n"
                  "• Réessayez dans quelques minutes\n"
                  "• Contactez un administrateur si le problème persiste",
            inline=False
        )
        
        embed.set_footer(text="Boutique temporairement fermée")
        
        return embed
    
    def create_loading_embed(self) -> discord.Embed:
        """
        Crée un embed de chargement.
        
        Returns:
            discord.Embed: Embed de chargement
        """
        embed = discord.Embed(
            title="🔄 Préparation de la Boutique...",
            description="Le marchand sélectionne ses meilleurs objets magiques...",
            color=0xf39c12  # Orange
        )
        
        embed.set_footer(text="Veuillez patienter quelques instants")
        
        return embed