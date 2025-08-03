super().__init__(bot)
        # commands/boutique/main_command.py
"""
Commande principale pour la boutique magique.
"""

import discord
from discord import app_commands
import logging
import random
from typing import Optional

from ..base import BaseCommand
from .google_sheets_client import GoogleSheetsClient
from .item_selector import ItemSelector
from .response_builder import BoutiqueResponseBuilder
from .config import get_config

logger = logging.getLogger(__name__)

class BoutiqueCommand(BaseCommand):
    """
    Commande Discord pour la boutique magique aléatoire.
    Génère une sélection d'objets magiques depuis un Google Sheets.
    """
    
    def __init__(self, bot):
        """
        Initialise la commande boutique.
        
        Args:
            bot: Instance du bot Discord
        """
        super().__init__(bot)
        
        # Configuration
        self.sheet_id = '1DsvQ5GmwBH-jXo3vHR-XqkpQjkyRHi5BaZ0gqkcrvI8'
        self.sheet_name = 'Objets Magique'
        self.excluded_rarities = ['Très rare', 'Légendaire', 'Artefact']
        self.min_items = 3
        self.max_items = 8
        
        # Log de debug pour la configuration
        logger.info(f"Configuration boutique - Raretés exclues: {self.excluded_rarities}")
        
        # Composants
        self.sheets_client = GoogleSheetsClient(self.sheet_id)
        self.item_selector = ItemSelector(self.excluded_rarities)
        self.response_builder = BoutiqueResponseBuilder()
    
    @property
    def name(self) -> str:
        """Nom de la commande."""
        return "boutique"
    
    @property
    def description(self) -> str:
        """Description de la commande."""
        return "Génère une sélection aléatoire d'objets magiques depuis la boutique"
    
    def register(self, tree: app_commands.CommandTree):
        """Enregistre la commande dans l'arbre des commandes Discord."""
        
        @tree.command(name=self.name, description=self.description)
        @app_commands.describe(
            nombre_objets="Nombre d'objets à afficher (entre 3 et 8, aléatoire par défaut)"
        )
        async def boutique_command(
            interaction: discord.Interaction,
            nombre_objets: Optional[int] = None
        ):
            await self.callback(interaction, nombre_objets)
    
    async def callback(self, interaction: discord.Interaction, nombre_objets: Optional[int] = None):
        """
        Traite la commande boutique.
        
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
            
            # Réponse immédiate avec embed de chargement
            loading_embed = self.response_builder.create_loading_embed()
            await interaction.response.send_message(embed=loading_embed)
            
            # Récupération des données depuis Google Sheets
            logger.info(f"Récupération des objets depuis la feuille '{self.sheet_name}'")
            raw_items = await self.sheets_client.fetch_sheet_data(self.sheet_name)
            
            if not raw_items:
                error_embed = self.response_builder.create_error_embed(
                    "Aucun objet trouvé dans la base de données.",
                    f"La feuille '{self.sheet_name}' semble être vide."
                )
                await interaction.edit_original_response(embed=error_embed)
                return
            
            logger.info(f"Récupération réussie: {len(raw_items)} objets trouvés")
            
            # Filtrage par rareté
            filtered_items = self.item_selector.filter_items_by_rarity(raw_items, 'Rareté')
            
            if not filtered_items:
                error_embed = self.response_builder.create_error_embed(
                    "Aucun objet disponible après filtrage.",
                    f"Tous les objets ont des raretés exclues: {', '.join(self.excluded_rarities)}"
                )
                await interaction.edit_original_response(embed=error_embed)
                return
            
            logger.info(f"Filtrage terminé: {len(filtered_items)} objets disponibles")
            
            # Sélection aléatoire
            try:
                selected_items = self.item_selector.select_random_items(
                    filtered_items, 
                    min_count=target_count, 
                    max_count=target_count
                )
            except ValueError as e:
                error_embed = self.response_builder.create_error_embed(
                    "Erreur lors de la sélection des objets.",
                    str(e)
                )
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
            
            # Création de la réponse finale
            boutique_embed = self.response_builder.create_boutique_embed(
                validated_items, 
                stats
            )
            
            # Mise à jour de la réponse
            await interaction.edit_original_response(embed=boutique_embed)
            
            logger.info(f"Boutique générée avec succès: {len(validated_items)} objets affichés")
            
        except Exception as e:
            logger.error(f"Erreur dans la commande boutique: {e}", exc_info=True)
            
            # Gestion d'erreur robuste
            try:
                error_embed = self.response_builder.create_error_embed(
                    "Une erreur inattendue s'est produite.",
                    f"Erreur technique: {str(e)[:200]}..."
                )
                
                # Vérifier si on peut encore répondre
                if not interaction.response.is_done():
                    await interaction.response.send_message(embed=error_embed, ephemeral=True)
                else:
                    await interaction.edit_original_response(embed=error_embed)
                    
            except Exception as fallback_error:
                logger.error(f"Erreur lors de l'envoi du message d'erreur: {fallback_error}")
                
                # Dernier recours: message texte simple
                try:
                    if not interaction.response.is_done():
                        await interaction.response.send_message(
                            "❌ Erreur: Impossible d'accéder à la boutique magique pour le moment.",
                            ephemeral=True
                        )
                    else:
                        await interaction.edit_original_response(
                            content="❌ Erreur: Impossible d'accéder à la boutique magique pour le moment.",
                            embed=None
                        )
                except:
                    logger.error("Impossible d'envoyer une réponse d'erreur à l'utilisateur")
    
    async def test_connection(self) -> bool:
        """
        Test la connexion au Google Sheets.
        
        Returns:
            bool: True si la connexion réussit
        """
        try:
            return await self.sheets_client.test_connection(self.sheet_name)
        except Exception as e:
            logger.error(f"Test de connexion échoué: {e}")
            return False
    
    def get_config_info(self) -> dict:
        """
        Retourne les informations de configuration.
        
        Returns:
            dict: Configuration actuelle
        """
        return {
            'sheet_id': self.sheet_id,
            'sheet_name': self.sheet_name,
            'excluded_rarities': self.excluded_rarities,
            'min_items': self.min_items,
            'max_items': self.max_items,
            'sheet_url': self.sheets_client.get_sheet_url(self.sheet_name)
        }