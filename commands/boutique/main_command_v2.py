# commands/boutique/main_command_v2.py
"""
Commande principale pour la boutique magique adaptée au format OM_PRICE.
"""

import discord
from discord import app_commands
import logging
import random
from typing import Optional

from ..base import BaseCommand
from .google_sheets_client import GoogleSheetsClient
from .item_selector_v2 import ItemSelectorV2
from .response_builder_v2 import BoutiqueResponseBuilderV2
from .config_v2 import get_config

logger = logging.getLogger(__name__)

class BoutiqueCommandV2(BaseCommand):
    """
    Commande Discord pour la boutique magique adaptée au format OM_PRICE.
    """
    
    def __init__(self, bot):
        """
        Initialise la commande boutique pour OM_PRICE.
        
        Args:
            bot: Instance du bot Discord
        """
        super().__init__(bot)
        
        # Configuration depuis les variables d'environnement
        config = get_config()
        google_config = config['google_sheets']
        selection_config = config['item_selection']
        
        self.sheet_id = google_config['sheet_id']
        self.sheet_name = google_config['sheet_name']
        self.excluded_rarities = selection_config['excluded_rarities']
        self.min_items = selection_config['min_items']
        self.max_items = selection_config['max_items']
        
        # Log de debug pour la configuration
        logger.info(f"Configuration boutique OM_PRICE - Sheet: {self.sheet_name}")
        logger.info(f"Configuration boutique OM_PRICE - Raretés exclues: {self.excluded_rarities}")
        logger.info(f"Configuration boutique OM_PRICE - Items: {self.min_items}-{self.max_items}")
        
        # Composants adaptés pour OM_PRICE
        self.sheets_client = GoogleSheetsClient(self.sheet_id)
        self.item_selector = ItemSelectorV2(self.excluded_rarities)
        self.response_builder = BoutiqueResponseBuilderV2()
    
    @property
    def name(self) -> str:
        """Nom de la commande."""
        return "boutique-v2"
    
    @property
    def description(self) -> str:
        """Description de la commande."""
        return "Génère une sélection aléatoire d'objets magiques depuis la boutique OM_PRICE"
    
    def register(self, tree: app_commands.CommandTree):
        """Enregistre la commande dans l'arbre des commandes Discord."""
        
        @tree.command(name=self.name, description=self.description)
        @app_commands.describe(
            nombre_objets="Nombre d'objets à afficher (entre 3 et 8, aléatoire par défaut)"
        )
        async def boutique_v2_command(
            interaction: discord.Interaction,
            nombre_objets: Optional[int] = None
        ):
            await self.callback(interaction, nombre_objets)
    
    async def callback(self, interaction: discord.Interaction, nombre_objets: Optional[int] = None):
        """
        Traite la commande boutique OM_PRICE.
        
        Args:
            interaction: Interaction Discord
            nombre_objets: Nombre d'objets à afficher (optionnel)
        """
        try:
            # Validation du nombre d'objets
            if nombre_objets is not None:
                if nombre_objets < self.min_items or nombre_objets > self.max_items:
                    await interaction.response.send_message(
                        f"❌ Le nombre d'objets doit être entre {self.min_items} et {self.max_items}.",
                        ephemeral=True
                    )
                    return
                target_count = nombre_objets
            else:
                target_count = random.randint(self.min_items, self.max_items)
            
            # MODIFICATION: Réponse immédiate avec embed de chargement TEMPORAIRE
            loading_embed = self.response_builder.create_loading_embed()
            await interaction.response.send_message(embed=loading_embed, ephemeral=True)
            
            # Récupération des données depuis Google Sheets
            logger.info(f"Récupération des objets OM_PRICE depuis la feuille '{self.sheet_name}'")
            raw_items = await self.sheets_client.fetch_sheet_data(self.sheet_name)
            
            if not raw_items:
                error_embed = self.response_builder.create_error_embed(
                    "Aucun objet trouvé dans la base de données OM_PRICE.",
                    f"La feuille '{self.sheet_name}' semble être vide."
                )
                # MODIFICATION: Éditer le message initial temporaire
                await interaction.edit_original_response(embed=error_embed)
                return
            
            logger.info(f"Récupération OM_PRICE réussie: {len(raw_items)} objets trouvés")
            
            # Filtrage par rareté avec conservation des indices originaux
            rarity_column = get_config()['item_selection']['rarity_column']
            filtered_items, filtered_indices = self.item_selector.filter_items_by_rarity(raw_items, rarity_column)
            
            if not filtered_items:
                error_embed = self.response_builder.create_error_embed(
                    "Aucun objet disponible après filtrage OM_PRICE.",
                    f"Tous les objets ont des raretés exclues: {', '.join(self.excluded_rarities)}"
                )
                # MODIFICATION: Éditer le message initial temporaire
                await interaction.edit_original_response(embed=error_embed)
                return
            
            logger.info(f"Filtrage OM_PRICE terminé: {len(filtered_items)} objets disponibles")
            
            config = get_config()
            if config['filtering'].get('require_valid_price', False):
                price_column = config['filtering'].get('price_column', 'Prix Achat')
                
                # Filtrage par prix en préservant les indices originaux
                filtered_items, filtered_indices = self.item_selector.filter_items_by_price(
                    (filtered_items, filtered_indices),
                    price_column
                )
                
                if not filtered_items:
                    error_embed = self.response_builder.create_error_embed(
                        "Aucun objet avec prix valide disponible.",
                        "Tous les objets filtrés n'ont pas de prix spécifié."
                    )
                    # MODIFICATION: Éditer le message initial temporaire
                    await interaction.edit_original_response(embed=error_embed)
                    return
                
                logger.info(f"Filtrage prix terminé: {len(filtered_items)} objets avec prix valide")

            # Sélection aléatoire
            try:
                selected_items, selected_indices = self.item_selector.select_random_items(
                    (filtered_items, filtered_indices), 
                    min_count=target_count, 
                    max_count=target_count
                )
            except ValueError as e:
                error_embed = self.response_builder.create_error_embed(
                    "Erreur lors de la sélection des objets OM_PRICE.",
                    str(e)
                )
                # MODIFICATION: Éditer le message initial temporaire
                await interaction.edit_original_response(embed=error_embed)
                return
            
            # Validation des objets sélectionnés
            validated_items = [
                self.item_selector.validate_item_data(item) 
                for item in selected_items
            ]
            
            # Statistiques
            stats = {
                'total_items': len(raw_items),
                'filtered_items': len(filtered_items),
                'selected_items': len(validated_items),
                'target_count': target_count
            }
            
            # Création de la réponse finale avec les indices pour les liens Google Sheets
            boutique_embed = self.response_builder.create_boutique_embed(
                validated_items, 
                stats,
                selected_indices
            )
            
            # MODIFICATION: Mise à jour du message initial temporaire
            await interaction.edit_original_response(embed=boutique_embed)
            
            logger.info(f"Boutique OM_PRICE générée avec succès: {len(validated_items)} objets affichés")
            
        except Exception as e:
            logger.error(f"Erreur dans la commande boutique OM_PRICE: {e}", exc_info=True)
            
            # Gestion d'erreur robuste
            try:
                error_embed = self.response_builder.create_error_embed(
                    "Une erreur inattendue s'est produite avec OM_PRICE.",
                    f"Erreur technique: {str(e)[:200]}..."
                )
                
                # MODIFICATION: Vérifier si on peut encore répondre avec message temporaire
                if not interaction.response.is_done():
                    await interaction.response.send_message(embed=error_embed, ephemeral=True)
                else:
                    await interaction.edit_original_response(embed=error_embed)
                    
            except Exception as fallback_error:
                logger.error(f"Erreur lors de l'envoi du message d'erreur OM_PRICE: {fallback_error}")
                
                # MODIFICATION: Dernier recours avec message temporaire
                try:
                    if not interaction.response.is_done():
                        await interaction.response.send_message(
                            "❌ Erreur: Impossible d'accéder à la boutique magique OM_PRICE pour le moment.",
                            ephemeral=True
                        )
                    else:
                        await interaction.edit_original_response(
                            content="❌ Erreur: Impossible d'accéder à la boutique magique OM_PRICE pour le moment.",
                            embed=None
                        )
                except:
                    logger.error("Impossible d'envoyer une réponse d'erreur à l'utilisateur")
    
    async def test_connection(self) -> bool:
        """
        Test la connexion au Google Sheets OM_PRICE.
        
        Returns:
            bool: True si la connexion réussit
        """
        try:
            return await self.sheets_client.test_connection(self.sheet_name)
        except Exception as e:
            logger.error(f"Test de connexion OM_PRICE échoué: {e}")
            return False
    
    def get_config_info(self) -> dict:
        """
        Retourne les informations de configuration OM_PRICE.
        
        Returns:
            dict: Configuration actuelle
        """
        return {
            'sheet_id': self.sheet_id,
            'sheet_name': self.sheet_name,
            'excluded_rarities': self.excluded_rarities,
            'min_items': self.min_items,
            'max_items': self.max_items,
            'sheet_url': self.sheets_client.get_sheet_url(self.sheet_name),
            'version': 'OM_PRICE_v2'
        }