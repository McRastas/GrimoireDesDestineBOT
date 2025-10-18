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
                               format_type: str = "classique"):
        """
        Crée l'embed (ou les embeds) principal des parchemins.
        
        Args:
            spells: Liste des sorts sélectionnés
            stats: Statistiques optionnelles
            spell_indices: Indices originaux des sorts
            filters: Filtres appliqués
            format_type: Ignoré, affichage copiable uniquement
            
        Returns:
            discord.Embed ou List[discord.Embed]: Embed(s) formaté(s)
        """
        logger.info(f"Création embed parchemin - {len(spells)} sorts")
        
        return self._create_copyable_embeds(spells, stats, spell_indices, filters)
    
    # ========================================================================
    # FORMAT COPIABLE
    # ========================================================================
    
    def _create_copyable_embeds(self, spells: List[Dict], stats: Dict[str, any] = None,
                               spell_indices: List[int] = None, filters: Dict[str, any] = None):
        """
        Crée un ou plusieurs embeds avec affichage COPIABLE.
        
        Retourne un seul embed si tout tient, ou une liste d'embeds si besoin de pagination.
        Un nouvel embed est créé pour chaque chunk (découpage naturel par limite de caractères).
        """
        # Couleur de l'embed basée sur le niveau moyen
        embed_color = self._get_embed_color_by_level(spells)
        description = self._build_description_with_filters(filters)
        
        # Construire la liste copiable
        spell_list = self._build_spell_list(spells)
        
        # Découper en chunks (le découpage tient compte des backticks)
        chunks = self._split_field_value(spell_list, self.max_field_length)
        
        # Créer un embed par chunk
        embeds = []
        
        for chunk_index, chunk in enumerate(chunks):
            # Créer l'embed
            if len(chunks) == 1:
                # Un seul embed nécessaire
                title = f"📜 Parchemins de Sorts - {len(spells)} disponible{'s' if len(spells) > 1 else ''}"
            else:
                # Plusieurs embeds nécessaires - un par chunk
                title = f"📜 Parchemins de Sorts ({chunk_index + 1}/{len(chunks)}) - {len(spells)} sorts"
            
            embed = discord.Embed(
                title=title,
                description=description if chunk_index == 0 else None,  # Description seulement sur le premier
                color=embed_color
            )
            
            # Ajouter le chunk comme field unique
            if chunk_index == 0:
                field_name = "📋 Parchemins (Copie facile)"
                # Ajouter les backticks pour le formatage code Discord
                chunk = "```\n" + chunk + "\n```"
            else:
                field_name = f"📋 Parchemins (suite {chunk_index + 1})"
                # Ajouter les backticks aussi pour les chunks suivants
                chunk = "```\n" + chunk + "\n```"
            
            embed.add_field(
                name=field_name,
                value=chunk,
                inline=False
            )
            
            # Footer avec statistiques (seulement sur le dernier embed)
            if chunk_index == len(chunks) - 1:
                footer_text = self._create_footer_text(stats)
                footer_text += " | 💡 Sélectionnez le texte et copiez avec Ctrl+C"
                embed.set_footer(text=footer_text)
            else:
                embed.set_footer(text="👇 Voir l'embed suivant pour la suite")
            
            embeds.append(embed)
        
        # Retourner un seul embed ou une liste selon le cas
        if len(embeds) == 1:
            return embeds[0]
        else:
            logger.info(f"Création de {len(embeds)} embeds pour {len(spells)} sorts ({len(chunks)} chunks)")
            return embeds
    
    def _build_spell_list(self, spells: List[Dict]) -> str:
        """Construit la liste copiable des sorts avec nom français en premier."""
        lines = []
        
        for spell in spells:
            name_en = spell.get('name', 'Inconnu')
            
            # 🔧 FIX: Chercher 'name_vf' (avec underscore) au lieu de 'NameVF'
            # C'est la clé utilisée par google_sheets_client.py
            name_fr = spell.get('name_vf', spell.get('name_fr', None))
            
            level = spell.get('level', 0)
            school = spell.get('school', 'Inconnue')
            ritual = spell.get('ritual', False)
            
            # Classes
            classes = spell.get('classes', [])
            if isinstance(classes, str):
                classes = [c.strip() for c in classes.split(',')]
            classes_str = ' ; '.join(classes) if classes else 'Diverses'
            
            # Format: * Parchemin de Nom FR [Nom EN] (niveau X - ECOLE) | CLASSE1 ; CLASSE2
            ritual_marker = " 🔮" if ritual else ""
            
            # Afficher nom FR en premier si disponible, sinon juste le nom EN
            if name_fr and name_fr.strip() and name_fr != name_en:
                spell_name = f"{name_fr} [{name_en}]"
            else:
                spell_name = name_en
            
            line = f"* Parchemin de {spell_name} (niveau {level} - {school}){ritual_marker} | {classes_str}"
            lines.append(line)
        
        return "\n".join(lines)
    
    def _split_field_value(self, text: str, max_length: int) -> List[str]:
        """Découpe le texte en chunks pour respecter la limite Discord."""
        # Réserver de l'espace pour les backticks sur le premier chunk (8 caractères)
        first_chunk_max = max_length - 8  # Pour "```\n" et "\n```"
        
        if len(text) <= first_chunk_max:
            return [text]
        
        chunks = []
        current_chunk = []
        current_length = 0
        is_first_chunk = True
        
        for line in text.split('\n'):
            line_length = len(line) + 1  # +1 pour le newline
            
            # Utiliser la limite appropriée selon si c'est le premier chunk ou non
            chunk_limit = first_chunk_max if is_first_chunk else max_length
            
            if current_length + line_length > chunk_limit:
                # Sauvegarder le chunk et commencer un nouveau
                if current_chunk:
                    chunks.append('\n'.join(current_chunk))
                    is_first_chunk = False
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
        if not stats:
            return "🎲 Parchemins de Faerûn"
        
        footer_parts = []
        
        if stats.get('total_spells'):
            footer_parts.append(f"📚 {stats['total_spells']} sorts disponibles")
        
        if stats.get('level_distribution'):
            level_dist = stats['level_distribution']
            dist_str = ", ".join([f"Niv.{lvl}: {count}" for lvl, count in sorted(level_dist.items())])
            footer_parts.append(f"Répartition: {dist_str}")
        
        return " | ".join(footer_parts) if footer_parts else "🎲 Parchemins de Faerûn"
    
    def create_error_embed(self, title: str, description: str, color: int = 0xe74c3c) -> discord.Embed:
        """
        Crée un embed d'erreur standard.
        
        Args:
            title: Titre de l'erreur
            description: Description de l'erreur
            color: Couleur de l'embed (rouge par défaut)
            
        Returns:
            discord.Embed: Embed d'erreur formaté
        """
        embed = discord.Embed(
            title=f"❌ {title}",
            description=description,
            color=color
        )
        embed.set_footer(text="Contactez un administrateur si le problème persiste")
        return embed
    
    def create_loading_embed(self, title: str = None, description: str = None) -> discord.Embed:
        """
        Crée un embed de chargement.
        
        Args:
            title: Titre optionnel
            description: Description optionnelle
            
        Returns:
            discord.Embed: Embed de chargement formaté
        """
        embed = discord.Embed(
            title=title or "🔄 Chargement...",
            description=description or "Préparation des parchemins en cours...",
            color=0x3498db
        )
        return embed