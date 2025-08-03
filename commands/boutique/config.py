# commands/boutique/config.py
"""
Configuration centralisée pour le module boutique avec variables d'environnement.
"""

import os
from typing import List, Dict, Any

# Configuration Google Sheets (avec variables d'environnement)
GOOGLE_SHEETS_CONFIG = {
    'sheet_id': os.getenv('BOUTIQUE_SHEET_ID', '1DsvQ5GmwBH-jXo3vHR-XqkpQjkyRHi5BaZ0gqkcrvI8'),
    'sheet_name': os.getenv('BOUTIQUE_SHEET_NAME', 'Objets Magique'),
    'base_url': 'https://docs.google.com/spreadsheets/d'
}

# Configuration de la sélection d'objets (basée sur l'analyse réelle)
ITEM_SELECTION_CONFIG = {
    'min_items': int(os.getenv('BOUTIQUE_MIN_ITEMS', '3')),
    'max_items': int(os.getenv('BOUTIQUE_MAX_ITEMS', '8')),
    'excluded_rarities': os.getenv('BOUTIQUE_EXCLUDED_RARITIES', 'Très rare,Légendaire,Artefact').split(','),
    'rarity_column': os.getenv('BOUTIQUE_RARITY_COLUMN', 'Rareté')
}

# Configuration des colonnes du Google Sheets (basée sur l'analyse du CSV réel)
COLUMNS_CONFIG = {
    'nom_principal': os.getenv('BOUTIQUE_COL_NOM_PRINCIPAL', 'Nom de l\'objet'),
    'nom_alternatif': os.getenv('BOUTIQUE_COL_NOM_ALTERNATIF', 'Nom de l\'objet_1'),  # Vraie colonne nom
    'nom_vo': os.getenv('BOUTIQUE_COL_NOM_VO', 'Nom Vo '),  # Attention à l'espace à la fin
    'nom_en_vo': os.getenv('BOUTIQUE_COL_NOM_EN_VO', 'Nom en VO'),
    'type': os.getenv('BOUTIQUE_COL_TYPE', 'Type'),
    'rarity': os.getenv('BOUTIQUE_COL_RARITY', 'Rareté'),
    'link': os.getenv('BOUTIQUE_COL_LINK', 'Lien'),
    'craft_cost': os.getenv('BOUTIQUE_COL_CRAFT_COST', 'Coût de craft'),
    'profession': os.getenv('BOUTIQUE_COL_PROFESSION', 'Metier'),
    'buy_price': os.getenv('BOUTIQUE_COL_BUY_PRICE', 'Prix achat'),
    'specs': os.getenv('BOUTIQUE_COL_SPECS', 'Spécificités'),
    'sell_price': os.getenv('BOUTIQUE_COL_SELL_PRICE', 'Prix vente'),
    'source': os.getenv('BOUTIQUE_COL_SOURCE', 'Source'),
    'effect': os.getenv('BOUTIQUE_COL_EFFECT', 'Effet')
}

# Configuration Discord
DISCORD_CONFIG = {
    'max_field_length': int(os.getenv('BOUTIQUE_MAX_FIELD_LENGTH', '1024')),
    'max_embed_length': int(os.getenv('BOUTIQUE_MAX_EMBED_LENGTH', '6000')),
    'colors': {
        'success': int(os.getenv('BOUTIQUE_COLOR_SUCCESS', '0x2ecc71'), 16),  # Vert
        'error': int(os.getenv('BOUTIQUE_COLOR_ERROR', '0xe74c3c'), 16),     # Rouge
        'warning': int(os.getenv('BOUTIQUE_COLOR_WARNING', '0xf39c12'), 16), # Orange
        'info': int(os.getenv('BOUTIQUE_COLOR_INFO', '0x3498db'), 16),       # Bleu
        'magic': int(os.getenv('BOUTIQUE_COLOR_MAGIC', '0x9b59b6'), 16)      # Violet
    }
}

# Emojis par rareté
RARITY_EMOJIS = {
    'commun': os.getenv('BOUTIQUE_EMOJI_COMMUN', '⚪'),
    'peu commun': os.getenv('BOUTIQUE_EMOJI_PEU_COMMUN', '🟢'), 
    'rare': os.getenv('BOUTIQUE_EMOJI_RARE', '🔵'),
    'très rare': os.getenv('BOUTIQUE_EMOJI_TRES_RARE', '🟣'),
    'légendaire': os.getenv('BOUTIQUE_EMOJI_LEGENDAIRE', '🟡'),
    'artefact': os.getenv('BOUTIQUE_EMOJI_ARTEFACT', '🔴'),
    'default': os.getenv('BOUTIQUE_EMOJI_DEFAULT', '✨')
}

