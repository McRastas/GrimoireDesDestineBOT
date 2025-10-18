# commands/parchemin/__init__.py
"""
Module Parchemin - Bot Faerûn (Parchemins de sorts D&D 5e)

Ce module fournit un système de génération de parchemins aléatoires basé sur Google Sheets
pour générer des sorts D&D 5e avec filtres avancés.

ARCHITECTURE MODULAIRE:
    - main_command_v2.py        : Commande principale parchemin
    - google_sheets_client.py   : Client pour accéder au Google Sheets public
    - spell_selector_v2.py      : Sélecteur de sorts avec filtres
    - response_builder_v2.py    : Constructeur de réponses Discord
    - config_v2.py             : Configuration des parchemins
    - __init__.py              : Assemblage et exports du module

UTILISATION:
    from commands.parchemin import ParcheminCommand
    
    command = ParcheminCommand(bot)
    command.register(bot.tree)

FONCTIONNALITÉS:
    ✅ Accès aux Google Sheets publics (pas de credentials requis)
    ✅ Filtrage par niveau, école, classe, rituel
    ✅ Sélection aléatoire de 1-15 sorts
    ✅ Formatage Discord avec embeds enrichis
    ✅ Gestion d'erreurs robuste
    ✅ Liens directs vers Google Sheets
    ✅ Support plages de niveaux (ex: 1-3)
    ✅ Emojis par école de magie
    ✅ Cache intelligent des données
"""

# Import principal - utiliser la version V2 comme version principale (même logique que boutique)
try:
    from .main_command_v2 import ParcheminCommandV2 as ParcheminCommand
    PARCHEMIN_AVAILABLE = True
    print("✅ Module parchemin chargé avec succès")
except ImportError as e:
    PARCHEMIN_AVAILABLE = False
    print(f"❌ Module parchemin non disponible: {e}")
    print("   • Vérifiez que main_command_v2.py existe")
    print("   • Vérifiez que aiohttp est installé")

# Import des composants pour usage avancé (même structure que boutique)
try:
    from .google_sheets_client import GoogleSheetsClient
    SHEETS_CLIENT_AVAILABLE = True
except ImportError:
    SHEETS_CLIENT_AVAILABLE = False
    print("⚠️ GoogleSheetsClient non disponible")

try:
    from .spell_selector_v2 import SpellSelectorV2
    SPELL_SELECTOR_AVAILABLE = True
except ImportError:
    SPELL_SELECTOR_AVAILABLE = False
    print("⚠️ SpellSelectorV2 non disponible")

try:
    from .response_builder_v2 import ParcheminResponseBuilderV2
    RESPONSE_BUILDER_AVAILABLE = True
except ImportError:
    RESPONSE_BUILDER_AVAILABLE = False
    print("⚠️ ParcheminResponseBuilderV2 non disponible")

try:
    from .config_v2 import get_config, validate_config
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False
    print("⚠️ Configuration V2 non disponible")

# Export principal (même structure que boutique)
__all__ = []

if PARCHEMIN_AVAILABLE:
    __all__.append('ParcheminCommand')

if SHEETS_CLIENT_AVAILABLE:
    __all__.append('GoogleSheetsClient')

if SPELL_SELECTOR_AVAILABLE:
    __all__.append('SpellSelectorV2')

if RESPONSE_BUILDER_AVAILABLE:
    __all__.append('ParcheminResponseBuilderV2')

if CONFIG_AVAILABLE:
    __all__.extend(['get_config', 'validate_config'])

# Métadonnées du module (adaptation de boutique)
__version__ = "1.0.0-SPELLS"
__author__ = "Bot Faerûn Team"
__description__ = "Système de génération de parchemins de sorts basé sur Google Sheets"

# Configuration du module (même structure que boutique)
MODULE_CONFIG = {
    'version': __version__,
    'format': 'D&D_5E_SPELLS',
    'parchemin_available': PARCHEMIN_AVAILABLE,
    'components': {
        'sheets_client': SHEETS_CLIENT_AVAILABLE,
        'spell_selector': SPELL_SELECTOR_AVAILABLE,
        'response_builder': RESPONSE_BUILDER_AVAILABLE,
        'config': CONFIG_AVAILABLE
    },
    'features': [
        'Format D&D 5e natif',
        'Niveaux 0-9 (cantrips à niveau 9)',
        'Filtrage par école, classe, rituel',
        'Plages de niveaux (ex: 1-3)',
        'Emojis par école de magie',
        'Couleurs par niveau de sort',
        'Sélection aléatoire équilibrée',
        'Cache intelligent des données',
        'Support GID Google Sheets',
        'Affichage enrichi Discord'
    ]
}

def create_command_instance(bot):
    """
    Factory function pour créer une instance de la commande parchemin.
    Même pattern que boutique.
    
    Args:
        bot: Instance du bot Discord
        
    Returns:
        ParcheminCommand: Instance configurée de la commande
    """
    if not PARCHEMIN_AVAILABLE:
        raise ImportError("La commande parchemin n'est pas disponible")
    
    return ParcheminCommand(bot)

def get_module_info() -> dict:
    """
    Retourne les informations sur le module parchemin.
    Même fonction que boutique.
    
    Returns:
        dict: Informations complètes du module
    """
    return MODULE_CONFIG

def diagnose_module() -> dict:
    """
    Effectue un diagnostic du module parchemin.
    Même logique que boutique/diagnose_module.
    
    Returns:
        dict: Résultats du diagnostic
    """
    diagnosis = {
        'module_ready': PARCHEMIN_AVAILABLE,
        'version': __version__,
        'format': 'D&D_5E_SPELLS',
        'all_components_available': all([
            PARCHEMIN_AVAILABLE,
            SHEETS_CLIENT_AVAILABLE, 
            SPELL_SELECTOR_AVAILABLE,
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

# Message d'initialisation (même structure que boutique)
if __name__ == "__main__":
    print("🔧 Module Parchemin D&D 5e")
    print("=" * 40)
    
    diag = diagnose_module()
    print(f"📦 Version: {diag['version']}")
    print(f"🎯 Format: {diag['format']}")
    print(f"✅ Module prêt: {diag['module_ready']}")
    
    if diag['missing_components']:
        print(f"⚠️ Composants manquants: {', '.join(diag['missing_components'])}")
    else:
        print("✅ Tous les composants sont disponibles")
    
    print(f"\n🚀 Utilisation: from commands.parchemin import ParcheminCommand")
    print(f"   Commande Discord: /parchemin")

# Auto-diagnostic au chargement du module (même logique que boutique)
try:
    if CONFIG_AVAILABLE:
        if validate_config():
            print("✅ Configuration parchemin validée")
        else:
            print("⚠️ Configuration parchemin invalide")
except Exception as e:
    print(f"⚠️ Erreur validation configuration: {e}")

print(f"📋 Module parchemin chargé - {len(__all__)} exports disponibles")