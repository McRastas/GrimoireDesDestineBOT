# commands/boutique/__init__.py
"""
Module Boutique - Bot Faerûn

Ce module fournit un système de boutique aléatoire basé sur Google Sheets
pour générer des objets magiques filtrés par rareté.

ARCHITECTURE MODULAIRE:
    - main_command.py           : Commande principale Discord
    - google_sheets_client.py   : Client pour accéder au Google Sheets public
    - item_selector.py          : Sélecteur d'objets aléatoires avec filtres
    - response_builder.py       : Constructeur de réponses Discord
    - __init__.py              : Assemblage et exports du module

UTILISATION:
    from commands.boutique import BoutiqueCommand
    
    command = BoutiqueCommand(bot)
    command.register(bot.tree)

FONCTIONNALITÉS:
    ✅ Accès aux Google Sheets publics (pas de credentials requis)
    ✅ Filtrage par rareté (exclut très rare et légendaire)
    ✅ Sélection aléatoire de 3-8 objets
    ✅ Formatage Discord avec embeds
    ✅ Gestion d'erreurs robuste
"""

from .main_command import BoutiqueCommand
from .google_sheets_client import GoogleSheetsClient
from .item_selector import ItemSelector
from .response_builder import BoutiqueResponseBuilder

# Export principal
__all__ = [
    'BoutiqueCommand',           # Commande principale
    'GoogleSheetsClient',        # Client Google Sheets
    'ItemSelector',              # Sélecteur d'objets
    'BoutiqueResponseBuilder'    # Constructeur de réponses
]

# Métadonnées du module
__version__ = "1.0.0"
__author__ = "Bot Faerûn Team"
__description__ = "Système de boutique aléatoire basé sur Google Sheets"

# Configuration du module
MODULE_CONFIG = {
    'version': __version__,
    'google_sheet_id': '1DsvQ5GmwBH-jXo3vHR-XqkpQjkyRHi5BaZ0gqkcrvI8',
    'sheet_name': 'Objets Magique',
    'rarity_filters': ['très rare', 'légendaire'],  # Raretés à exclure
    'random_count_min': 3,
    'random_count_max': 8,
    'columns': {
        'nom': 'Nom de l\'objet',
        'nom_vo': 'Nom Vo Nom en VO',
        'type': 'Type',
        'rarity': 'Rareté',
        'link': 'Lien',
        'craft_cost': 'Coût de craft',
        'profession': 'Metier',
        'buy_price': 'Prix achat',
        'specs': 'Spécificités',
        'sell_price': 'Prix vente',
        'source': 'Source',
        'effect': 'Effet'
    }
}

def create_command_instance(bot):
    """
    Factory function pour créer une instance de la commande boutique.
    
    Args:
        bot: Instance du bot Discord
        
    Returns:
        BoutiqueCommand: Instance configurée de la commande
    """
    return BoutiqueCommand(bot)

def get_module_info() -> dict:
    """
    Retourne les informations sur le module boutique.
    
    Returns:
        dict: Informations complètes du module
    """
    return MODULE_CONFIG