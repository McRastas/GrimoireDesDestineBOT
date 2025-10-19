# commands/parchemin/config_v2.py
"""
Configuration pour les parchemins de sorts - Structure similaire à boutique/config_v2.py
COMPLÈTEMENT FLEXIBLE - Tous les noms de colonnes sont configurables
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

# Configuration Google Sheets pour les parchemins (comme GOOGLE_SHEETS_CONFIG dans boutique)
GOOGLE_SHEETS_CONFIG = {
    'sheet_id': os.getenv('PARCHEMIN_SHEET_ID', '1DsvQ5GmwBH-jXo3vHR-XqkpQjkyRHi5BaZ0gqkcrvI8'),
    'sheet_name': os.getenv('PARCHEMIN_SHEET_NAME', 'Spells'),
    'sheet_gid': os.getenv('PARCHEMIN_SHEET_GID', '1370110278'),
    'base_url': 'https://docs.google.com/spreadsheets/d'
}

# Configuration de sélection des parchemins (comme ITEM_SELECTION_CONFIG dans boutique)
SPELL_SELECTION_CONFIG = {
    'min_items': int(os.getenv('PARCHEMIN_MIN_ITEMS', '1')),
    'max_items': int(os.getenv('PARCHEMIN_MAX_ITEMS', '15')),
    'excluded_levels': os.getenv('PARCHEMIN_EXCLUDED_LEVELS', '').split(',') if os.getenv('PARCHEMIN_EXCLUDED_LEVELS') else [],
    'level_column': os.getenv('PARCHEMIN_LEVEL_COLUMN', 'Level')
}

# ========================================================================
# MAPPING DES COLONNES - TOUS CONFIGURABLES
# ========================================================================
# Format: 'clé_interne': 'NOM_COLONNE_PAR_DEFAUT'
# Vous pouvez modifier via .env avec PARCHEMIN_COL_XXX=Votre_Nom_Colonne

COLUMNS_CONFIG = {
    # Colonnes essentielles
    'name': os.getenv('PARCHEMIN_COL_NAME', 'Name'),
    'name_vf': os.getenv('PARCHEMIN_COL_NAME_VF', 'NameVF'),
    'level': os.getenv('PARCHEMIN_COL_LEVEL', 'Level'),
    'school': os.getenv('PARCHEMIN_COL_SCHOOL', 'School'),
    'source': os.getenv('PARCHEMIN_COL_SOURCE', 'Source'),
    
    # Colonnes optionnelles
    'ritual': os.getenv('PARCHEMIN_COL_RITUAL', 'RITUEL'),
    'classes': os.getenv('PARCHEMIN_COL_CLASSES', 'CLASSE'),
    
    # Ajoute ici d'autres colonnes selon tes besoins
    # 'description': os.getenv('PARCHEMIN_COL_DESCRIPTION', 'Description'),
    # 'components': os.getenv('PARCHEMIN_COL_COMPONENTS', 'Components'),
    # 'range': os.getenv('PARCHEMIN_COL_RANGE', 'Range'),
}

# Configuration Discord (comme DISCORD_CONFIG dans boutique)
DISCORD_CONFIG = {
    'embed_color_by_level': {
        0: 0x95a5a6,    # Gris pour cantrips
        1: 0x2ecc71,    # Vert pour niveau 1
        2: 0x3498db,    # Bleu pour niveau 2
        3: 0x9b59b6,    # Violet pour niveau 3
        4: 0xf39c12,    # Orange pour niveau 4
        5: 0xe74c3c,    # Rouge pour niveau 5
        6: 0x8e44ad,    # Violet foncé pour niveau 6
        7: 0x1abc9c,    # Turquoise pour niveau 7
        8: 0x34495e,    # Gris foncé pour niveau 8
        9: 0xc0392b,    # Rouge foncé pour niveau 9
    }
}

# Emojis des écoles de magie (pour l'affichage futur)
SCHOOL_EMOJIS = {
    'abjuration': '🛡️',
    'conjuration': '✨',
    'divination': '🔮',
    'enchantment': '💫',
    'evocation': '⚡',
    'illusion': '🌫️',
    'necromancy': '💀',
    'transmutation': '🔄',
}

# Emojis des niveaux (pour l'affichage futur)
LEVEL_EMOJIS = {
    0: '✨',  # Cantrips
    1: '⚡',
    2: '🔥',
    3: '💜',
    4: '🧡',
    5: '❤️',
    6: '💀',
    7: '👑',
    8: '🌟',
    9: '✔️',
}

# Emoji rituel
RITUAL_EMOJIS = {
    True: '🔮',
    False: '',
}

# Messages parchemin
PARCHEMIN_MESSAGES = {
    'loading': "🔄 Préparation des Parchemins...",
    'loading_desc': "Le mage sélectionne ses meilleurs sorts...",
    'no_spells': "Aucun sort trouvé avec ces critères.",
    'error': "Une erreur s'est produite lors de la génération des parchemins.",
}

# Valeurs par défaut
DEFAULT_VALUES = {
    'school': 'Inconnue',
    'source': 'Manuel inconnu',
    'level': 0,
}

# Configuration du filtrage
FILTERING_CONFIG = {
    'na_values': ['NA', 'N/A', '', 'None', 'none', 'NONE'],
    'class_separator': ',',
    'require_valid_price': False,
}

# Configuration logging
LOGGING_CONFIG = {
    'level': os.getenv('LOG_LEVEL', 'INFO'),
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
}

# ========================================================================
# FONCTION PRINCIPALE DE CONFIGURATION
# ========================================================================

def get_config(section: str = None) -> Dict[str, Any]:
    """
    Récupère la configuration.
    Même structure que boutique/config_v2.py
    """
    all_config = {
        'google_sheets': GOOGLE_SHEETS_CONFIG,
        'spell_selection': SPELL_SELECTION_CONFIG,
        'columns': COLUMNS_CONFIG,
        'discord': DISCORD_CONFIG,
        'school_emojis': SCHOOL_EMOJIS,
        'level_emojis': LEVEL_EMOJIS,
        'ritual_emojis': RITUAL_EMOJIS,
        'messages': PARCHEMIN_MESSAGES,
        'defaults': DEFAULT_VALUES,
        'filtering': FILTERING_CONFIG,
        'logging': LOGGING_CONFIG
    }
    
    if section:
        return all_config.get(section, {})
    
    return all_config

def validate_config() -> bool:
    """
    Valide la configuration actuelle.
    Même logique que dans boutique/config_v2.py
    """
    try:
        assert GOOGLE_SHEETS_CONFIG['sheet_id'], "Sheet ID manquant"
        assert GOOGLE_SHEETS_CONFIG['sheet_name'], "Nom de feuille manquant"
        assert SPELL_SELECTION_CONFIG['min_items'] > 0, "min_items doit être > 0"
        assert SPELL_SELECTION_CONFIG['max_items'] >= SPELL_SELECTION_CONFIG['min_items'], "max_items doit être >= min_items"
        
        return True
    except AssertionError as e:
        print(f"Erreur de configuration: {e}")
        return False

def get_column_name(column_key: str) -> str:
    """
    Récupère le nom de la colonne pour une clé donnée.
    Utile pour avoir une source unique de vérité.
    
    Args:
        column_key: Clé de colonne (ex: 'name', 'level', 'school', etc.)
        
    Returns:
        str: Nom de la colonne dans Google Sheets
    """
    return COLUMNS_CONFIG.get(column_key, '')

def print_config() -> None:
    """Affiche la configuration actuelle pour debug."""
    print("🔧 Configuration du module parchemin")
    print("=" * 60)
    
    if validate_config():
        print("✅ Configuration valide\n")
        
        print("📋 Google Sheets:")
        print(f"   • Sheet ID: {GOOGLE_SHEETS_CONFIG['sheet_id']}")
        print(f"   • Sheet Name: {GOOGLE_SHEETS_CONFIG['sheet_name']}")
        print(f"   • Sheet GID: {GOOGLE_SHEETS_CONFIG['sheet_gid']}\n")
        
        print("🎲 Sélection des parchemins:")
        print(f"   • Min/Max: {SPELL_SELECTION_CONFIG['min_items']}-{SPELL_SELECTION_CONFIG['max_items']}")
        print(f"   • Niveaux exclus: {SPELL_SELECTION_CONFIG['excluded_levels']}\n")
        
        print("📊 Mapping des colonnes:")
        for key, col_name in COLUMNS_CONFIG.items():
            print(f"   • {key:15} → {col_name}")
        
    else:
        print("❌ Configuration invalide")

if __name__ == "__main__":
    print_config()