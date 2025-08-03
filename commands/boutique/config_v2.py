# commands/boutique/config_v2.py
"""
Configuration pour le fichier OM_PRICE.csv - Structure différente
"""

import os
from typing import List, Dict, Any

# Tentative de chargement automatique du fichier .env avec python-dotenv
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Fichier .env chargé avec python-dotenv")
except ImportError:
    print("ℹ️ Aucun fichier .env trouvé, utilisation des valeurs par défaut")

# Configuration Google Sheets pour OM_PRICE
GOOGLE_SHEETS_CONFIG = {
    'sheet_id': os.getenv('BOUTIQUE_SHEET_ID', '1DsvQ5GmwBH-jXo3vHR-XqkpQjkyRHi5BaZ0gqkcrvI8'),
    'sheet_name': os.getenv('BOUTIQUE_SHEET_NAME', 'OM_PRICE'),  # Nouveau nom de feuille
    'sheet_gid': os.getenv('BOUTIQUE_SHEET_GID', '0'),  # GID différent
    'base_url': 'https://docs.google.com/spreadsheets/d'
}

# Configuration de sélection avec les nouvelles raretés
ITEM_SELECTION_CONFIG = {
    'min_items': int(os.getenv('BOUTIQUE_MIN_ITEMS', '3')),
    'max_items': int(os.getenv('BOUTIQUE_MAX_ITEMS', '8')),
    # Nouvelles raretés à exclure (format différent)
    'excluded_rarities': os.getenv('BOUTIQUE_EXCLUDED_RARITIES', '3-VERY RARE,4-LEGENDARY').split(','),
    'rarity_column': os.getenv('BOUTIQUE_RARITY_COLUMN', 'RARETER')  # Nouvelle colonne
}

# Mapping des colonnes pour OM_PRICE
COLUMNS_CONFIG = {
    'nom_anglais': os.getenv('BOUTIQUE_COL_NOM_ANGLAIS', 'Name'),
    'nom_francais': os.getenv('BOUTIQUE_COL_NOM_FRANCAIS', 'NameVF'),
    'type': os.getenv('BOUTIQUE_COL_TYPE', 'Type'),
    'rarity': os.getenv('BOUTIQUE_COL_RARITY', 'RARETER'),
    'lien_magique': os.getenv('BOUTIQUE_COL_LIEN', 'Lien'),
    'source': os.getenv('BOUTIQUE_COL_SOURCE', 'Source'),
    'price_median': os.getenv('BOUTIQUE_COL_PRICE_MEDIAN', 'MEDIANNE'),
    'price_costf': os.getenv('BOUTIQUE_COL_PRICE_COSTF', 'CostF'),
    'price_magic_items': os.getenv('BOUTIQUE_COL_PRICE_MAGIC', 'Magic Item Prices.Price'),
    'price_dungeonsport': os.getenv('BOUTIQUE_COL_PRICE_DUNGEON', 'DUNGEONSPORT.Cost'),
    'grimoire_name': os.getenv('BOUTIQUE_COL_GRIMOIRE', 'GRIMOIRE_NAME')
}

# Configuration Discord (identique)
DISCORD_CONFIG = {
    'max_field_length': int(os.getenv('BOUTIQUE_MAX_FIELD_LENGTH', '1024')),
    'max_embed_length': int(os.getenv('BOUTIQUE_MAX_EMBED_LENGTH', '6000')),
    'colors': {
        'success': int(os.getenv('BOUTIQUE_COLOR_SUCCESS', '0x2ecc71'), 16),
        'error': int(os.getenv('BOUTIQUE_COLOR_ERROR', '0xe74c3c'), 16),
        'warning': int(os.getenv('BOUTIQUE_COLOR_WARNING', '0xf39c12'), 16),
        'info': int(os.getenv('BOUTIQUE_COLOR_INFO', '0x3498db'), 16),
        'magic': int(os.getenv('BOUTIQUE_COLOR_MAGIC', '0x9b59b6'), 16)
    }
}

# Emojis par rareté (adaptés au nouveau format)
RARITY_EMOJIS = {
    '0-commun': '⚪',
    '1-uncommun': '🟢',
    '2-rare': '🔵',
    '3-very rare': '🟣',
    '4-legendary': '🟡',
    'default': '✨'
}

# Emojis pour le lien magique (Y/N au lieu de Oui/Non)
LIEN_MAGIQUE_EMOJIS = {
    'y': '🔗',
    'n': '❌',
    'default': '🔮'
}

