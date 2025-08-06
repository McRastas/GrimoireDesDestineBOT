# commands/boutique/search_command.py
"""
Commande de recherche d'objets magiques avec recherche floue (fuzzy search).
"""

import discord
from discord import app_commands
import logging
import re
from typing import Optional, List, Dict, Tuple
from difflib import SequenceMatcher

from ..base import BaseCommand
from .google_sheets_client import GoogleSheetsClient
from .config_v2 import get_config
from .item_selector_v2 import ItemSelectorV2

logger = logging.getLogger(__name__)

class SearchCommand(BaseCommand):
    """
    Commande Discord pour rechercher des objets magiques dans la base de données.
    """
    
    def __init__(self, bot):
        """
        Initialise la commande de recherche.
        
        Args:
            bot: Instance du bot Discord
        """
        super().__init__(bot)
        
        # Configuration
        config = get_config()
        google_config = config['google_sheets']
        
        self.sheet_id = google_config['sheet_id']
        self.sheet_name = google_config['sheet_name']
        
        # Composants
        self.sheets_client = GoogleSheetsClient(self.sheet_id)
        self.item_selector = ItemSelectorV2()
        
        # Configuration de recherche
        self.min_similarity = 0.4  # Seuil de similarité minimum (40%)
        self.max_results = 10      # Nombre maximum de résultats
        
        logger.info("Commande de recherche d'objets magiques initialisée")
    
    @property
    def name(self) -> str:
        """Nom de la commande."""
        return "recherche-objet"
    
    @property
    def description(self) -> str:
        """Description de la commande."""
        return "Recherche des objets magiques par nom ou description"
    
    def register(self, tree: app_commands.CommandTree):
        """Enregistre la commande dans l'arbre des commandes Discord."""
        
        @tree.command(name=self.name, description=self.description)
        @app_commands.describe(
            recherche="Terme à rechercher (nom d'objet, description, etc.)",
            limite="Nombre maximum de résultats à afficher (1-15, défaut: 5)"
        )
        async def search_command(
            interaction: discord.Interaction,
            recherche: str,
            limite: Optional[int] = 5
        ):
            await self.callback(interaction, recherche, limite)
    
    async def callback(self, interaction: discord.Interaction, recherche: str, limite: Optional[int] = 5):
        """
        Traite la commande de recherche.
        
        Args:
            interaction: Interaction Discord
            recherche: Terme de recherche
            limite: Nombre maximum de résultats
        """
        try:
            # Validation des paramètres
            if not recherche or len(recherche.strip()) < 2:
                await interaction.response.send_message(
                    "❌ La recherche doit contenir au moins 2 caractères.",
                    ephemeral=True
                )
                return
            
            if limite < 1 or limite > 15:
                await interaction.response.send_message(
                    "❌ La limite doit être entre 1 et 15 résultats.",
                    ephemeral=True
                )
                return
            
            # Nettoyer le terme de recherche
            search_term = recherche.strip().lower()
            
            # Réponse immédiate avec embed de chargement
            loading_embed = self._create_loading_embed(search_term)
            await interaction.response.send_message(embed=loading_embed)
            
            # Récupération des données depuis Google Sheets
            logger.info(f"Recherche d'objets pour: '{search_term}'")
            raw_items = await self.sheets_client.fetch_sheet_data(self.sheet_name)
            
            if not raw_items:
                error_embed = self._create_error_embed(
                    "Base de données inaccessible",
                    "Impossible d'accéder à la base de données des objets magiques."
                )
                await interaction.edit_original_response(embed=error_embed)
                return
            
            # Recherche avec scoring de similarité
            search_results = self._search_items(raw_items, search_term, limite)
            
            if not search_results:
                no_results_embed = self._create_no_results_embed(search_term)
                await interaction.edit_original_response(embed=no_results_embed)
                return
            
            # Création de l'embed avec les résultats
            results_embed = self._create_results_embed(search_results, search_term)
            await interaction.edit_original_response(embed=results_embed)
            
            logger.info(f"Recherche terminée: {len(search_results)} résultats trouvés pour '{search_term}'")
            
        except Exception as e:
            logger.error(f"Erreur dans la commande de recherche: {e}", exc_info=True)
            
            try:
                error_embed = self._create_error_embed(
                    "Erreur lors de la recherche",
                    f"Une erreur inattendue s'est produite: {str(e)[:200]}"
                )
                
                if not interaction.response.is_done():
                    await interaction.response.send_message(embed=error_embed, ephemeral=True)
                else:
                    await interaction.edit_original_response(embed=error_embed)
            except:
                logger.error("Impossible d'envoyer une réponse d'erreur à l'utilisateur")
    
    def _search_items(self, items: List[Dict[str, str]], search_term: str, limit: int) -> List[Tuple[Dict[str, str], float, int]]:
        """
        Recherche des objets avec scoring de similarité.
        
        Args:
            items: Liste des objets de la base de données
            search_term: Terme de recherche (déjà nettoyé)
            limit: Nombre maximum de résultats
            
        Returns:
            List[Tuple[Dict, float, int]]: Liste des (objet, score, index_original) triée par score décroissant
        """
        results = []
        
        for index, item in enumerate(items):
            # Récupérer les champs à rechercher
            nom_fr = item.get("Nom de l'objet", "").lower()
            nom_en = item.get("Nom en VO", "").lower()
            type_obj = item.get("Type", "").lower()
            source = item.get("Source", "").lower()
            
            # Calculer les scores de similarité pour chaque champ
            scores = []
            
            # Nom français (priorité haute)
            if nom_fr:
                score_nom_fr = self._calculate_similarity(search_term, nom_fr)
                if score_nom_fr > 0:
                    scores.append(score_nom_fr * 2.0)  # Poids double pour le nom français
            
            # Nom anglais (priorité haute)
            if nom_en:
                score_nom_en = self._calculate_similarity(search_term, nom_en)
                if score_nom_en > 0:
                    scores.append(score_nom_en * 1.8)  # Poids élevé pour le nom anglais
            
            # Type d'objet (priorité moyenne)
            if type_obj:
                score_type = self._calculate_similarity(search_term, type_obj)
                if score_type > 0:
                    scores.append(score_type * 1.2)
            
            # Source (priorité faible)
            if source:
                score_source = self._calculate_similarity(search_term, source)
                if score_source > 0:
                    scores.append(score_source * 0.8)
            
            # Prendre le meilleur score
            if scores:
                best_score = max(scores)
                
                # Ne garder que les résultats au-dessus du seuil
                if best_score >= self.min_similarity:
                    results.append((item, best_score, index))
        
        # Trier par score décroissant et limiter les résultats
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:limit]
    
    def _calculate_similarity(self, search_term: str, text: str) -> float:
        """
        Calcule la similarité entre le terme de recherche et un texte.
        
        Args:
            search_term: Terme de recherche
            text: Texte à comparer
            
        Returns:
            float: Score de similarité (0.0 à 1.0)
        """
        if not search_term or not text:
            return 0.0
        
        # Nettoyage des textes
        search_clean = re.sub(r'[^\w\s]', '', search_term.lower()).strip()
        text_clean = re.sub(r'[^\w\s]', '', text.lower()).strip()
        
        if not search_clean or not text_clean:
            return 0.0
        
        # Correspondance exacte (score maximum)
        if search_clean == text_clean:
            return 1.0
        
        # Correspondance de début de mot
        if text_clean.startswith(search_clean):
            return 0.9
        
        # Correspondance contenue
        if search_clean in text_clean:
            return 0.8
        
        # Similarité de séquence (fuzzy matching)
        seq_similarity = SequenceMatcher(None, search_clean, text_clean).ratio()
        
        # Bonus si les mots correspondent partiellement
        search_words = search_clean.split()
        text_words = text_clean.split()
        
        word_matches = 0
        for search_word in search_words:
            for text_word in text_words:
                if search_word in text_word or text_word in search_word:
                    word_matches += 1
                    break
        
        if search_words:
            word_score = word_matches / len(search_words) * 0.3
            seq_similarity += word_score
        
        return min(seq_similarity, 1.0)
    
    def _create_loading_embed(self, search_term: str) -> discord.Embed:
        """Crée un embed de chargement."""
        embed = discord.Embed(
            title="🔍 Recherche en cours...",
            description=f"Recherche d'objets correspondant à : **{search_term}**",
            color=0xf39c12  # Orange
        )
        embed.set_footer(text="Fouille dans les grimoires...")
        return embed
    
    def _create_no_results_embed(self, search_term: str) -> discord.Embed:
        """Crée un embed quand aucun résultat n'est trouvé."""
        embed = discord.Embed(
            title="🔍 Aucun résultat trouvé",
            description=f"Aucun objet ne correspond à votre recherche : **{search_term}**",
            color=0xe74c3c  # Rouge
        )
        
        embed.add_field(
            name="💡 Suggestions",
            value="• Vérifiez l'orthographe\n"
                  "• Essayez des termes plus courts\n"
                  "• Utilisez des synonymes\n"
                  "• Essayez le nom en anglais",
            inline=False
        )
        
        embed.set_footer(text="Les objets légendaires sont parfois difficiles à trouver...")
        return embed
    
    def _create_results_embed(self, results: List[Tuple[Dict[str, str], float, int]], search_term: str) -> discord.Embed:
        """Crée l'embed avec les résultats de recherche."""
        embed = discord.Embed(
            title=f"🔍 Résultats de recherche : {search_term}",
            description=f"**{len(results)} objet(s) trouvé(s)**",
            color=0x2ecc71  # Vert
        )
        
        for i, (item, score, original_index) in enumerate(results, 1):
            # Validation des données de l'objet
            validated_item = self.item_selector.validate_item_data(item)
            
            name = self._format_result_name(validated_item, i, score)
            details = self._format_result_details(validated_item, original_index)
            
            # Limiter la taille du champ si nécessaire
            if len(details) > 1024:
                details = details[:1000] + "\n\n*[Détails tronqués]*"
            
            embed.add_field(
                name=name,
                value=details,
                inline=False
            )
        
        embed.set_footer(text=f"Recherche effectuée sur {search_term} • Objets triés par pertinence")
        return embed
    
    def _format_result_name(self, item: Dict[str, str], rank: int, score: float) -> str:
        """Formate le nom d'un résultat avec son rang."""
        name = item.get("nom_display", "Objet mystérieux")
        rarity = item.get("rarity_display", "")
        
        # Emoji de rareté
        emoji_map = {
            'commun': '⚪',
            'peu commun': '🟢',
            'rare': '🔵',
            'très rare': '🟣',
            'légendaire': '🟡'
        }
        
        rarity_lower = rarity.lower().strip()
        emoji = emoji_map.get(rarity_lower, '✨')
        
        # Indicateur de pertinence
        relevance = "🎯" if score >= 0.8 else "🔍" if score >= 0.6 else "🔎"
        
        return f"{relevance} {emoji} #{rank} • {name}"
    
    def _format_result_details(self, item: Dict[str, str], original_index: int) -> str:
        """Formate les détails d'un résultat de recherche."""
        details = []
        
        # Noms (français et anglais si différents)
        nom_fr = item.get("Nom de l'objet", "")
        nom_en = item.get("Nom en VO", "")
        
        if nom_fr and nom_en and nom_fr.lower() != nom_en.lower():
            details.append(f"**Nom FR:** {nom_fr}")
            details.append(f"**Nom EN:** {nom_en}")
        elif nom_fr:
            details.append(f"**Nom:** {nom_fr}")
        elif nom_en:
            details.append(f"**Nom:** {nom_en}")
        
        # Rareté et type
        rarity = item.get("rarity_display", "")
        if rarity:
            details.append(f"**Rareté:** {rarity}")
        
        type_obj = item.get("Type", "")
        if type_obj:
            formatted_type = type_obj.replace("_", " ").title()
            details.append(f"**Type:** {formatted_type}")
        
        # Lien magique
        lien_display = item.get("lien_display", "")
        if lien_display:
            lien_emoji = "🔗" if lien_display.lower() == "oui" else "❌"
            details.append(f"**Lien magique:** {lien_emoji} {lien_display}")
        
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
    
    def _generate_sheets_link(self, item: Dict[str, str], original_index: int = None) -> str:
        """Génère un lien direct vers Google Sheets."""
        try:
            config = get_config()
            sheet_id = config['google_sheets']['sheet_id']
            sheet_gid = config['google_sheets'].get('sheet_gid', '0')
            
            if not sheet_id:
                return ""
            
            # Lien direct vers la ligne si on a l'index
            if original_index is not None:
                row_number = original_index + 2  # +2 pour header et index 0
                return f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit?gid={sheet_gid}#gid={sheet_gid}&range=A{row_number}"
            
            # Sinon, lien vers la feuille
            return f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit?gid={sheet_gid}#gid={sheet_gid}"
        
        except Exception as e:
            logger.debug(f"Erreur génération lien Google Sheets: {e}")
            return ""
    
    def _create_error_embed(self, title: str, description: str) -> discord.Embed:
        """Crée un embed d'erreur."""
        embed = discord.Embed(
            title=f"❌ {title}",
            description=description,
            color=0xe74c3c  # Rouge
        )
        
        embed.add_field(
            name="Solutions",
            value="• Vérifiez votre connexion internet\n"
                  "• Réessayez dans quelques minutes\n"
                  "• Contactez un administrateur si le problème persiste",
            inline=False
        )
        
        embed.set_footer(text="Service temporairement indisponible")
        return embed