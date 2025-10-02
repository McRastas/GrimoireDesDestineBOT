# commands/postulation/config.py
"""
Configuration pour le système de postulation des joueurs.
"""

import os
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

# Tentative de chargement automatique du fichier .env avec python-dotenv
try:
    from dotenv import load_dotenv
    load_dotenv()
    logger.info("✅ Fichier .env chargé avec python-dotenv")
except ImportError:
    logger.info("ℹ️ Aucun fichier .env trouvé, utilisation des valeurs par défaut")

# Configuration Google Sheets pour les personnages
GOOGLE_SHEETS_CONFIG = {
    'sheet_id': os.getenv('POSTULATION_SHEET_ID', '1QPLhU1I594hKQdvg4LhrL6Tui6pko01hiRO0DUnvk2U'),
    'sheet_name': os.getenv('POSTULATION_SHEET_NAME', 'Suivi des personnages'),
    'sheet_gid': os.getenv('POSTULATION_SHEET_GID', '0'),
    'base_url': 'https://docs.google.com/spreadsheets/d'
}

# Mapping des colonnes du Google Sheet
COLUMNS_CONFIG = {
    'discord_id': os.getenv('POSTULATION_COL_DISCORD_ID', 'ID Discord'),
    'nom_pj': os.getenv('POSTULATION_COL_NOM_PJ', 'Nom du PJ'),
    'joueur': os.getenv('POSTULATION_COL_JOUEUR', 'Joueurs'),
    'token_url': os.getenv('POSTULATION_COL_TOKEN_URL', 'Url de token'),
    'race': os.getenv('POSTULATION_COL_RACE', 'Races'),
    'classe1': os.getenv('POSTULATION_COL_CLASSE1', 'Classe 1'),
    'niveau1': os.getenv('POSTULATION_COL_NIVEAU1', 'Niv.'),
    'classe2': os.getenv('POSTULATION_COL_CLASSE2', 'Classe 2'),
    'niveau2': os.getenv('POSTULATION_COL_NIVEAU2', 'Niv._1'),
    'classe3': os.getenv('POSTULATION_COL_CLASSE3', 'Classe 3'),
    'niveau3': os.getenv('POSTULATION_COL_NIVEAU3', 'Niv._2'),
    'niveau_total': os.getenv('POSTULATION_COL_NIVEAU_TOTAL', 'Niv. PJ'),
    'statut': os.getenv('POSTULATION_COL_STATUT', 'Statut')
}

# Configuration de filtrage des personnages
FILTERING_CONFIG = {
    'statut_valide': os.getenv('POSTULATION_STATUT_VALIDE', 'ACTIF'),
    'exclude_pnj': os.getenv('POSTULATION_EXCLUDE_PNJ', 'true').lower() == 'true',
    'statut_pnj': 'PNJ'
}

# Configuration Discord
DISCORD_CONFIG = {
    'use_webhook': os.getenv('POSTULATION_USE_WEBHOOK', 'true').lower() == 'true',
    'webhook_fallback': True,  # Utiliser mention si webhook échoue
    'embed_color': int(os.getenv('POSTULATION_EMBED_COLOR', '0x3498db'), 16),
    'max_rp_length': int(os.getenv('POSTULATION_MAX_RP_LENGTH', '1000'))
}

# Messages personnalisables
MESSAGES_CONFIG = {
    'title': os.getenv('POSTULATION_MSG_TITLE', '🎭 POSTULATION'),
    'no_characters': os.getenv('POSTULATION_MSG_NO_CHARS', 'Aucun personnage actif trouvé pour votre compte Discord.'),
    'error_loading': os.getenv('POSTULATION_MSG_ERROR_LOADING', 'Erreur lors du chargement de vos personnages.'),
    'success': os.getenv('POSTULATION_MSG_SUCCESS', 'Postulation envoyée avec succès !'),
    'select_placeholder': os.getenv('POSTULATION_SELECT_PLACEHOLDER', 'Choisissez votre personnage...'),
    'rp_label': os.getenv('POSTULATION_RP_LABEL', 'Message RP de postulation'),
    'rp_placeholder': os.getenv('POSTULATION_RP_PLACEHOLDER', 'Décrivez pourquoi votre personnage souhaite participer à cette quête...')
}

