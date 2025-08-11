# commands/boutique/main_command_v2.py
"""
Commande principale pour la boutique magique adaptée au format OM_PRICE.
"""

import discord
from discord import app_commands
import logging
import random
from typing import Optional, List

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
            nombre_objets="Nombre d'objets à afficher (entre 3 et 8, aléatoire par défaut)",
            public="Afficher la boutique publiquement (visible par tous) - défaut: non",
            format_copiable="Inclure une version markdown copiable - défaut: non"
        )
        async def boutique_v2_command(
            interaction: discord.Interaction,
            nombre_objets: Optional[int] = None,
            public: Optional[bool] = False,
            format_copiable: Optional[bool] = False
        ):
            await self.callback(interaction, nombre_objets, public, format_copiable)
    
    async def callback(self, interaction: discord.Interaction, nombre_objets: Optional[int] = None, public: Optional[bool] = False, format_copiable: Optional[bool] = False):
        """
        Traite la commande boutique OM_PRICE.
        
        Args:
            interaction: Interaction Discord
            nombre_objets: Nombre d'objets à afficher (optionnel)
            public: Si True, le message sera visible par tous, sinon temporaire (défaut: False)
            format_copiable: Si True, inclut une version markdown copiable (défaut: False)
        """
        try:
            # Déterminer si le message doit être temporaire ou public
            is_ephemeral = not public  # Si public=True, ephemeral=False, et vice versa
            
            # Validation du nombre d'objets
            if nombre_objets is not None:
                if nombre_objets < self.min_items or nombre_objets > self.max_items:
                    await interaction.response.send_message(
                        f"❌ Le nombre d'objets doit être entre {self.min_items} et {self.max_items}.",
                        ephemeral=True  # Les messages d'erreur restent toujours temporaires
                    )
                    return
                target_count = nombre_objets
            else:
                target_count = random.randint(self.min_items, self.max_items)
            
            # Réponse immédiate avec embed de chargement
            loading_embed = self.response_builder.create_loading_embed()
            await interaction.response.send_message(embed=loading_embed, ephemeral=is_ephemeral)
            
            # Récupération des données depuis Google Sheets
            logger.info(f"Récupération des objets OM_PRICE depuis la feuille '{self.sheet_name}' (public: {public}, copiable: {format_copiable})")
            raw_items = await self.sheets_client.fetch_sheet_data(self.sheet_name)
            
            if not raw_items:
                error_embed = self.response_builder.create_error_embed(
                    "Aucun objet trouvé dans la base de données OM_PRICE.",
                    f"La feuille '{self.sheet_name}' semble être vide."
                )
                await interaction.edit_original_response(embed=error_embed)
                return
            
            # Filtrage par rareté avec préservation des indices originaux
            rarity_column = get_config()['item_selection']['rarity_column']
            filtered_items, filtered_indices = self.item_selector.filter_items_by_rarity(raw_items, rarity_column)

            if len(filtered_items) < target_count:
                # Ajuster le nombre cible si pas assez d'objets disponibles
                logger.warning(f"Seulement {len(filtered_items)} objets disponibles, ajustement du nombre cible")
                target_count = len(filtered_items)

            if target_count == 0:
                error_embed = self.response_builder.create_error_embed(
                    "Aucun objet disponible après filtrage.",
                    f"Tous les objets sont dans les raretés exclues : {', '.join(self.excluded_rarities)}"
                )
                await interaction.edit_original_response(embed=error_embed)
                return

            # Sélection aléatoire d'objets avec leurs indices
            try:
                selected_items, selected_indices = self.item_selector.select_random_items(
                    (filtered_items, filtered_indices), 
                    min_count=target_count, 
                    max_count=target_count
                )
                            
                if not selected_items:
                    raise ValueError("Aucun objet sélectionné après le processus de sélection")
                    
            except Exception as e:
                logger.error(f"Erreur lors de la sélection des objets: {e}")
                error_embed = self.response_builder.create_error_embed(
                    "Erreur lors de la sélection des objets magiques OM_PRICE.",
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
            
            # Création de la réponse finale avec les indices pour les liens Google Sheets
            boutique_embed = self.response_builder.create_boutique_embed(
                validated_items, 
                stats,
                selected_indices
            )
            
            # Ajouter une indication du mode d'affichage dans le footer si c'est public
            if public:
                current_footer = boutique_embed.footer.text if boutique_embed.footer else ""
                boutique_embed.set_footer(text=f"{current_footer} • Message public partagé par {interaction.user.display_name}")
            
            # Mise à jour du message avec l'embed principal
            await interaction.edit_original_response(embed=boutique_embed)
            
            # === VERSION MARKDOWN COPIABLE (OPTIONNELLE) ===
            
            if format_copiable:
                # Création du contenu markdown copiable
                markdown_content = self.response_builder.create_markdown_output(validated_items, stats)
                
                # Vérifier si le contenu markdown est trop long pour Discord
                if len(markdown_content) > 1900:  # Limite Discord avec marge de sécurité
                    # Diviser en plusieurs parties
                    parts = self._split_markdown_content(markdown_content)
                    
                    # Envoyer les parties markdown
                    for i, part in enumerate(parts):
                        markdown_embed = discord.Embed(
                            title=f"📋 Version Copiable (partie {i+1}/{len(parts)})",
                            description=f"```markdown\n{part}\n```",
                            color=0x3498db
                        )
                        await interaction.followup.send(embed=markdown_embed, ephemeral=is_ephemeral)
                else:
                    # Envoyer la version markdown copiable en un seul message
                    markdown_embed = discord.Embed(
                        title="📋 Version Copiable",
                        description=f"```markdown\n{markdown_content}\n```",
                        color=0x3498db
                    )
                    await interaction.followup.send(embed=markdown_embed, ephemeral=is_ephemeral)
            
            logger.info(f"Boutique OM_PRICE générée avec succès: {len(validated_items)} objets affichés (public: {public}, copiable: {format_copiable})")
            
        except Exception as e:
            logger.error(f"Erreur dans la commande boutique OM_PRICE: {e}", exc_info=True)
            
            # Gestion d'erreur robuste
            try:
                error_embed = self.response_builder.create_error_embed(
                    "Une erreur inattendue s'est produite avec OM_PRICE.",
                    f"Erreur technique: {str(e)[:200]}..."
                )
                
                # Vérifier si on peut encore répondre
                if not interaction.response.is_done():
                    await interaction.response.send_message(embed=error_embed, ephemeral=True)  # Erreurs toujours temporaires
                else:
                    await interaction.edit_original_response(embed=error_embed)
                    
            except Exception as fallback_error:
                logger.error(f"Erreur lors de l'envoi du message d'erreur OM_PRICE: {fallback_error}")
                
                # Dernier recours
                try:
                    if not interaction.response.is_done():
                        await interaction.response.send_message(
                            "❌ Erreur: Impossible d'accéder à la boutique magique OM_PRICE pour le moment.",
                            ephemeral=True  # Erreurs toujours temporaires
                        )
                    else:
                        await interaction.edit_original_response(
                            content="❌ Erreur: Impossible d'accéder à la boutique magique OM_PRICE pour le moment.",
                            embed=None
                        )
                except:
                    logger.error("Impossible d'envoyer une réponse d'erreur à l'utilisateur")

    def _split_markdown_content(self, content: str, max_length: int = 1800) -> List[str]:
        """
        Divise le contenu markdown en parties gérables pour Discord.
        
        Args:
            content: Contenu à diviser
            max_length: Longueur maximale par partie
            
        Returns:
            List[str]: Liste des parties
        """
        if len(content) <= max_length:
            return [content]
        
        parts = []
        lines = content.split('\n')
        current_part = []
        current_length = 0
        
        for line in lines:
            line_length = len(line) + 1  # +1 pour le \n
            
            if current_length + line_length > max_length and current_part:
                # Sauvegarder la partie actuelle
                parts.append('\n'.join(current_part))
                current_part = [line]
                current_length = line_length
            else:
                current_part.append(line)
                current_length += line_length
        
        # Ajouter la dernière partie
        if current_part:
            parts.append('\n'.join(current_part))
        
        return parts

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