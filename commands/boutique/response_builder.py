# commands/boutique/response_builder.py
"""
Constructeur de réponses Discord pour la commande boutique.
"""

import discord
import logging
from typing import List, Dict, Optional
from .config import get_config

logger = logging.getLogger(__name__)

class BoutiqueResponseBuilder:
    """
    Classe pour construire les réponses Discord de la boutique.
    """
    
    def __init__(self):
        """Initialise le constructeur de réponses."""
        self.max_field_length = 1024  # Limite Discord pour les champs d'embed
        self.max_embed_length = 6000  # Limite Discord pour la longueur totale d'un embed
        
        # Charger la configuration
        config = get_config()
        self.lien_emojis = config.get('lien_magique_emojis', {
            'oui': '🔗',
            'non': '❌', 
            'maudit': '💀',
            'default': '🔮'
        })
    
    def create_boutique_embed(self, items: List[Dict[str, str]], stats: Dict[str, any] = None, item_indices: List[int] = None) -> discord.Embed:
        """
        Crée l'embed principal de la boutique.
        
        Args:
            items: Liste des objets sélectionnés
            stats: Statistiques optionnelles
            item_indices: Indices des objets dans la liste originale (pour les liens Google Sheets)
            
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
    
    def _format_item_details(self, item: Dict[str, str], original_index: int = None) -> str:
        """
        Formate les détails d'un objet.
        
        Args:
            item: Objet à formatter
            original_index: Index de l'objet dans la liste originale (pour le lien Google Sheets)
            
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
        
        # Lien magique (colonne G "Lien")
        lien_magique = item.get("Lien", "")
        if lien_magique and not lien_magique.startswith("http"):  # Pas un lien web
            lien_formatted = self._format_lien_magique(lien_magique)
            if lien_formatted:
                details.append(f"**Lien magique:** {lien_formatted}")
        
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
        
        # Lien vers Google Sheets (nouvelle fonctionnalité)
        sheets_link = self._generate_sheets_link(item, original_index)
        if sheets_link:
            details.append(f"[📊 Voir dans Google Sheets]({sheets_link})")
        
        # Lien web vers la source (si c'est un lien HTTP dans une autre colonne)
        link = item.get("Lien", "")
        if link and link.startswith("http"):
            details.append(f"[📖 Plus d'infos]({link})")
        
        return '\n'.join(details) if details else "Informations non disponibles"
    
    def _format_lien_magique(self, lien_value: str) -> str:
        """
        Formate l'information de lien magique avec emojis.
        
        Args:
            lien_value: Valeur de la colonne Lien
            
        Returns:
            str: Lien magique formaté avec emoji
        """
        if not lien_value:
            return ""
        
        lien_lower = lien_value.lower().strip()
        
        if lien_lower in ['oui', 'yes']:
            return f"{self.lien_emojis['oui']} Oui"
        elif lien_lower in ['non', 'no']:
            return f"{self.lien_emojis['non']} Non"
        elif lien_lower == 'maudit':
            return f"{self.lien_emojis['maudit']} Maudit"
        else:
            # Pour les autres valeurs, on les affiche telles quelles
            return f"{self.lien_emojis['default']} {lien_value}"
    
    def _generate_sheets_link(self, item: Dict[str, str], original_index: int = None) -> str:
        """
        Génère un lien direct vers la ligne de l'objet dans Google Sheets.
        
        Args:
            item: Objet pour lequel générer le lien
            original_index: Index de l'objet dans la liste originale
            
        Returns:
            str: URL vers Google Sheets ou chaîne vide si impossible
        """
        try:
            # Récupérer la configuration
            config = get_config()
            sheet_id = config['google_sheets']['sheet_id']
            sheet_gid = config['google_sheets'].get('sheet_gid', '775953869')
            
            if not sheet_id or not item:
                return ""
            
            # Méthode 1: Si on a l'index original, utiliser le numéro de ligne
            if original_index is not None:
                # +2 car les indices Python commencent à 0 et il y a une ligne d'en-tête
                row_number = original_index + 2
                # URL pour aller directement à une ligne spécifique (colonne B)
                # Format: https://docs.google.com/spreadsheets/d/{ID}/edit?gid={GID}#gid={GID}&range=B{ROW}
                return f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit?gid={sheet_gid}#gid={sheet_gid}&range=B{row_number}"
            
            # Méthode 2: Utiliser le nom de l'objet pour la recherche
            nom_objet = item.get("Nom de l'objet_1") or item.get("Nom de l'objet", "")
            if nom_objet:
                from urllib.parse import quote
                nom_encoded = quote(nom_objet)
                # URL avec recherche automatique sur la bonne feuille
                return f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit?gid={sheet_gid}#gid={sheet_gid}&search={nom_encoded}"
            
            # Méthode 3: Lien vers la feuille spécifique
            return f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit?gid={sheet_gid}#gid={sheet_gid}"
            
        except Exception as e:
            logger.debug(f"Erreur génération lien Google Sheets: {e}")
            return ""
    
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