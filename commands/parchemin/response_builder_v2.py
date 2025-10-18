# commands/parchemin/response_builder_v2.py
"""
Constructeur de réponses Discord pour les parchemins de sorts.
Affichage classique amélioré avec tous les détails: nom, niveau, école, rituel, classe
"""

import discord
import logging
from typing import List, Dict, Optional
from .config_v2 import get_config

logger = logging.getLogger(__name__)

class ParcheminResponseBuilderV2:
    """
    Classe pour construire les réponses Discord adaptée aux parchemins de sorts.
    Affichage classique amélioré.
    """
    
    def __init__(self):
        """Initialise le constructeur de réponses."""
        self.max_field_length = 1024
        self.max_embed_length = 6000
        
        config = get_config()
        self.school_emojis = config.get('school_emojis', {})
        self.level_emojis = config.get('level_emojis', {})
        self.ritual_emojis = config.get('ritual_emojis', {})
        self.discord_config = config.get('discord', {})
        
        logger.info("ParcheminResponseBuilderV2 initialisé")
    
    def create_parchemin_embed(self, spells: List[Dict], stats: Dict[str, any] = None, 
                               spell_indices: List[int] = None, filters: Dict[str, any] = None,
                               format_type: str = "classique") -> discord.Embed:
        """
        Crée l'embed principal des parchemins.
        
        Args:
            spells: Liste des sorts sélectionnés
            stats: Statistiques optionnelles
            spell_indices: Indices originaux des sorts
            filters: Filtres appliqués
            format_type: Ignoré, affichage classique uniquement
            
        Returns:
            discord.Embed: Embed formaté
        """
        logger.info(f"Création embed parchemin - {len(spells)} sorts")
        
        return self._create_classique_embed(spells, stats, spell_indices, filters)
    
    # ========================================================================
    # FORMAT CLASSIQUE AMÉLIORÉ
    # ========================================================================
    
    def _create_classique_embed(self, spells: List[Dict], stats: Dict[str, any] = None,
                                spell_indices: List[int] = None, filters: Dict[str, any] = None) -> discord.Embed:
        """Crée l'embed avec affichage CLASSIQUE amélioré."""
        
        embed_color = self._get_embed_color_by_level(spells)
        title = f"📜 Parchemins de Sorts - {len(spells)} disponible{'s' if len(spells) > 1 else ''}"
        description = self._build_description_with_filters(filters)
        
        embed = discord.Embed(
            title=title,
            description=description,
            color=embed_color
        )
        
        # Affichage CLASSIQUE avec tous les détails
        for i, spell in enumerate(spells, 1):
            name = spell.get('name', 'Inconnu')
            level = spell.get('level', 0)
            school = spell.get('school', 'Inconnue')
            ritual = spell.get('ritual', False)
            source = spell.get('source', 'Manuel inconnu')
            
            # Classes
            classes = spell.get('classes', [])
            if isinstance(classes, str):
                classes = [c.strip() for c in classes.split(',')]
            classes_str = ', '.join(classes) if classes else 'Diverses'
            
            # Formatage des emojis
            level_emoji = self.level_emojis.get(level, '🔥')
            school_emoji = self.school_emojis.get(school.lower(), '🔮')
            ritual_text = " 🔮 *Rituel*" if ritual else ""
            
            # Création du field avec meilleure mise en page
            field_name = f"{i}. {name} {level_emoji}"
            
            field_value = (
                f"**Niveau:** {level}\n"
                f"{school_emoji} **École:** {school}{ritual_text}\n"
                f"📚 **Classes:** {classes_str}\n"
                f"📖 **Source:** {source}"
            )
            
            embed.add_field(
                name=field_name,
                value=field_value,
                inline=False
            )
        
        footer_text = self._create_footer_text(stats)
        embed.set_footer(text=footer_text)
        
        return embed
    
    # ========================================================================
    # FONCTIONS UTILITAIRES
    # ========================================================================
    
    def _build_description_with_filters(self, filters: Dict[str, any] = None) -> str:
        """Crée la description avec les filtres appliqués."""
        if not filters:
            return "🎲 Sélection aléatoire de sorts depuis Faerûn"
        
        desc_parts = ["🎲 Sélection aléatoire"]
        
        if filters.get('level_range'):
            min_lvl, max_lvl = filters['level_range']
            if min_lvl == max_lvl:
                desc_parts.append(f"| Niveau: {min_lvl}")
            else:
                desc_parts.append(f"| Niveaux: {min_lvl}-{max_lvl}")
        
        if filters.get('school_filter'):
            desc_parts.append(f"| École: {filters['school_filter']}")
        
        if filters.get('class_filter'):
            desc_parts.append(f"| Classe: {filters['class_filter']}")
        
        if filters.get('ritual_filter') is not None:
            ritual_text = "Rituels seulement" if filters['ritual_filter'] else "Rituels inclus"
            desc_parts.append(f"| {ritual_text}")
        
        return " ".join(desc_parts)
    
    def _get_embed_color_by_level(self, spells: List[Dict]) -> int:
        """Détermine la couleur de l'embed basée sur le niveau moyen."""
        if not spells:
            return 0x95a5a6
        
        avg_level = sum(int(s.get('level', 0)) for s in spells) / len(spells)
        level_key = int(round(avg_level))
        
        color_map = self.discord_config.get('embed_color_by_level', {})
        return color_map.get(level_key, 0x9b59b6)
    
    def _create_footer_text(self, stats: Dict[str, any] = None) -> str:
        """Crée le texte du footer avec statistiques."""
        footer_parts = ["🎲 Parchemins de Faerûn"]
        
        if stats:
            if 'total_spells' in stats:
                footer_parts.append(f"• {stats['total_spells']} sorts en base")
            if 'filtered_spells' in stats:
                footer_parts.append(f"• {stats['filtered_spells']} disponibles")
        
        return " ".join(footer_parts)
    
    def create_error_embed(self, error_message: str, details: str = None) -> discord.Embed:
        """Crée un embed d'erreur."""
        embed = discord.Embed(
            title="❌ Erreur - Parchemins Indisponibles",
            description=error_message,
            color=0xe74c3c
        )
        
        if details:
            embed.add_field(name="Détails", value=details, inline=False)
        
        embed.set_footer(text="Parchemins temporairement indisponibles")
        
        return embed
    
    def create_loading_embed(self) -> discord.Embed:
        """Crée un embed de chargement."""
        embed = discord.Embed(
            title="🔄 Préparation des Parchemins...",
            description="Le mage sélectionne ses meilleurs sorts...",
            color=0xf39c12
        )
        
        embed.set_footer(text="Veuillez patienter quelques instants")
        
        return embed