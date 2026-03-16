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

# Configuration de sélection mise à jour
ITEM_SELECTION_CONFIG = {
    'min_items': int(os.getenv('BOUTIQUE_MIN_ITEMS', '3')),
    'max_items': int(os.getenv('BOUTIQUE_MAX_ITEMS', '15')),
    'excluded_rarities': os.getenv('BOUTIQUE_EXCLUDED_RARITIES', 'Très rare,Légendaire').split(','),
    'rarity_column': os.getenv('BOUTIQUE_RARITY_COLUMN', 'Rareté')  # TA colonne
}

# Mapping des colonnes selon tes noms
COLUMNS_CONFIG = {
    'nom_francais': os.getenv('BOUTIQUE_COL_NOM_FRANCAIS', 'Nom de l\'objet'),
    'nom_anglais': os.getenv('BOUTIQUE_COL_NOM_ANGLAIS', 'Nom en VO'), 
    'type': os.getenv('BOUTIQUE_COL_TYPE', 'Type'),
    'rarity': os.getenv('BOUTIQUE_COL_RARITY', 'Rareté'),
    'lien_magique': os.getenv('BOUTIQUE_COL_LIEN', 'Lien'),
    'source': os.getenv('BOUTIQUE_COL_SOURCE', 'Source'),
    'price_achat': os.getenv('BOUTIQUE_COL_PRICE_ACHAT', 'Prix Achat'),
    # Autres colonnes de prix si nécessaire
    'price_median': os.getenv('BOUTIQUE_COL_PRICE_MEDIAN', 'Prix Achat'),  # Utilise Prix Achat par défaut
    'price_costf': os.getenv('BOUTIQUE_COL_PRICE_COSTF', 'Prix Achat'),
    'price_magic_items': os.getenv('BOUTIQUE_COL_PRICE_MAGIC', 'Prix Achat'),
    'price_dungeonsport': os.getenv('BOUTIQUE_COL_PRICE_DUNGEON', 'Prix Achat'),
    'grimoire_name': os.getenv('BOUTIQUE_COL_GRIMOIRE', 'Nom de l\'objet'),
    'validate': os.getenv('BOUTIQUE_COL_VALIDATE', 'VALIDATE')
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

# Valeurs considérées comme NA/invalides
NA_VALUES = {
    'strings': os.getenv('BOUTIQUE_NA_VALUES', 'NA,N/A,na,n/a,null,NULL,Null,,').split(','),
    'numbers': ['0', '0.0', '-1']
}

# Configuration de filtrage OM_PRICE
FILTERING_CONFIG = {
    'exclude_na_values': os.getenv('BOUTIQUE_EXCLUDE_NA', 'true').lower() == 'true',
    'critical_columns': ['Nom de l\'objet', 'Nom en VO', 'Rareté', 'Type'],
    'na_values': os.getenv('BOUTIQUE_NA_VALUES', 'NA,N/A,na,n/a,null,NULL,Null,,').split(','),
    'require_valid_name': True,
    'require_valid_rarity': True,
    # ASSUREZ-VOUS QUE C'EST TRUE :
    'require_valid_price': True,  # Pour exclure les objets sans prix
    # CORRIGEZ LE NOM DE LA COLONNE :
    'price_column': 'OM_PRICE',  # Au lieu de 'Prix Achat'
    # Filtre VALIDATE : raretés pour lesquelles les entrées NOK sont exclues
    'validate_column': os.getenv('BOUTIQUE_COL_VALIDATE', 'VALIDATE'),
    'rarities_requiring_validation': ['Rare', 'Très rare']
}
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
        'filtering': FILTERING_CONFIG,
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

# Fonction de normalisation des raretés mise à jour pour tes données
def normalize_rarity_name(rarity: str) -> str:
    """
    Convertit le format de rareté de ta feuille vers un format lisible.
    """
    rarity_map = {
        'Commun': 'Commun',  # ← CORRIGÉ: virgule au lieu de point-virgule
        'Peu commun': 'Peu commun',
        'Rare': 'Rare',
        'Très rare': 'Très rare', 
        'Légendaire': 'Légendaire',
        # Versions alternatives au cas où
        'Common': 'Commun',
        'Uncommon': 'Peu commun',
        'Very Rare': 'Très rare',
        'Legendary': 'Légendaire'
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

def is_na_value(value: str) -> bool:
    """
    Vérifie si une valeur est considérée comme NA.
    
    Args:
        value: Valeur à vérifier
        
    Returns:
        bool: True si la valeur est NA
    """
    if value is None:
        return True
    
    value_str = str(value).strip()
    
    if not value_str:  # Chaîne vide
        return True
    
    # Vérifier les valeurs NA configurées
    na_values = FILTERING_CONFIG['na_values']
    return value_str.upper() in [na.upper() for na in na_values]

def clean_na_value(value: str, default: str = "") -> str:
    """
    Nettoie une valeur NA en la remplaçant par une valeur par défaut.
    
    Args:
        value: Valeur à nettoyer
        default: Valeur par défaut si NA
        
    Returns:
        str: Valeur nettoyée
    """
    if is_na_value(value):
        return default
    
    return str(value).strip()

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
