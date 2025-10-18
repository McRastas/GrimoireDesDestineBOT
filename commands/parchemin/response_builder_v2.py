# commands/parchemin/response_builder_v2.py
"""
Constructeur de réponses Discord pour les parchemins de sorts.
Supporte deux formats : TABLEAU ou CLASSIQUE
"""

import discord
import logging
from typing import List, Dict, Optional
from .config_v2 import get_config, normalize_school_name, normalize_level_name

logger = logging.getLogger(__name__)

class ParcheminResponseBuilderV2:
    """
    Classe pour construire les réponses Discord adaptée aux parchemins de sorts.
    Supporte deux formats d'affichage : tableau ou classique.
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
            format_type: "tableau" ou "classique" (défaut: classique)
            
        Returns:
            discord.Embed: Embed formaté
        """
        logger.info(f"Création embed parchemin - {len(spells)} sorts - format: {format_type}")
        
        # Utiliser le format demandé
        if format_type.lower() == "tableau":
            return self._create_tableau_embed(spells, stats, spell_indices, filters)
        else:
            return self._create_classique_embed(spells, stats, spell_indices, filters)
    
    # ========================================================================
    # FORMAT TABLEAU
    # ========================================================================
    
    def _create_tableau_embed(self, spells: List[Dict], stats: Dict[str, any] = None,
                              spell_indices: List[int] = None, filters: Dict[str, any] = None) -> discord.Embed:
        """Crée l'embed avec affichage TABLEAU."""
        
        embed_color = self._get_embed_color_by_level(spells)
        title = f"📜 Parchemins de Sorts - {len(spells)} disponible{'s' if len(spells) > 1 else ''}"
        description = self._build_description_with_filters(filters)
        
        embed = discord.Embed(
            title=title,
            description=description,
            color=embed_color
        )
        
        # Grouper les sorts par niveau
        spells_by_level = self._group_spells_by_level(spells)
        
        # Affichage TABLEAU par niveau
        for level in sorted(spells_by_level.keys()):
            level_spells = spells_by_level[level]
            field_name = self._get_level_field_name(level, len(level_spells))
            field_value = self._format_level_spells_tableau(level_spells, spell_indices)
            
            if len(field_value) > self.max_field_length:
                field_value = self._truncate_field_value(field_value)
            
            embed.add_field(
                name=field_name,
                value=field_value,
                inline=False
            )
        
        footer_text = self._create_footer_text(stats) + " • Format: Tableau"
        embed.set_footer(text=footer_text)
        
        return embed
    
    def _format_level_spells_tableau(self, spells: List[Dict], spell_indices: List[int] = None) -> str:
        """Formate les sorts d'un niveau en format TABLEAU."""
        if not spells:
            return "❌ Aucun sort disponible"
        
        lines = []
        
        # En-têtes du tableau
        lines.append("```")
        lines.append("┌────────────────────┬────────────┬──────────────┐")
        lines.append("│ Sort               │ École      │ Classe       │")
        lines.append("├────────────────────┼────────────┼──────────────┤")
        
        # Corps du tableau
        for i, spell in enumerate(spells):
            name = spell.get('name', 'Inconnu')[:17].ljust(17)
            school = self._format_school_short(spell.get('school', 'Inconnue'))[:10].ljust(10)
            
            # Classes (première classe)
            classes = spell.get('classes', [])
            if isinstance(classes, str):
                classes = [c.strip() for c in classes.split(',')]
            
            first_class = self._format_class_emoji(classes[0] if classes else "Unknown")[:12].ljust(12)
            
            line = f"│ {name} │ {school} │ {first_class} │"
            lines.append(line)
        
        # Fermature du tableau
        lines.append("└────────────────────┴────────────┴──────────────┘")
        lines.append("```")
        
        # Détails supplémentaires
        details = self._format_spells_details(spells)
        if details:
            lines.append("")
            lines.append(details)
        
        return "\n".join(lines)
    
    def _format_school_short(self, school: str) -> str:
        """Formate le nom court d'école avec emoji."""
        school_lower = school.lower().strip()
        emoji = self.school_emojis.get(school_lower, '🔮')
        
        abbrev_map = {
            'abjuration': 'Abjur.',
            'conjuration': 'Conj.',
            'divination': 'Div.',
            'enchantment': 'Ench.',
            'evocation': 'Evoc.',
            'illusion': 'Illu.',
            'necromancy': 'Necro.',
            'transmutation': 'Trans.',
        }
        
        abbrev = abbrev_map.get(school_lower, school[:6])
        return f"{emoji} {abbrev}"
    
    def _format_class_emoji(self, class_name: str) -> str:
        """Formate le nom de classe avec emoji."""
        class_map = {
            'artificer': '⚙️ Artificer',
            'bard': '🎵 Bard',
            'cleric': '⛪ Cleric',
            'druid': '🌿 Druid',
            'paladin': '⚔️ Paladin',
            'ranger': '🏹 Ranger',
            'sorcerer': '✨ Sorc.',
            'warlock': '👁️ Warl.',
            'wizard': '🔵 Wizard',
        }
        
        class_lower = class_name.lower().strip()
        return class_map.get(class_lower, f"• {class_name}")
    
    def _format_spells_details(self, spells: List[Dict]) -> str:
        """Formate les détails supplémentaires des sorts."""
        details = []
        
        for spell in spells[:5]:  # Limiter pour ne pas surcharger
            name = spell.get('name', 'Inconnu')
            level = spell.get('level', 0)
            ritual = spell.get('ritual', False)
            source = spell.get('source', 'Manuel inconnu')
            
            level_emoji = self.level_emojis.get(level, '🔥')
            ritual_emoji = self.ritual_emojis.get(ritual, '')
            
            detail_line = f"• **{name}** {level_emoji} {ritual_emoji} — *{source}*"
            details.append(detail_line)
        
        if len(spells) > 5:
            details.append(f"*... et {len(spells) - 5} autres sorts*")
        
        return "\n".join(details) if details else ""
    
    # ========================================================================
    # FORMAT CLASSIQUE
    # ========================================================================
    
    def _create_classique_embed(self, spells: List[Dict], stats: Dict[str, any] = None,
                                spell_indices: List[int] = None, filters: Dict[str, any] = None) -> discord.Embed:
        """Crée l'embed avec affichage CLASSIQUE (par niveau, détails complets)."""
        
        embed_color = self._get_embed_color_by_level(spells)
        title = f"📜 Parchemins de Sorts - {len(spells)} disponible{'s' if len(spells) > 1 else ''}"
        description = self._build_description_with_filters(filters)
        
        embed = discord.Embed(
            title=title,
            description=description,
            color=embed_color
        )
        
        # Grouper les sorts par niveau
        spells_by_level = self._group_spells_by_level(spells)
        
        # Affichage CLASSIQUE par niveau
        for level in sorted(spells_by_level.keys()):
            level_spells = spells_by_level[level]
            field_name = self._get_level_field_name(level, len(level_spells))
            field_value = self._format_level_spells_classique(level_spells, spell_indices)
            
            if len(field_value) > self.max_field_length:
                field_value = self._truncate_field_value(field_value)
            
            embed.add_field(
                name=field_name,
                value=field_value,
                inline=False
            )
        
        footer_text = self._create_footer_text(stats) + " • Format: Classique"
        embed.set_footer(text=footer_text)
        
        return embed
    
    def _format_level_spells_classique(self, spells: List[Dict], spell_indices: List[int] = None) -> str:
        """Formate les sorts d'un niveau en format CLASSIQUE (listing détaillé)."""
        if not spells:
            return "❌ Aucun sort disponible"
        
        lines = []
        
        for i, spell in enumerate(spells, 1):
            name = spell.get('name', 'Inconnu')
            school = spell.get('school', 'Inconnue')
            ritual = spell.get('ritual', False)
            source = spell.get('source', 'Manuel inconnu')
            
            # Classes
            classes = spell.get('classes', [])
            if isinstance(classes, str):
                classes = [c.strip() for c in classes.split(',')]
            
            classes_str = ', '.join(classes) if classes else 'Diverses'
            
            # Formatage du sort
            school_emoji = self.school_emojis.get(school.lower(), '🔮')
            ritual_emoji = self.ritual_emojis.get(ritual, '')
            
            line = f"**{i}. {name}** {ritual_emoji}\n"
            line += f"   {school_emoji} *{school}* • {classes_str}\n"
            line += f"   📖 {source}"
            
            lines.append(line)
        
        return "\n\n".join(lines)
    
    # ========================================================================
    # FONCTIONS UTILITAIRES COMMUNES
    # ========================================================================
    
    def _group_spells_by_level(self, spells: List[Dict]) -> Dict[int, List[Dict]]:
        """Groupe les sorts par niveau."""
        grouped = {}
        
        for spell in spells:
            level = int(spell.get('level', 0))
            if level not in grouped:
                grouped[level] = []
            grouped[level].append(spell)
        
        return grouped
    
    def _get_level_field_name(self, level: int, count: int) -> str:
        """Crée le nom du champ pour un niveau."""
        if level == 0:
            emoji = self.level_emojis.get(0, '✨')
            return f"{emoji} Tours de Magie ({count})"
        else:
            emoji = self.level_emojis.get(level, '🔥')
            return f"{emoji} Niveau {level} ({count})"
    
    def _build_description_with_filters(self, filters: Dict[str, any] = None) -> str:
        """Crée la description avec les filtres appliqués."""
        if not filters:
            return "🎲 Sélection aléatoire de sorts depuis Faerûn"
        
        desc_parts = ["🎲 Sélection aléatoire"]
        
        if filters.get('level_range'):
            desc_parts.append(f"| Niveau: {filters['level_range']}")
        
        if filters.get('school_filter'):
            desc_parts.append(f"| École: {filters['school_filter']}")
        
        if filters.get('class_filter'):
            desc_parts.append(f"| Classe: {filters['class_filter']}")
        
        if filters.get('ritual_filter') is not None:
            ritual_text = "Rituels seulement" if filters['ritual_filter'] else "Rituels inclus"
            desc_parts.append(f"| {ritual_text}")
        
        return " ".join(desc_parts)
    
    def _truncate_field_value(self, value: str) -> str:
        """Tronque une valeur si elle est trop longue."""
        if len(value) <= self.max_field_length:
            return value
        
        truncated = value[:self.max_field_length - 50]
        last_newline = truncated.rfind('\n')
        
        if last_newline > self.max_field_length // 2:
            truncated = truncated[:last_newline]
        
        return truncated + "\n\n*[Contenu tronqué]*"
    
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