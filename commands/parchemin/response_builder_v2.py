# commands/parchemin/response_builder_v2.py
"""
Constructeur de réponses Discord pour les parchemins de sorts.
Affichage amélioré avec tous les détails: nom, niveau, école, rituel, classe
"""

import discord
import logging
from typing import List, Dict, Optional
from .config_v2 import get_config

logger = logging.getLogger(__name__)

class ParcheminResponseBuilderV2:
    """
    Classe pour construire les réponses Discord adaptée aux parchemins de sorts.
    Affichage amélioré avec support tableau et classique.
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
        if format_type and format_type.lower() == "tableau":
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
            field_value = self._format_level_spells_tableau(level_spells)
            
            if len(field_value) > self.max_field_length:
                field_value = self._truncate_field_value(field_value)
            
            embed.add_field(
                name=field_name,
                value=field_value,
                inline=False
            )
        
        footer_text = self._create_footer_text(stats) + " • Format: 📊 Tableau"
        embed.set_footer(text=footer_text)
        
        return embed
    
    def _format_level_spells_tableau(self, spells: List[Dict]) -> str:
        """Formate les sorts d'un niveau en format TABLEAU avec tous les détails."""
        if not spells:
            return "❌ Aucun sort disponible"
        
        lines = []
        
        # En-têtes du tableau
        lines.append("```")
        lines.append("┌──────────────────────┬────────────┬──────────┬─────────────┐")
        lines.append("│ Sort                 │ École      │ Rituel   │ Classe      │")
        lines.append("├──────────────────────┼────────────┼──────────┼─────────────┤")
        
        # Corps du tableau
        for spell in spells:
            name = spell.get('name', 'Inconnu')[:19].ljust(19)
            school = self._format_school_short(spell.get('school', 'Inconnue'))[:10].ljust(10)
            
            # Rituel
            ritual = spell.get('ritual', False)
            ritual_text = ("Oui" if ritual else "Non")[:8].ljust(8)
            
            # Classes (première classe)
            classes = spell.get('classes', [])
            if isinstance(classes, str):
                classes = [c.strip() for c in classes.split(',')]
            
            first_class = self._format_class_emoji(classes[0] if classes else "Unknown")[:11].ljust(11)
            
            line = f"│ {name} │ {school} │ {ritual_text} │ {first_class} │"
            lines.append(line)
        
        # Fermature du tableau
        lines.append("└──────────────────────┴────────────┴──────────┴─────────────┘")
        lines.append("```")
        
        # Détails complets sous le tableau
        lines.append("\n**Détails des sorts:**")
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
            
            # Formatage
            level_emoji = self.level_emojis.get(level, '🔥')
            school_emoji = self.school_emojis.get(school.lower(), '🔮')
            ritual_emoji = self.ritual_emojis.get(ritual, '')
            
            detail = f"{i}. **{name}** {level_emoji}\n"
            detail += f"   {school_emoji} {school} {ritual_emoji}\n"
            detail += f"   📚 {classes_str}\n"
            detail += f"   📖 {source}"
            lines.append(detail)
        
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
            'sorcerer': '✨ Sorcer.',
            'warlock': '👁️ Warlock',
            'wizard': '🔵 Wizard',
        }
        
        class_lower = class_name.lower().strip()
        return class_map.get(class_lower, f"• {class_name}")
    
    # ========================================================================
    # FORMAT CLASSIQUE
    # ========================================================================
    
    def _create_classique_embed(self, spells: List[Dict], stats: Dict[str, any] = None,
                                spell_indices: List[int] = None, filters: Dict[str, any] = None) -> discord.Embed:
        """Crée l'embed avec affichage CLASSIQUE (détails complets)."""
        
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
            ritual_emoji = self.ritual_emojis.get(ritual, '')
            ritual_text = " 🔮 *Rituel*" if ritual else ""
            
            # Création du field
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
        
        footer_text = self._create_footer_text(stats) + " • Format: 📄 Classique"
        embed.set_footer(text=footer_text)
        
        return embed
    
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