# Configuration de logging
LOGGING_CONFIG = {
    'level': os.getenv('POSTULATION_LOG_LEVEL', 'INFO'),
    'format': os.getenv('POSTULATION_LOG_FORMAT', '[%(asctime)s] [POSTULATION] %(levelname)s: %(message)s')
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
        'columns': COLUMNS_CONFIG,
        'filtering': FILTERING_CONFIG,
        'discord': DISCORD_CONFIG,
        'messages': MESSAGES_CONFIG,
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
        assert GOOGLE_SHEETS_CONFIG['sheet_id'], "Sheet ID manquant"
        assert GOOGLE_SHEETS_CONFIG['sheet_name'], "Nom de feuille manquant"
        assert COLUMNS_CONFIG['discord_id'], "Colonne discord_id manquante"
        assert COLUMNS_CONFIG['nom_pj'], "Colonne nom_pj manquante"
        assert DISCORD_CONFIG['max_rp_length'] > 0, "max_rp_length doit être > 0"
        
        logger.info("✅ Configuration postulation validée")
        return True
    except AssertionError as e:
        logger.error(f"❌ Erreur de configuration postulation: {e}")
        return False

def format_class_info(classe1: str, niveau1: str, classe2: str = "", niveau2: str = "", classe3: str = "", niveau3: str = "") -> str:
    """
    Formate les informations de classe(s) d'un personnage.
    
    Args:
        classe1: Première classe
        niveau1: Niveau de la première classe
        classe2: Deuxième classe (optionnel)
        niveau2: Niveau de la deuxième classe (optionnel)
        classe3: Troisième classe (optionnel)
        niveau3: Niveau de la troisième classe (optionnel)
        
    Returns:
        str: Classes formatées (ex: "Paladin 5 / Guerrier 3")
    """
    classes = []
    
    if classe1 and niveau1:
        classes.append(f"{classe1} {niveau1}")
    
    if classe2 and niveau2:
        classes.append(f"{classe2} {niveau2}")
    
    if classe3 and niveau3:
        classes.append(f"{classe3} {niveau3}")
    
    return " / ".join(classes) if classes else "Classe inconnue"

def clean_value(value: Any, default: str = "") -> str:
    """
    Nettoie une valeur en gérant les None, vides, et NA.
    
    Args:
        value: Valeur à nettoyer
        default: Valeur par défaut si vide
        
    Returns:
        str: Valeur nettoyée
    """
    if value is None:
        return default
    
    value_str = str(value).strip()
    
    # Valeurs considérées comme vides
    empty_values = ['', 'NA', 'N/A', 'na', 'n/a', 'null', 'NULL', 'None', '0']
    
    if value_str in empty_values:
        return default
    
    return value_str

if __name__ == "__main__":
    print("🔧 Configuration du module postulation")
    print("=" * 60)
    
    if validate_config():
        print("✅ Configuration valide")
        config = get_config()
        print(f"\n📋 Configuration actuelle:")
        print(f"   • Sheet ID: {config['google_sheets']['sheet_id']}")
        print(f"   • Sheet Name: {config['google_sheets']['sheet_name']}")
        print(f"   • Statut valide: {config['filtering']['statut_valide']}")
        print(f"   • Use Webhook: {config['discord']['use_webhook']}")
        print(f"   • Max RP Length: {config['discord']['max_rp_length']}")
        
        # Test des fonctions utilitaires
        print(f"\n🔄 Test des fonctions:")
        test_classes = format_class_info("Paladin", "5", "Guerrier", "3")
        print(f"   • format_class_info('Paladin', '5', 'Guerrier', '3') -> '{test_classes}'")
        test_clean = clean_value("NA", "Valeur par défaut")
        print(f"   • clean_value('NA', 'Valeur par défaut') -> '{test_clean}'")
    else:
        print("❌ Configuration invalide")