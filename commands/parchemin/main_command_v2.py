# commands/parchemin/main_command_v2.py
"""
Commande principale pour la génération de parchemins de sorts.
Structure inspirée de boutique/main_command_v2.py
MODIFIÉE: Support du paramètre format_affichage (tableau ou classique)
"""

import discord
from discord import app_commands
import logging
import random
from typing import Optional, List, Tuple

from ..base import BaseCommand
from .google_sheets_client import GoogleSheetsClient
from .spell_selector_v2 import SpellSelectorV2
from .response_builder_v2 import ParcheminResponseBuilderV2
from .config_v2 import get_config

logger = logging.getLogger(__name__)

class ParcheminCommandV2(BaseCommand):
    """
    Commande Discord pour la génération de parchemins de sorts.
    Équivalent de BoutiqueCommandV2 pour les sorts.
    """
    
    def __init__(self, bot):
        """
        Initialise la commande parchemin.
        Même structure que BoutiqueCommandV2.__init__
        
        Args:
            bot: Instance du bot Discord
        """
        super().__init__(bot)
        
        # Configuration depuis les variables d'environnement (même logique que boutique)
        config = get_config()
        google_config = config['google_sheets']
        selection_config = config['spell_selection']
        
        self.sheet_id = google_config['sheet_id']
        self.sheet_name = google_config['sheet_name']
        self.sheet_gid = google_config['sheet_gid']
        self.excluded_levels = selection_config['excluded_levels']
        self.min_items = selection_config['min_items']
        self.max_items = selection_config['max_items']
        
        # Log de debug pour la configuration (même logique que boutique)
        logger.info(f"Configuration parchemin - Sheet: {self.sheet_name}")
        logger.info(f"Configuration parchemin - GID: {self.sheet_gid}")
        logger.info(f"Configuration parchemin - Niveaux exclus: {self.excluded_levels}")
        logger.info(f"Configuration parchemin - Items: {self.min_items}-{self.max_items}")
        
        # Composants adaptés pour les sorts (même structure que boutique)
        self.sheets_client = GoogleSheetsClient(self.sheet_id)
        self.spell_selector = SpellSelectorV2(self.excluded_levels)
        self.response_builder = ParcheminResponseBuilderV2()
        
        # Cache des sorts (équivalent du cache d'items dans boutique)
        self._spells_cache = None
        self._cache_loaded = False
    
    @property
    def name(self) -> str:
        """Nom de la commande."""
        return "parchemin"
    
    @property
    def description(self) -> str:
        """Description de la commande."""
        return "Génère une sélection aléatoire de parchemins de sorts depuis Google Sheets"
    
    def register(self, tree: app_commands.CommandTree):
        """
        Enregistre la commande dans l'arbre des commandes Discord.
        Même structure que boutique/register mais avec filtres spécifiques aux sorts.
        """
        
        @tree.command(name=self.name, description=self.description)
        @app_commands.describe(
            nombre_parchemins="Nombre de parchemins à afficher (entre 1 et 15, aléatoire par défaut)",
            public="Afficher les parchemins publiquement (visible par tous) - défaut: non",
            niveau="Niveau de sort spécifique (0-9) ou plage (ex: 1-3)",
            ecole="École de magie spécifique",
            classe="Classe de personnage spécifique",
            rituel="Filtrer par sorts rituels",
            format_affichage="Format d'affichage: 'tableau' (compact) ou 'classique' (détaillé) - défaut: classique"
        )
        @app_commands.choices(
            ecole=[
                app_commands.Choice(name="Abjuration", value="abjuration"),
                app_commands.Choice(name="Conjuration", value="conjuration"),
                app_commands.Choice(name="Divination", value="divination"),
                app_commands.Choice(name="Enchantment", value="enchantment"),
                app_commands.Choice(name="Evocation", value="evocation"),
                app_commands.Choice(name="Illusion", value="illusion"),
                app_commands.Choice(name="Necromancy", value="necromancy"),
                app_commands.Choice(name="Transmutation", value="transmutation")
            ],
            classe=[
                app_commands.Choice(name="Artificer", value="artificer"),
                app_commands.Choice(name="Bard", value="bard"),
                app_commands.Choice(name="Cleric", value="cleric"),
                app_commands.Choice(name="Druid", value="druid"),
                app_commands.Choice(name="Paladin", value="paladin"),
                app_commands.Choice(name="Ranger", value="ranger"),
                app_commands.Choice(name="Sorcerer", value="sorcerer"),
                app_commands.Choice(name="Warlock", value="warlock"),
                app_commands.Choice(name="Wizard", value="wizard")
            ],
            format_affichage=[
                app_commands.Choice(name="📊 Tableau (compact)", value="tableau"),
                app_commands.Choice(name="📄 Classique (détaillé)", value="classique"),
            ]
        )
        async def parchemin_v2_command(
            interaction: discord.Interaction,
            nombre_parchemins: Optional[int] = None,
            public: Optional[bool] = False,
            niveau: Optional[str] = None,
            ecole: Optional[str] = None,
            classe: Optional[str] = None,
            rituel: Optional[bool] = None,
            format_affichage: Optional[str] = "classique"
        ):
            await self.callback(interaction, nombre_parchemins, public, niveau, ecole, classe, rituel, format_affichage)
    
    async def callback(self, interaction: discord.Interaction, nombre_parchemins: Optional[int] = None, 
                      public: Optional[bool] = False, niveau: Optional[str] = None,
                      ecole: Optional[str] = None, classe: Optional[str] = None, 
                      rituel: Optional[bool] = None, format_affichage: Optional[str] = "classique"):
        """
        Traite la commande parchemin.
        Même structure que boutique/callback mais adapté aux sorts.
        
        Args:
            interaction: Interaction Discord
            nombre_parchemins: Nombre de parchemins à afficher (optionnel)
            public: Si True, le message sera visible par tous, sinon temporaire (défaut: False)
            niveau: Niveau spécifique ou plage de niveaux (optionnel)
            ecole: École de magie spécifique (optionnel)
            classe: Classe de personnage spécifique (optionnel)
            rituel: Filtrer par sorts rituels (optionnel)
            format_affichage: Format d'affichage - "tableau" ou "classique" (défaut: classique)
        """
        try:
            # Déterminer si le message doit être temporaire ou public (même logique que boutique)
            is_ephemeral = not public
            
            # Validation du nombre de parchemins (même logique que boutique)
            if nombre_parchemins is not None:
                if nombre_parchemins < self.min_items or nombre_parchemins > self.max_items:
                    await interaction.response.send_message(
                        f"❌ Le nombre de parchemins doit être entre {self.min_items} et {self.max_items}.",
                        ephemeral=True
                    )
                    return
                target_count = nombre_parchemins
            else:
                # Générer un nombre aléatoire (même logique que boutique)
                target_count = random.randint(self.min_items, min(self.max_items, 8))
            
            # Parser le niveau (nouveau pour parchemin - pas dans boutique)
            level_range = self._parse_level_range(niveau)
            if niveau and not level_range:
                await interaction.response.send_message(
                    "❌ Format de niveau invalide. Utilisez un nombre (ex: 3) ou une plage (ex: 1-3).",
                    ephemeral=True
                )
                return
            
            # Réponse immédiate avec embed de chargement (même logique que boutique)
            loading_embed = self.response_builder.create_loading_embed()
            await interaction.response.send_message(embed=loading_embed, ephemeral=is_ephemeral)
            
            # Charger les sorts si nécessaire (équivalent du cache d'items)
            if not self._cache_loaded:
                await self._load_spells_cache()
            
            if not self._spells_cache:
                error_embed = self.response_builder.create_error_embed(
                    "Impossible de charger les données de sorts depuis Google Sheets.",
                    "Vérifiez que le Google Sheets est accessible et public."
                )
                await interaction.edit_original_response(embed=error_embed)
                return
            
            # Filtrer les sorts (même logique que boutique mais adapté aux sorts)
            filtered_spells, filtered_indices = self.spell_selector.filter_spells(
                self._spells_cache,
                level_range=level_range,
                school=ecole,
                class_name=classe,
                ritual=rituel
            )
            
            # Vérifier qu'il reste des sorts après filtrage
            if not filtered_spells:
                error_embed = self.response_builder.create_error_embed(
                    "Aucun sort trouvé avec ces critères.",
                    "Essayez de modifier les filtres pour obtenir des résultats."
                )
                await interaction.edit_original_response(embed=error_embed)
                return
            
            # Ajuster le nombre cible si pas assez de sorts (même logique que boutique)
            if len(filtered_spells) < target_count:
                logger.warning(f"Seulement {len(filtered_spells)} sorts disponibles, ajustement du nombre cible")
                target_count = len(filtered_spells)
            
            if target_count == 0:
                error_embed = self.response_builder.create_error_embed(
                    "Aucun sort disponible après filtrage.",
                    "Aucun sort trouvé avec les critères demandés."
                )
                await interaction.edit_original_response(embed=error_embed)
                return
            
            # Sélection aléatoire de sorts avec leurs indices (même logique que boutique)
            try:
                selected_spells, selected_indices = self.spell_selector.select_random_spells(
                    (filtered_spells, filtered_indices), 
                    min_count=target_count, 
                    max_count=target_count
                )
                
                if not selected_spells:
                    raise ValueError("Aucun sort sélectionné après le processus de sélection")
                    
            except Exception as e:
                logger.error(f"Erreur lors de la sélection des sorts: {e}")
                error_embed = self.response_builder.create_error_embed(
                    "Erreur lors de la sélection des sorts.",
                    str(e)
                )
                await interaction.edit_original_response(embed=error_embed)
                return
            
            # Validation des sorts sélectionnés (même logique que boutique)
            validated_spells = [
                self.spell_selector.validate_spell_data(spell) 
                for spell in selected_spells
            ]
            
            # Statistiques (même structure que boutique)
            stats = {
                'total_spells': len(self._spells_cache),
                'filtered_spells': len(filtered_spells),
                'selected_spells': len(validated_spells),
                'target_count': target_count
            }
            
            # Préparer les filtres pour l'affichage
            filters = {
                'level_range': level_range,
                'school_filter': ecole,
                'class_filter': classe,
                'ritual_filter': rituel
            }
            
            # Création de la réponse finale avec le format spécifié
            parchemin_embed = self.response_builder.create_parchemin_embed(
                validated_spells, 
                stats,
                selected_indices,
                filters,
                format_type=format_affichage
            )
            
            # Ajouter une indication du mode d'affichage si public (même logique que boutique)
            if public:
                current_footer = parchemin_embed.footer.text if parchemin_embed.footer else ""
                parchemin_embed.set_footer(text=f"{current_footer} • Message public partagé par {interaction.user.display_name}")
            
            # Mise à jour du message avec l'embed principal
            await interaction.edit_original_response(embed=parchemin_embed)
            
            # Log de l'utilisation réussie (même logique que boutique)
            logger.info(f"Commande parchemin exécutée par {interaction.user.name} - "
                       f"{len(selected_spells)} sorts - Format: {format_affichage} - "
                       f"Filtres: niveau={niveau}, école={ecole}, classe={classe}, rituel={rituel}")
            
        except Exception as e:
            logger.error(f"Erreur dans la commande parchemin: {e}")
            try:
                if not interaction.response.is_done():
                    await interaction.response.send_message(
                        "❌ Une erreur s'est produite lors de la génération des parchemins.",
                        ephemeral=True
                    )
                else:
                    await interaction.edit_original_response(
                        embed=self.response_builder.create_error_embed(
                            "Une erreur s'est produite lors de la génération des parchemins.",
                            str(e)
                        )
                    )
            except:
                pass
    
    async def _load_spells_cache(self):
        """
        Charge les sorts dans le cache depuis Google Sheets.
        Équivalent du chargement du cache d'items dans boutique.
        """
        try:
            logger.info("Chargement des sorts depuis Google Sheets...")
            
            # Utiliser le GID si disponible, sinon le nom de la feuille (même logique que boutique)
            if self.sheet_gid and self.sheet_gid != '0':
                self._spells_cache = await self.sheets_client.fetch_sheet_data(gid=self.sheet_gid)
            else:
                self._spells_cache = await self.sheets_client.fetch_sheet_data(sheet_name=self.sheet_name)
            
            self._cache_loaded = True
            
            logger.info(f"Cache des sorts chargé avec {len(self._spells_cache)} sorts")
            
        except Exception as e:
            logger.error(f"Erreur lors du chargement du cache des sorts: {e}")
            self._spells_cache = []
            self._cache_loaded = False
    
    def _parse_level_range(self, niveau_str: Optional[str]) -> Optional[Tuple[int, int]]:
        """
        Parse une chaîne de niveau en plage.
        Nouveau pour parchemin (les objets n'ont pas de niveaux dans boutique).
        
        Args:
            niveau_str: Chaîne comme "3" ou "1-3"
            
        Returns:
            Tuple (min_level, max_level) ou None si invalide
        """
        if not niveau_str:
            return None
            
        try:
            if '-' in niveau_str:
                parts = niveau_str.split('-')
                if len(parts) == 2:
                    min_level = int(parts[0])
                    max_level = int(parts[1])
                    if 0 <= min_level <= max_level <= 9:
                        return (min_level, max_level)
            else:
                level = int(niveau_str)
                if 0 <= level <= 9:
                    return (level, level)
        except ValueError:
            pass
            
        return None
    
    async def reload_cache(self):
        """
        Recharge le cache des sorts. Utile pour les mises à jour.
        Même fonction que dans boutique.
        """
        self._cache_loaded = False
        await self._load_spells_cache()
    
    def get_cache_stats(self) -> dict:
        """
        Retourne des statistiques sur le cache actuel.
        Même fonction que dans boutique.
        
        Returns:
            dict: Statistiques du cache
        """
        if not self._spells_cache:
            return {'loaded': False, 'total_spells': 0}
        
        return self.spell_selector.get_spell_stats(self._spells_cache)