# Messages adaptés
BOUTIQUE_MESSAGES = {
    'title': os.getenv('BOUTIQUE_MSG_TITLE', '🏪 Boutique Magique - Objets Disponibles'),
    'loading_title': os.getenv('BOUTIQUE_MSG_LOADING_TITLE', '🔄 Préparation de la Boutique...'),
    'loading_description': os.getenv('BOUTIQUE_MSG_LOADING_DESC', 'Le marchand sélectionne ses meilleurs objets magiques...'),
    'error_title': os.getenv('BOUTIQUE_MSG_ERROR_TITLE', '❌ Erreur - Boutique Indisponible'),
    'footer_base': os.getenv('BOUTIQUE_MSG_FOOTER_BASE', 'Boutique magique de Faerûn'),
    'footer_loading': os.getenv('BOUTIQUE_MSG_FOOTER_LOADING', 'Veuillez patienter quelques instants'),
    'footer_error': os.getenv('BOUTIQUE_MSG_FOOTER_ERROR', 'Boutique temporairement fermée')
}

# Valeurs par défaut adaptées
DEFAULT_VALUES = {
    'item_name': os.getenv('BOUTIQUE_DEFAULT_ITEM_NAME', 'Objet mystérieux'),
    'rarity': os.getenv('BOUTIQUE_DEFAULT_RARITY', '0-COMMUN'),
    'price': os.getenv('BOUTIQUE_DEFAULT_PRICE', 'Non spécifié'),
    'type': os.getenv('BOUTIQUE_DEFAULT_TYPE', 'Objet magique'),
    'lien': os.getenv('BOUTIQUE_DEFAULT_LIEN', 'N')
}

# Configuration de logging
LOGGING_CONFIG = {
    'level': os.getenv('BOUTIQUE_LOG_LEVEL', 'INFO'),
    'format': os.getenv('BOUTIQUE_LOG_FORMAT', '[%(asctime)s] [BOUTIQUE] %(levelname)s: %(message)s')
}

def get_config(section: str = None) -> Dict[str, Any]:
    """Récupère une section de configuration ou toute la configuration."""
    all_config = {
        'google_sheets': GOOGLE_SHEETS_CONFIG,
        'item_selection': ITEM_SELECTION_CONFIG,
        'columns': COLUMNS_CONFIG,
        'discord': DISCORD_CONFIG,
        'rarity_emojis': RARITY_EMOJIS,
        'lien_magique_emojis': LIEN_MAGIQUE_EMOJIS,
        'messages': BOUTIQUE_MESSAGES,
        'defaults': DEFAULT_VALUES,
        'logging': LOGGING_CONFIG
    }
    
    if section:
        return all_config.get(section, {})
    
    return all_config

def validate_config() -> bool:
    """Valide la configuration actuelle."""
    try:
        assert GOOGLE_SHEETS_CONFIG['sheet_id'], "Sheet ID manquant"
        assert GOOGLE_SHEETS_CONFIG['sheet_name'], "Nom de feuille manquant"
        assert ITEM_SELECTION_CONFIG['min_items'] > 0, "min_items doit être > 0"
        assert ITEM_SELECTION_CONFIG['max_items'] >= ITEM_SELECTION_CONFIG['min_items'], "max_items doit être >= min_items"
        
        return True
    except AssertionError as e:
        print(f"Erreur de configuration: {e}")
        return False

# Fonction pour convertir les raretés
def normalize_rarity_name(rarity: str) -> str:
    """
    Convertit le format de rareté OM_PRICE vers un format lisible.
    
    Args:
        rarity: Rareté au format "X-NAME"
        
    Returns:
        str: Rareté lisible
    """
    rarity_map = {
        '0-COMMUN': 'Commun',
        '1-UNCOMMUN': 'Peu commun',
        '2-RARE': 'Rare',
        '3-VERY RARE': 'Très rare',
        '4-LEGENDARY': 'Légendaire'
    }
    
    return rarity_map.get(rarity, rarity)

def normalize_lien_magique(lien: str) -> str:
    """
    Convertit Y/N en Oui/Non.
    
    Args:
        lien: Lien au format Y/N
        
    Returns:
        str: Lien lisible
    """
    lien_map = {
        'Y': 'Oui',
        'N': 'Non'
    }
    
    return lien_map.get(lien, lien)

if __name__ == "__main__":
    print("🔧 Configuration du module boutique - Version OM_PRICE")
    print("=" * 60)
    
    if validate_config():
        print("✅ Configuration valide")
        config = get_config()
        print(f"\n📋 Configuration actuelle:")
        print(f"   • Sheet ID: {config['google_sheets']['sheet_id']}")
        print(f"   • Sheet Name: {config['google_sheets']['sheet_name']}")
        print(f"   • Min/Max items: {config['item_selection']['min_items']}-{config['item_selection']['max_items']}")
        print(f"   • Raretés exclues: {', '.join(config['item_selection']['excluded_rarities'])}")
        
        # Test des fonctions de conversion
        print(f"\n🔄 Test des conversions:")
        print(f"   • '2-RARE' -> '{normalize_rarity_name('2-RARE')}'")
        print(f"   • 'Y' -> '{normalize_lien_magique('Y')}'")
        
    else:
        print("❌ Configuration invalide")