# Messages de la boutique
BOUTIQUE_MESSAGES = {
    'title': os.getenv('BOUTIQUE_MSG_TITLE', '🏪 Boutique Magique - Objets Disponibles'),
    'loading_title': os.getenv('BOUTIQUE_MSG_LOADING_TITLE', '🔄 Préparation de la Boutique...'),
    'loading_description': os.getenv('BOUTIQUE_MSG_LOADING_DESC', 'Le marchand sélectionne ses meilleurs objets magiques...'),
    'error_title': os.getenv('BOUTIQUE_MSG_ERROR_TITLE', '❌ Erreur - Boutique Indisponible'),
    'footer_base': os.getenv('BOUTIQUE_MSG_FOOTER_BASE', 'Boutique magique de Faerûn'),
    'footer_loading': os.getenv('BOUTIQUE_MSG_FOOTER_LOADING', 'Veuillez patienter quelques instants'),
    'footer_error': os.getenv('BOUTIQUE_MSG_FOOTER_ERROR', 'Boutique temporairement fermée')
}

# Validation et valeurs par défaut
DEFAULT_VALUES = {
    'item_name': os.getenv('BOUTIQUE_DEFAULT_ITEM_NAME', 'Objet mystérieux'),
    'rarity': os.getenv('BOUTIQUE_DEFAULT_RARITY', 'Inconnue'),
    'price': os.getenv('BOUTIQUE_DEFAULT_PRICE', 'Non spécifié'),
    'effect': os.getenv('BOUTIQUE_DEFAULT_EFFECT', 'Effet mystérieux'),
    'type': os.getenv('BOUTIQUE_DEFAULT_TYPE', 'Objet magique')
}

# Emojis pour le lien magique
LIEN_MAGIQUE_EMOJIS = {
    'oui': os.getenv('BOUTIQUE_EMOJI_LIEN_OUI', '🔗'),
    'non': os.getenv('BOUTIQUE_EMOJI_LIEN_NON', '❌'),
    'maudit': os.getenv('BOUTIQUE_EMOJI_LIEN_MAUDIT', '💀'),
    'default': os.getenv('BOUTIQUE_EMOJI_LIEN_DEFAULT', '🔮')
}
LOGGING_CONFIG = {
    'level': os.getenv('BOUTIQUE_LOG_LEVEL', 'INFO'),
    'format': os.getenv('BOUTIQUE_LOG_FORMAT', '[%(asctime)s] [BOUTIQUE] %(levelname)s: %(message)s')
}

def get_config(section: str = None) -> Dict[str, Any]:
    """
    Récupère une section de configuration ou toute la configuration.
    
    Args:
        section: Nom de la section à récupérer (optionnel)
        
    Returns:
        dict: Configuration demandée
    """
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
    """
    Valide la configuration actuelle.
    
    Returns:
        bool: True si la configuration est valide
    """
    try:
        # Vérifications basiques
        assert GOOGLE_SHEETS_CONFIG['sheet_id'], "Sheet ID manquant"
        assert GOOGLE_SHEETS_CONFIG['sheet_name'], "Nom de feuille manquant"
        assert ITEM_SELECTION_CONFIG['min_items'] > 0, "min_items doit être > 0"
        assert ITEM_SELECTION_CONFIG['max_items'] >= ITEM_SELECTION_CONFIG['min_items'], "max_items doit être >= min_items"
        assert ITEM_SELECTION_CONFIG['excluded_rarities'] is not None, "excluded_rarities ne peut pas être None"
        
        return True
    except AssertionError as e:
        print(f"Erreur de configuration: {e}")
        return False

