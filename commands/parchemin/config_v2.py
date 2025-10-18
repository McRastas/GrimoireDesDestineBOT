# commands/parchemin/config_v2.py
"""
Configuration pour les parchemins de sorts - Structure similaire à boutique/config_v2.py
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

# Mapping des colonnes selon les noms du CSV sorts (comme COLUMNS_CONFIG dans boutique)
COLUMNS_CONFIG = {
    'name': os.getenv('PARCHEMIN_COL_NAME', 'Name'),
    'source': os.getenv('PARCHEMIN_COL_SOURCE', 'Source'),
    'level': os.getenv('PARCHEMIN_COL_LEVEL', 'Level'),
    'school': os.getenv('PARCHEMIN_COL_SCHOOL', 'School'),
    'ritual': os.getenv('PARCHEMIN_COL_RITUAL', 'RITUEL'),
    'classes': os.getenv('PARCHEMIN_COL_CLASSES', 'CLASSE'),
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
        7: 0x34495e,    # Bleu foncé pour niveau 7
        8: 0x2c3e50,    # Bleu très foncé pour niveau 8
        9: 0x1a252f     # Presque noir pour niveau 9
    },
    'max_field_length': 1024,
    'max_embed_length': 6000,
    'max_embed_fields': 25
}

# Emojis pour les écoles de magie (comme RARITY_EMOJIS dans boutique)
SCHOOL_EMOJIS = {
    'abjuration': '🛡️',
    'conjuration': '🌀',
    'divination': '🔮',
    'enchantment': '💫',
    'evocation': '⚡',
    'illusion': '🎭',
    'necromancy': '💀',
    'transmutation': '🔄',
}

# Emojis pour les niveaux (comme LEVEL_EMOJIS mais pour parchemin)
LEVEL_EMOJIS = {
    0: '✨',  # Cantrip
    1: '1️⃣',
    2: '2️⃣',
    3: '3️⃣',
    4: '4️⃣',
    5: '5️⃣',
    6: '6️⃣',
    7: '7️⃣',
    8: '8️⃣',
    9: '9️⃣',
}

# Emojis pour les sorts rituels (comme LIEN_MAGIQUE_EMOJIS dans boutique)
RITUAL_EMOJIS = {
    True: '🔮',  # Sort rituel
    False: '',   # Sort normal
}

# Messages par défaut (comme BOUTIQUE_MESSAGES dans boutique)
PARCHEMIN_MESSAGES = {
    'title': '📜 **Parchemins de sorts**',
    'no_spells': '❌ Aucun sort trouvé avec ces critères.',
    'invalid_level': '❌ Format de niveau invalide. Utilisez un nombre (ex: 3) ou une plage (ex: 1-3).',
    'invalid_count': '❌ Le nombre de parchemins doit être entre {min} et {max}.',
    'loading_error': '❌ Erreur lors du chargement des sorts. Contactez un administrateur.',
    'sheets_error': '❌ Impossible d\'accéder aux données Google Sheets.',
    'footer_base': 'Parchemins de Faerûn',
    'footer_loading': 'Chargement des sorts...',
    'footer_error': 'Échec du chargement'
}

# Valeurs par défaut adaptées (comme DEFAULT_VALUES dans boutique)
DEFAULT_VALUES = {
    'spell_name': 'Sort mystérieux',
    'level': 0,
    'school': 'Inconnue',
    'source': 'Manuel inconnu',
    'ritual': False,
    'classes': []
}

# Configuration de filtrage (comme FILTERING_CONFIG dans boutique)
FILTERING_CONFIG = {
    'exclude_na_values': True,
    'critical_columns': ['Name', 'Level', 'School'],
    'na_values': ['NA', 'N/A', 'na', 'n/a', 'null', 'NULL', 'Null', ''],
    'require_valid_name': True,
    'require_valid_level': True,
    'level_range_separator': '-',
    'class_separator': ',',
    'min_similarity': 0.4  # Pour la recherche floue
}

# Configuration de logging (comme LOGGING_CONFIG dans boutique)
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '[%(asctime)s] [PARCHEMIN] %(levelname)s: %(message)s'
}

def get_config(section: str = None) -> Dict[str, Any]:
    """
    Récupère une section de configuration ou toute la configuration.
    Même structure que dans boutique/config_v2.py
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

# Fonction de normalisation des écoles (comme normalize_rarity_name dans boutique)
def normalize_school_name(school: str) -> str:
    """
    Convertit le nom d'école en format lisible avec emoji.
    Équivalent de normalize_rarity_name pour les écoles.
    """
    school_lower = school.lower().strip()
    emoji = SCHOOL_EMOJIS.get(school_lower, '🔮')
    return f"{emoji} {school.title()}"

# Fonction de normalisation des niveaux
def normalize_level_name(level: int) -> str:
    """
    Convertit le niveau en format lisible avec emoji.
    """
    if level == 0:
        return f"{LEVEL_EMOJIS[0]} Tours de magie"
    else:
        emoji = LEVEL_EMOJIS.get(level, '🔥')
        return f"{emoji} Niveau {level}"

# Fonction de vérification NA (comme is_na_value dans boutique)
def is_na_value(value: str) -> bool:
    """
    Vérifie si une valeur est considérée comme NA.
    Même logique que dans boutique/config_v2.py
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
    Même logique que dans boutique/config_v2.py
    """
    if is_na_value(value):
        return default
    
    return str(value).strip()

def parse_classes_list(classes_str: str) -> List[str]:
    """
    Parse une chaîne de classes en liste.
    Adapté de la logique de parsing des prix/colonnes dans boutique.
    """
    if is_na_value(classes_str):
        return []
    
    separator = FILTERING_CONFIG['class_separator']
    classes = [cls.strip() for cls in classes_str.split(separator) if cls.strip()]
    return classes

if __name__ == "__main__":
    print("🔧 Configuration du module parchemin")
    print("=" * 50)
    
    if validate_config():
        print("✅ Configuration valide")
        config = get_config()
        print(f"\n📋 Configuration actuelle:")
        print(f"   • Sheet ID: {config['google_sheets']['sheet_id']}")
        print(f"   • Sheet Name: {config['google_sheets']['sheet_name']}")
        print(f"   • Min/Max parchemins: {config['spell_selection']['min_items']}-{config['spell_selection']['max_items']}")
        print(f"   • Niveaux exclus: {', '.join(config['spell_selection']['excluded_levels'])}")
        
        # Test des fonctions de conversion
        print(f"\n🔄 Test des conversions:")
        print(f"   • 'Evocation' -> '{normalize_school_name('Evocation')}'")
        print(f"   • Niveau 3 -> '{normalize_level_name(3)}'")
        print(f"   • 'Wizard , Sorcerer' -> {parse_classes_list('Wizard , Sorcerer')}")
        
    else:
        print("❌ Configuration invalide")




