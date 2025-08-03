# commands/boutique/__init__.py
"""
Module Boutique - Bot Faerûn (Version OM_PRICE uniquement)

Ce module fournit un système de boutique aléatoire basé sur Google Sheets
pour générer des objets magiques au format OM_PRICE.

ARCHITECTURE MODULAIRE:
    - main_command_v2.py        : Commande principale OM_PRICE
    - google_sheets_client.py   : Client pour accéder au Google Sheets public
    - item_selector_v2.py       : Sélecteur d'objets OM_PRICE
    - response_builder_v2.py    : Constructeur de réponses OM_PRICE
    - config_v2.py             : Configuration OM_PRICE
    - __init__.py              : Assemblage et exports du module

UTILISATION:
    from commands.boutique import BoutiqueCommand
    
    command = BoutiqueCommand(bot)
    command.register(bot.tree)

FONCTIONNALITÉS:
    ✅ Accès aux Google Sheets publics (pas de credentials requis)
    ✅ Filtrage par rareté OM_PRICE (exclut 3-VERY RARE et 4-LEGENDARY)
    ✅ Sélection aléatoire de 3-8 objets
    ✅ Formatage Discord avec embeds
    ✅ Gestion d'erreurs robuste
    ✅ Liens directs vers Google Sheets
    ✅ Prix multiples (CostF, MEDIANNE, etc.)
    ✅ Noms français et anglais
"""

# Import principal - utiliser la version V2 comme version principale
try:
    from .main_command_v2 import BoutiqueCommandV2 as BoutiqueCommand
    BOUTIQUE_AVAILABLE = True
    print("✅ Module boutique OM_PRICE chargé avec succès")
except ImportError as e:
    BOUTIQUE_AVAILABLE = False
    print(f"❌ Module boutique OM_PRICE non disponible: {e}")
    print("   • Vérifiez que main_command_v2.py existe")
    print("   • Vérifiez que aiohttp est installé")

# Import des composants pour usage avancé
try:
    from .google_sheets_client import GoogleSheetsClient
    SHEETS_CLIENT_AVAILABLE = True
except ImportError:
    SHEETS_CLIENT_AVAILABLE = False
    print("⚠️ GoogleSheetsClient non disponible")

try:
    from .item_selector_v2 import ItemSelectorV2
    ITEM_SELECTOR_AVAILABLE = True
except ImportError:
    ITEM_SELECTOR_AVAILABLE = False
    print("⚠️ ItemSelectorV2 non disponible")

try:
    from .response_builder_v2 import BoutiqueResponseBuilderV2
    RESPONSE_BUILDER_AVAILABLE = True
except ImportError:
    RESPONSE_BUILDER_AVAILABLE = False
    print("⚠️ BoutiqueResponseBuilderV2 non disponible")

try:
    from .config_v2 import get_config, validate_config
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False
    print("⚠️ Configuration V2 non disponible")

# Export principal
__all__ = []

if BOUTIQUE_AVAILABLE:
    __all__.append('BoutiqueCommand')

if SHEETS_CLIENT_AVAILABLE:
    __all__.append('GoogleSheetsClient')

if ITEM_SELECTOR_AVAILABLE:
    __all__.append('ItemSelectorV2')

if RESPONSE_BUILDER_AVAILABLE:
    __all__.append('BoutiqueResponseBuilderV2')

if CONFIG_AVAILABLE:
    __all__.extend(['get_config', 'validate_config'])

# Métadonnées du module
__version__ = "2.0.0-OM_PRICE"
__author__ = "Bot Faerûn Team"
__description__ = "Système de boutique aléatoire OM_PRICE basé sur Google Sheets"

# Configuration du module
MODULE_CONFIG = {
    'version': __version__,
    'format': 'OM_PRICE',
    'boutique_available': BOUTIQUE_AVAILABLE,
    'components': {
        'sheets_client': SHEETS_CLIENT_AVAILABLE,
        'item_selector': ITEM_SELECTOR_AVAILABLE,
        'response_builder': RESPONSE_BUILDER_AVAILABLE,
        'config': CONFIG_AVAILABLE
    },
    'features': [
        'Format OM_PRICE natif',
        'Raretés numériques (0-COMMUN à 4-LEGENDARY)',
        'Prix multiples (CostF, MEDIANNE, etc.)',
        'Noms français/anglais (NameVF/Name)',
        'Liens magiques Y/N',
        'Liens directs Google Sheets',
        'Filtrage intelligent par rareté'
    ]
}

def create_command_instance(bot):
    """
    Factory function pour créer une instance de la commande boutique.
    
    Args:
        bot: Instance du bot Discord
        
    Returns:
        BoutiqueCommand: Instance configurée de la commande OM_PRICE
    """
    if not BOUTIQUE_AVAILABLE:
        raise ImportError("La commande boutique OM_PRICE n'est pas disponible")
    
    return BoutiqueCommand(bot)

def get_module_info() -> dict:
    """
    Retourne les informations sur le module boutique.
    
    Returns:
        dict: Informations complètes du module
    """
    return MODULE_CONFIG

def diagnose_module() -> dict:
    """
    Effectue un diagnostic du module boutique OM_PRICE.
    
    Returns:
        dict: Résultats du diagnostic
    """
    diagnosis = {
        'module_ready': BOUTIQUE_AVAILABLE,
        'version': __version__,
        'format': 'OM_PRICE',
        'all_components_available': all([
            BOUTIQUE_AVAILABLE,
            SHEETS_CLIENT_AVAILABLE, 
            ITEM_SELECTOR_AVAILABLE,
            RESPONSE_BUILDER_AVAILABLE,
            CONFIG_AVAILABLE
        ]),
        'components_status': MODULE_CONFIG['components'],
        'missing_components': [
            comp for comp, available in MODULE_CONFIG['components'].items() 
            if not available
        ]
    }
    
    return diagnosis

# Message d'initialisation
if __name__ == "__main__":
    print("🔧 Module Boutique OM_PRICE")
    print("=" * 40)
    
    diag = diagnose_module()
    print(f"📦 Version: {diag['version']}")
    print(f"🎯 Format: {diag['format']}")
    print(f"✅ Module prêt: {diag['module_ready']}")
    
    if diag['missing_components']:
        print(f"⚠️ Composants manquants: {', '.join(diag['missing_components'])}")
    else:
        print("✅ Tous les composants sont disponibles")
    
    print(f"\n🚀 Utilisation: from commands.boutique import BoutiqueCommand")
    print(f"   Commande Discord: /boutique-v2")

# Auto-diagnostic au chargement du module
try:
    if CONFIG_AVAILABLE:
        if validate_config():
            print("✅ Configuration OM_PRICE validée")
        else:
            print("⚠️ Configuration OM_PRICE invalide")
except Exception as e:
    print(f"⚠️ Erreur validation configuration: {e}")

print(f"📋 Module boutique OM_PRICE chargé - {len(__all__)} exports disponibles")