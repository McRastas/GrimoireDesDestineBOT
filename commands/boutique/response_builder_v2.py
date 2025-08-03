# commands/boutique/response_builder_v2.py
"""
Constructeur de réponses adapté pour OM_PRICE.csv
"""

import discord
import logging
from typing import List, Dict, Optional
from .config_v2 import get_config

logger = logging.getLogger(__name__)

class BoutiqueResponseBuilderV2:
    """
    Classe pour construire les réponses Discord adaptée au format OM_PRICE.
    """
    
    def __init__(self):
        """Initialise le constructeur de réponses."""
        self.max_field_length = 1024
        self.max_embed_length = 6000
        
        # Charger la configuration
        config = get_config()
        self.lien_emojis = config.get('lien_magique_emojis', {
            'y': '🔗',
            'n': '❌',
            'default': '🔮'
        })
        self.rarity_emojis = config.get('rarity_emojis', {})
    
    def create_boutique_embed(self, items: List[Dict[str, str]], stats: Dict[str, any] = None, item_indices: List[int] = None) -> discord.Embed:
        """
        Crée l'embed principal de la boutique pour OM_PRICE.
        """
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
            
            # Passer l'index de ligne si disponible
            original_index = item_indices[i-1] if item_indices and len(item_indices) >= i else None
            value = self._format_item_details(item, original_index)
            
            # Vérifier la longueur du champ
            if len(value) > self.max_field_length:
                value = self._truncate_field_value(value)
            
            embed.add_field(
                name=name,
                value=value,
                inline=False
            )
        
        # Footer avec statistiques
        footer_text = self._create_footer_text(stats)
        embed.set_footer(text=footer_text)
        
        return embed
    
    def _get_item_name(self, item: Dict[str, str], index: int) -> str:
        """
        Formate le nom d'un objet OM_PRICE.
        """
        name = item.get("nom_display", f"Objet #{index}")
        rarity = item.get("rarity_display", "")
        
        # Mapping direct des emojis par rareté
        emoji_map = {
            'commun': '⚪',
            'peu commun': '🟢',
            'rare': '🔵',
            'très rare': '🟣',
            'légendaire': '🟡'
        }
        
        rarity_lower = rarity.lower().strip()
        emoji = emoji_map.get(rarity_lower, '✨')
        
        return f"{emoji} {name}"
    
    def _format_item_details(self, item: Dict[str, str], original_index: int = None) -> str:
        """
        Formate les détails d'un objet OM_PRICE.
        """
        details = []
        
        # Rareté
        rarity = item.get("rarity_display", "Inconnue")
        if rarity:
            details.append(f"**Rareté:** {rarity}")
        
        # Type
        item_type = item.get("Type", "")
        if item_type:
            # Formatter le type (première lettre en majuscule, remplacer _ par espaces)
            formatted_type = item_type.replace("_", " ").title()
            details.append(f"**Type:** {formatted_type}")
        
        # Lien magique
        lien_display = item.get("lien_display", "")
        if lien_display:
            lien_formatted = self._format_lien_magique(lien_display)
            if lien_formatted:
                details.append(f"**Lien magique:** {lien_formatted}")
        
        # Prix
        price = item.get("price_display", "")
        if price and price != "Prix non spécifié":
            details.append(f"**Prix:** {price}")
        
        # Source
        source = item.get("Source", "")
        if source:
            details.append(f"**Source:** {source}")
        
        # Lien vers Google Sheets
        sheets_link = self._generate_sheets_link(item, original_index)
        if sheets_link:
            details.append(f"[📊 Voir dans Google Sheets]({sheets_link})")
        
        return '\n'.join(details) if details else "Informations non disponibles"
    
    def _format_lien_magique(self, lien_value: str) -> str:
        """
        Formate l'information de lien magique pour OM_PRICE.
        """
        if not lien_value:
            return ""
        
        lien_lower = lien_value.lower().strip()
        
        if lien_lower == 'oui':
            return f"{self.lien_emojis['y']} Oui"
        elif lien_lower == 'non':
            return f"{self.lien_emojis['n']} Non"
        else:
            return f"{self.lien_emojis['default']} {lien_value}"
    
    def _generate_sheets_link(self, item: Dict[str, str], original_index: int = None) -> str:
        """
        Génère un lien direct vers Google Sheets pour OM_PRICE.
        """
        try:
            # Récupérer la configuration
            config = get_config()
            sheet_id = config['google_sheets']['sheet_id']
            sheet_gid = config['google_sheets'].get('sheet_gid', '0')
            
            if not sheet_id or not item:
                return ""
            
            # Méthode 1: Si on a l'index original, utiliser le numéro de ligne
            if original_index is not None:
                # +2 car indices Python commencent à 0 et il y a une ligne d'en-tête
                row_number = original_index + 2
                # URL pour aller directement à une ligne spécifique (colonne A pour OM_PRICE)
                return f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit?gid={sheet_gid}#gid={sheet_gid}&range=A{row_number}"
            
            # Méthode 2: Utiliser le nom de l'objet pour la recherche
            nom_objet = item.get("nom_display", "")
            if nom_objet:
                from urllib.parse import quote
                nom_encoded = quote(nom_objet)
                return f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit?gid={sheet_gid}#gid={sheet_gid}&search={nom_encoded}"
            
            # Méthode 3: Lien vers la feuille spécifique
            return f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit?gid={sheet_gid}#gid={sheet_gid}"
            
        except Exception as e:
            logger.debug(f"Erreur génération lien Google Sheets: {e}")
            return ""
    
    def _truncate_field_value(self, value: str) -> str:
        """
        Tronque la valeur d'un champ si elle est trop longue.
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
        """
        embed = discord.Embed(
            title="🔄 Préparation de la Boutique...",
            description="Le marchand sélectionne ses meilleurs objets magiques...",
            color=0xf39c12  # Orange
        )
        
        embed.set_footer(text="Veuillez patienter quelques instants")
        
        return embed