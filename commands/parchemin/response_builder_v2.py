# commands/parchemin/response_builder_v2.py
"""
Constructeur de réponses Discord pour les parchemins de sorts.
Structure inspirée de boutique/response_builder_v2.py
"""

import discord
import logging
from typing import List, Dict, Optional
from .config_v2 import get_config, normalize_school_name, normalize_level_name

logger = logging.getLogger(__name__)

class ParcheminResponseBuilderV2:
    """
    Classe pour construire les réponses Discord adaptée aux parchemins de sorts.
    Équivalent de BoutiqueResponseBuilderV2 pour les sorts.
    """
    
    def __init__(self):
        """
        Initialise le constructeur de réponses.
        Même structure que BoutiqueResponseBuilderV2.__init__
        """
        self.max_field_length = 1024
        self.max_embed_length = 6000
        
        # Charger la configuration (même logique que boutique)
        config = get_config()
        self.school_emojis = config.get('school_emojis', {})
        self.level_emojis = config.get('level_emojis', {})
        self.ritual_emojis = config.get('ritual_emojis', {})
        self.discord_config = config.get('discord', {})
        
        logger.info("ParcheminResponseBuilderV2 initialisé")
    
    def create_parchemin_embed(self, spells: List[Dict], stats: Dict[str, any] = None, spell_indices: List[int] = None, filters: Dict[str, any] = None) -> discord.Embed:
        """
        Crée l'embed principal des parchemins.
        Équivalent de create_boutique_embed dans boutique.
        
        Args:
            spells: Liste des sorts sélectionnés
            stats: Statistiques optionnelles
            spell_indices: Indices originaux des sorts
            filters: Filtres appliqués
            
        Returns:
            discord.Embed: Embed formaté
        """
        logger.info(f"Création embed parchemin - {len(spells)} sorts, indices: {spell_indices}")
        
        # Couleur basée sur le niveau moyen (équivalent couleur boutique)
        embed_color = self._get_embed_color_by_level(spells)
        
        # Titre et description (même structure que boutique)
        title = f"📜 Parchemins de Sorts - {len(spells)} disponible{'s' if len(spells) > 1 else ''}"
        description = self._build_description_with_filters(filters)
        
        embed = discord.Embed(
            title=title,
            description=description,
            color=embed_color
        )
        
        # Grouper les sorts par niveau (équivalent groupement par rareté)
        spells_by_level = self._group_spells_by_level(spells)
        
        # Ajout des sorts comme champs par niveau
        for level in sorted(spells_by_level.keys()):
            level_spells = spells_by_level[level]
            field_name = self._get_level_field_name(level, len(level_spells))
            field_value = self._format_level_spells(level_spells, spell_indices)
            
            # Vérifier la longueur du champ (même logique que boutique)
            if len(field_value) > self.max_field_length:
                field_value = self._truncate_field_value(field_value)
            
            embed.add_field(
                name=field_name,
                value=field_value,
                inline=False
            )
        
        # Footer avec statistiques (même logique que boutique)
        footer_text = self._create_footer_text(stats)
        embed.set_footer(text=footer_text)
        
        return embed
    
    def _get_embed_color_by_level(self, spells: List[Dict]) -> int:
        """
        Détermine la couleur de l'embed basée sur le niveau moyen.
        Équivalent de la couleur par rareté dans boutique.
        
        Args:
            spells: Liste des sorts
            
        Returns:
            int: Couleur hexadécimale
        """
        if not spells:
            return 0x95a5a6  # Gris par défaut
        
        # Calculer le niveau moyen
        total_levels = sum(spell.get('level', 0) for spell in spells)
        avg_level = total_levels / len(spells)
        
        # Arrondir au niveau le plus proche
        rounded_level = round(avg_level)
        
        # Retourner la couleur correspondante
        color_map = self.discord_config.get('embed_color_by_level', {})
        return color_map.get(rounded_level, 0x95a5a6)
    
    def _build_description_with_filters(self, filters: Dict[str, any] = None) -> str:
        """
        Construit la description avec les filtres appliqués.
        Équivalent du système de description de boutique.
        
        Args:
            filters: Dictionnaire des filtres appliqués
            
        Returns:
            str: Description formatée
        """
        description_parts = ["Voici les parchemins de sorts disponibles aujourd'hui !"]
        
        if filters:
            filter_parts = []
            
            if filters.get('level_range'):
                min_level, max_level = filters['level_range']
                if min_level == max_level:
                    filter_parts.append(f"**Niveau:** {min_level}")
                else:
                    filter_parts.append(f"**Niveau:** {min_level}-{max_level}")
            
            if filters.get('school_filter'):
                filter_parts.append(f"**École:** {filters['school_filter'].title()}")
            
            if filters.get('class_filter'):
                filter_parts.append(f"**Classe:** {filters['class_filter'].title()}")
            
            if filters.get('ritual_filter') is not None:
                ritual_text = "Oui" if filters['ritual_filter'] else "Non"
                filter_parts.append(f"**Rituel:** {ritual_text}")
            
            if filter_parts:
                description_parts.append("\n**Filtres appliqués:** " + " • ".join(filter_parts))
        
        return "\n".join(description_parts)
    
    def _group_spells_by_level(self, spells: List[Dict]) -> Dict[int, List[Dict]]:
        """
        Groupe les sorts par niveau.
        Équivalent de groupement par rareté dans boutique.
        
        Args:
            spells: Liste des sorts
            
        Returns:
            Dict[int, List[Dict]]: Sorts groupés par niveau
        """
        grouped = {}
        for spell in spells:
            level = spell.get('level', 0)
            if level not in grouped:
                grouped[level] = []
            grouped[level].append(spell)
        return grouped
    
    def _get_level_field_name(self, level: int, count: int) -> str:
        """
        Crée le nom du field pour un niveau donné.
        Équivalent du nom de field par rareté dans boutique.
        
        Args:
            level: Niveau des sorts
            count: Nombre de sorts dans ce niveau
            
        Returns:
            str: Nom du field formaté
        """
        level_name = normalize_level_name(level)
        return f"{level_name} ({count} sort{'s' if count > 1 else ''})"
    
    def _format_level_spells(self, level_spells: List[Dict], spell_indices: List[int] = None) -> str:
        """
        Formate les sorts d'un niveau donné.
        Équivalent du formatage d'objets par rareté dans boutique.
        
        Args:
            level_spells: Sorts du niveau
            spell_indices: Indices originaux (optionnels)
            
        Returns:
            str: Contenu du field formaté
        """
        spell_lines = []
        
        for i, spell in enumerate(level_spells):
            # Récupérer l'index original si disponible
            original_index = None
            if spell_indices and i < len(spell_indices):
                original_index = spell_indices[i]
            
            # Formater une ligne de sort
            spell_line = self._format_spell_details(spell, original_index)
            spell_lines.append(spell_line)
        
        return '\n\n'.join(spell_lines) if spell_lines else "Aucun sort disponible"
    
    def _format_spell_details(self, spell: Dict, original_index: int = None) -> str:
        """
        Formate les détails d'un sort.
        Équivalent de _format_item_details dans boutique.
        
        Args:
            spell: Données du sort
            original_index: Index original dans la base (optionnel)
            
        Returns:
            str: Détails formatés du sort
        """
        details = []
        
        # Nom du sort avec emoji d'école et rituel
        name = spell.get('name', 'Sort mystérieux')
        school = spell.get('school', '').lower()
        school_emoji = self.school_emojis.get(school, '🔮')
        ritual_emoji = ' 🔮' if spell.get('ritual', False) else ''
        
        details.append(f"**{name}**{ritual_emoji}")
        
        # École et source
        school_name = spell.get('school', 'Inconnue')
        source = spell.get('source', 'Source inconnue')
        details.append(f"{school_emoji} *{school_name}* • *{source}*")
        
        # Classes disponibles
        classes = spell.get('classes', [])
        if classes:
            # Limiter l'affichage pour éviter les lignes trop longues
            classes_display = classes[:3]  # Première 3 classes
            classes_text = ", ".join(classes_display)
            if len(classes) > 3:
                classes_text += f" +{len(classes)-3}"
            details.append(f"*Classes: {classes_text}*")
        
        # Lien vers Google Sheets (même logique que boutique)
        sheets_link = self._generate_sheets_link(spell, original_index)
        if sheets_link:
            details.append(f"[📊 Voir dans Google Sheets]({sheets_link})")
        
        return '\n'.join(details)
    
    def _generate_sheets_link(self, spell: Dict, original_index: int = None) -> str:
        """
        Génère un lien direct vers Google Sheets pour un sort.
        Même logique que boutique/_generate_sheets_link.
        
        Args:
            spell: Données du sort
            original_index: Index original dans la base
            
        Returns:
            str: URL vers Google Sheets ou chaîne vide
        """
        try:
            # Récupérer la configuration (même logique que boutique)
            config = get_config()
            sheet_id = config['google_sheets']['sheet_id']
            sheet_gid = config['google_sheets'].get('sheet_gid', '0')
            
            spell_name = spell.get('name', 'Sort inconnu')
            
            if not sheet_id:
                logger.debug(f"Pas de lien généré pour {spell_name}: sheet_id manquant")
                return ""
            
            # Méthode 1: Si on a l'index original, utiliser le numéro de ligne
            if original_index is not None:
                # +2 car indices Python commencent à 0 et il y a une ligne d'en-tête
                row_number = original_index + 2
                url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit?gid={sheet_gid}#gid={sheet_gid}&range=A{row_number}"
                logger.debug(f"Lien généré pour {spell_name}: ligne {row_number}")
                return url
            
            # Méthode 2: Utiliser le nom du sort pour la recherche
            if spell_name and spell_name != 'Sort inconnu':
                from urllib.parse import quote
                name_encoded = quote(spell_name)
                url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit?gid={sheet_gid}#gid={sheet_gid}&search={name_encoded}"
                logger.debug(f"Lien de recherche généré pour {spell_name}")
                return url
            
            # Méthode 3: Lien vers la feuille spécifique
            url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit?gid={sheet_gid}#gid={sheet_gid}"
            logger.debug(f"Lien général généré pour {spell_name}")
            return url
            
        except Exception as e:
            logger.error(f"Erreur génération lien Google Sheets pour {spell_name}: {e}")
            return ""
    
    def _truncate_field_value(self, value: str) -> str:
        """
        Tronque la valeur d'un champ si elle est trop longue.
        Même logique que boutique/_truncate_field_value.
        
        Args:
            value: Valeur à tronquer
            
        Returns:
            str: Valeur tronquée si nécessaire
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
        Crée le texte du footer avec statistiques.
        Même logique que boutique/_create_footer_text.
        
        Args:
            stats: Statistiques optionnelles
            
        Returns:
            str: Texte du footer
        """
        footer_parts = ["🎲 Parchemins de Faerûn"]
        
        if stats:
            if 'total_spells' in stats:
                footer_parts.append(f"• {stats['total_spells']} sorts en base")
            if 'filtered_spells' in stats:
                footer_parts.append(f"• {stats['filtered_spells']} sorts disponibles")
        
        return " ".join(footer_parts)
    
    def create_error_embed(self, error_message: str, details: str = None) -> discord.Embed:
        """
        Crée un embed d'erreur.
        Même structure que boutique/create_error_embed.
        
        Args:
            error_message: Message d'erreur principal
            details: Détails techniques (optionnels)
            
        Returns:
            discord.Embed: Embed d'erreur formaté
        """
        embed = discord.Embed(
            title="❌ Erreur - Parchemins Indisponibles",
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
        
        embed.set_footer(text="Parchemins temporairement indisponibles")
        
        return embed
    
    def create_loading_embed(self) -> discord.Embed:
        """
        Crée un embed de chargement.
        Même structure que boutique/create_loading_embed.
        
        Returns:
            discord.Embed: Embed de chargement
        """
        embed = discord.Embed(
            title="🔄 Préparation des Parchemins...",
            description="Le mage sélectionne ses meilleurs sorts...",
            color=0xf39c12  # Orange
        )
        
        embed.set_footer(text="Veuillez patienter quelques instants")
        
        return embed
    
    def create_search_results_embed(self, spells: List[Dict], query: str, total_found: int = None) -> discord.Embed:
        """
        Crée un embed pour les résultats de recherche.
        Nouveau pour parchemin (pas dans boutique de base).
        
        Args:
            spells: Sorts trouvés
            query: Terme de recherche
            total_found: Nombre total trouvé (si différent de len(spells))
            
        Returns:
            discord.Embed: Embed des résultats
        """
        if not spells:
            embed = discord.Embed(
                title="🔍 Recherche de Sorts",
                description=f"Aucun sort trouvé pour : **{query}**",
                color=0x95a5a6  # Gris
            )
            return embed
        
        # Titre avec nombre de résultats
        display_count = len(spells)
        actual_total = total_found if total_found is not None else display_count
        
        if actual_total > display_count:
            title = f"🔍 Recherche de Sorts ({display_count}/{actual_total} résultats)"
        else:
            title = f"🔍 Recherche de Sorts ({display_count} résultat{'s' if display_count > 1 else ''})"
        
        embed = discord.Embed(
            title=title,
            description=f"Recherche pour : **{query}**",
            color=0x3498db  # Bleu
        )
        
        # Ajouter les sorts trouvés (limiter pour éviter les embeds trop longs)
        for i, spell in enumerate(spells[:10], 1):
            spell_info = self._format_search_spell_info(spell)
            embed.add_field(
                name=f"{i}. {spell['name']}",
                value=spell_info,
                inline=True
            )
        
        if len(spells) > 10:
            embed.add_field(
                name="...",
                value=f"Et {len(spells) - 10} autre{'s' if len(spells) - 10 > 1 else ''} sort{'s' if len(spells) - 10 > 1 else ''}",
                inline=False
            )
        
        return embed
    
    def _format_search_spell_info(self, spell: Dict) -> str:
        """
        Formate les informations d'un sort pour les résultats de recherche.
        
        Args:
            spell: Données du sort
            
        Returns:
            str: Informations formatées
        """
        level = spell.get('level', 0)
        level_text = "Cantrip" if level == 0 else f"Niv. {level}"
        
        school = spell.get('school', 'Inconnue')
        school_emoji = self.school_emojis.get(school.lower(), '🔮')
        
        ritual_emoji = " 🔮" if spell.get('ritual', False) else ""
        
        info_parts = [f"{level_text} • {school_emoji} {school}{ritual_emoji}"]
        
        # Classes (limiter pour éviter les lignes trop longues)
        classes = spell.get('classes', [])
        if classes:
            classes_short = ", ".join(classes[:2])
            if len(classes) > 2:
                classes_short += "..."
            info_parts.append(f"*{classes_short}*")
        
        return "\n".join(info_parts)