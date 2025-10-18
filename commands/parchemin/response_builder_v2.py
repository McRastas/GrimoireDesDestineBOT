# commands/parchemin/response_builder_v2.py
"""
Constructeur de réponses Discord pour les parchemins de sorts.
Affichage avec embed copiable et un champ texte facilement copiable.
"""

import discord
import logging
from typing import List, Dict, Optional
from .config_v2 import get_config

logger = logging.getLogger(__name__)

class ParcheminResponseBuilderV2:
    """
    Classe pour construire les réponses Discord adaptée aux parchemins de sorts.
    Affichage avec embed copiable facilement.
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
            format_type: Ignoré, affichage copiable uniquement
            
        Returns:
            discord.Embed: Embed formaté
        """
        logger.info(f"Création embed parchemin - {len(spells)} sorts")
        
        return self._create_copyable_embed(spells, stats, spell_indices, filters)
    
    # ========================================================================
    # FORMAT COPIABLE
    # ========================================================================
    
    def _create_copyable_embed(self, spells: List[Dict], stats: Dict[str, any] = None,
                              spell_indices: List[int] = None, filters: Dict[str, any] = None) -> discord.Embed:
        """Crée l'embed avec affichage COPIABLE."""
        
        embed_color = self._get_embed_color_by_level(spells)
        title = f"📜 Parchemins de Sorts - {len(spells)} disponible{'s' if len(spells) > 1 else ''}"
        description = self._build_description_with_filters(filters)
        
        embed = discord.Embed(
            title=title,
            description=description,
            color=embed_color
        )
        
        # Construire la liste copiable
        spell_list = self._build_spell_list(spells)
        
        # Découper en chunks si trop long
        chunks = self._split_field_value(spell_list, self.max_field_length)
        
        # Ajouter les chunks comme fields
        for i, chunk in enumerate(chunks):
            if i == 0:
                field_name = "📋 Parchemins (Copie facile)"
            else:
                field_name = "📋 Suite..."
            
            # Ajouter les instructions pour le premier field
            if i == 0:
                chunk = "```\n" + chunk + "\n```"
            
            embed.add_field(
                name=field_name,
                value=chunk,
                inline=False
            )
        
        # Footer avec statistiques et instructions
        footer_text = self._create_footer_text(stats)
        footer_text += " | 💡 Sélectionnez le texte et copiez avec Ctrl+C"
        embed.set_footer(text=footer_text)
        
        return embed
    
    def _build_spell_list(self, spells: List[Dict]) -> str:
        """Construit la liste copiable des sorts avec classes."""
        lines = []
        
        for spell in spells:
            name = spell.get('name', 'Inconnu')
            level = spell.get('level', 0)
            school = spell.get('school', 'Inconnue')
            ritual = spell.get('ritual', False)
            
            # Classes
            classes = spell.get('classes', [])
            if isinstance(classes, str):
                classes = [c.strip() for c in classes.split(',')]
            classes_str = ' ; '.join(classes) if classes else 'Diverses'
            
            # Format: * Parchemin de Nom (niveau X - ECOLE) | CLASSE1 ; CLASSE2
            ritual_marker = " 🔮" if ritual else ""
            line = f"* Parchemin de {name} (niveau {level} - {school}){ritual_marker} | {classes_str}"
            lines.append(line)
        
        return "\n".join(lines)
    
    def _split_field_value(self, text: str, max_length: int) -> List[str]:
        """Découpe le texte en chunks pour respecter la limite Discord."""
        if len(text) <= max_length:
            return [text]
        
        chunks = []
        current_chunk = []
        current_length = 0
        
        for line in text.split('\n'):
            line_length = len(line) + 1  # +1 pour le newline
            
            if current_length + line_length > max_length:
                # Sauvegarder le chunk et commencer un nouveau
                if current_chunk:
                    chunks.append('\n'.join(current_chunk))
                current_chunk = [line]
                current_length = line_length
            else:
                current_chunk.append(line)
                current_length += line_length
        
        # Ajouter le dernier chunk
        if current_chunk:
            chunks.append('\n'.join(current_chunk))
        
        return chunks
    
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