def print_env_template():
    """
    Affiche un template pour les variables d'environnement.
    """
    template = """
# ============================================================================
# VARIABLES D'ENVIRONNEMENT POUR LE MODULE BOUTIQUE
# ============================================================================
# Copiez ces variables dans votre fichier .env et modifiez les valeurs selon vos besoins

# Configuration Google Sheets
BOUTIQUE_SHEET_ID=1DsvQ5GmwBH-jXo3vHR-XqkpQjkyRHi5BaZ0gqkcrvI8
BOUTIQUE_SHEET_NAME=Objets Magique

# Configuration de sélection
BOUTIQUE_MIN_ITEMS=3
BOUTIQUE_MAX_ITEMS=8
BOUTIQUE_EXCLUDED_RARITIES=très rare,légendaire
BOUTIQUE_RARITY_COLUMN=Rareté

# Configuration des colonnes (noms exacts dans le Google Sheets)
BOUTIQUE_COL_NOM=Nom de l'objet
BOUTIQUE_COL_NOM_VO=Nom Vo Nom en VO
BOUTIQUE_COL_TYPE=Type
BOUTIQUE_COL_RARITY=Rareté
BOUTIQUE_COL_LINK=Lien
BOUTIQUE_COL_CRAFT_COST=Coût de craft
BOUTIQUE_COL_PROFESSION=Metier
BOUTIQUE_COL_BUY_PRICE=Prix achat
BOUTIQUE_COL_SPECS=Spécificités
BOUTIQUE_COL_SELL_PRICE=Prix vente
BOUTIQUE_COL_SOURCE=Source
BOUTIQUE_COL_EFFECT=Effet

# Configuration Discord
BOUTIQUE_MAX_FIELD_LENGTH=1024
BOUTIQUE_MAX_EMBED_LENGTH=6000

# Couleurs Discord (format hexadécimal)
BOUTIQUE_COLOR_SUCCESS=0x2ecc71
BOUTIQUE_COLOR_ERROR=0xe74c3c
BOUTIQUE_COLOR_WARNING=0xf39c12
BOUTIQUE_COLOR_INFO=0x3498db
BOUTIQUE_COLOR_MAGIC=0x9b59b6

# Emojis par rareté
BOUTIQUE_EMOJI_COMMUN=⚪
BOUTIQUE_EMOJI_PEU_COMMUN=🟢
BOUTIQUE_EMOJI_RARE=🔵
BOUTIQUE_EMOJI_TRES_RARE=🟣
BOUTIQUE_EMOJI_LEGENDAIRE=🟡
BOUTIQUE_EMOJI_ARTEFACT=🔴
BOUTIQUE_EMOJI_DEFAULT=✨

# Messages personnalisés
BOUTIQUE_MSG_TITLE=🏪 Boutique Magique - Objets Disponibles
BOUTIQUE_MSG_LOADING_TITLE=🔄 Préparation de la Boutique...
BOUTIQUE_MSG_LOADING_DESC=Le marchand sélectionne ses meilleurs objets magiques...
BOUTIQUE_MSG_ERROR_TITLE=❌ Erreur - Boutique Indisponible
BOUTIQUE_MSG_FOOTER_BASE=Boutique magique de Faerûn
BOUTIQUE_MSG_FOOTER_LOADING=Veuillez patienter quelques instants
BOUTIQUE_MSG_FOOTER_ERROR=Boutique temporairement fermée

# Valeurs par défaut
BOUTIQUE_DEFAULT_ITEM_NAME=Objet mystérieux
BOUTIQUE_DEFAULT_RARITY=Inconnue
BOUTIQUE_DEFAULT_PRICE=Non spécifié
BOUTIQUE_DEFAULT_EFFECT=Effet mystérieux
BOUTIQUE_DEFAULT_TYPE=Objet magique

# Configuration de logging
BOUTIQUE_LOG_LEVEL=INFO
BOUTIQUE_LOG_FORMAT=[%(asctime)s] [BOUTIQUE] %(levelname)s: %(message)s

# ============================================================================
"""
    print(template)

def load_env_file(filepath: str = '.env') -> bool:
    """
    Charge un fichier .env manuellement (simple implémentation).
    
    Args:
        filepath: Chemin vers le fichier .env
        
    Returns:
        bool: True si le fichier a été chargé avec succès
    """
    try:
        if not os.path.exists(filepath):
            return False
        
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
        
        return True
    except Exception as e:
        print(f"Erreur lors du chargement du fichier .env: {e}")
        return False

# Tentative de chargement automatique du fichier .env
if os.path.exists('.env'):
    load_env_file('.env')

# Validation automatique au chargement du module
if __name__ == "__main__":
    print("🔧 Configuration du module boutique")
    print("=" * 50)
    
    if validate_config():
        print("✅ Configuration valide")
        
        # Affichage de la configuration actuelle
        config = get_config()
        print(f"\n📋 Configuration actuelle:")
        print(f"   • Sheet ID: {config['google_sheets']['sheet_id']}")
        print(f"   • Sheet Name: {config['google_sheets']['sheet_name']}")
        print(f"   • Min/Max items: {config['item_selection']['min_items']}-{config['item_selection']['max_items']}")
        print(f"   • Raretés exclues: {', '.join(config['item_selection']['excluded_rarities'])}")
        
    else:
        print("❌ Configuration invalide")
    
    print(f"\n💡 Pour personnaliser la configuration, créez un fichier .env avec:")
    print("   python -c \"from commands.boutique.config import print_env_template; print_env_template()\"")