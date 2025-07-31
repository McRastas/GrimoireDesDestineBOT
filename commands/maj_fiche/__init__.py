# commands/maj_fiche/__init__.py
"""
Module de mise à jour de fiche D&D - Bot Faerûn

Ce module fournit un système complet pour générer, valider et corriger
les templates de mise à jour de fiche de personnage D&D 5e.

ARCHITECTURE MODULAIRE:
    - main_command.py      : Classe de base commune avec méthodes utilitaires
    - template_generator.py : Générateur de templates avec suggestions par classe
    - slash_command_interface.py : Interface Discord avec gestion des paramètres
    - validation_system.py : Système de validation et correction automatique
    - __init__.py         : Assemblage et exports du module (ce fichier)

UTILISATION:
    from commands.maj_fiche import MajFicheCommand
    
    # La commande est prête à être enregistrée dans l'arbre Discord
    command = MajFicheCommand()
    command.register(bot.tree)

FONCTIONNALITÉS:
    ✅ Génération de templates personnalisés D&D 5e
    ✅ Suggestions intelligentes par classe et niveau
    ✅ Validation automatique des templates existants
    ✅ Corrections automatiques (formatage, séparateurs)
    ✅ Gestion des templates longs (division automatique)
    ✅ Calculs XP/PV automatiques avec vérification
    ✅ Interface Discord complète avec listes déroulantes
    ✅ Système de placeholders pour personnalisation
"""

# Imports des modules internes
from .main_command import MajFicheBaseCommand
from .template_generator import TemplateGenerator
from .validation_system import TemplateValidator
from .slash_command_interface import MajFicheSlashCommand

# Import pour compatibilité avec l'ancien système
# La commande principale reste accessible sous le nom original
MajFicheCommand = MajFicheSlashCommand

# Classes utilitaires accessibles pour extension
__all__ = [
    'MajFicheCommand',           # Commande principale (export principal)
    'MajFicheBaseCommand',       # Classe de base pour extensions
    'TemplateGenerator',         # Générateur de templates
    'TemplateValidator',         # Système de validation  
    'MajFicheSlashCommand'       # Interface Discord complète
]

# Métadonnées du module
__version__ = "2.0.0"
__author__ = "Bot Faerûn Team"
__description__ = "Système complet de mise à jour de fiche D&D 5e"

# Configuration du module
MODULE_CONFIG = {
    'version': __version__,
    'components': {
        'base': 'MajFicheBaseCommand - Logique commune et validations',
        'generator': 'TemplateGenerator - Génération de templates personnalisés', 
        'validator': 'TemplateValidator - Validation et corrections automatiques',
        'interface': 'MajFicheSlashCommand - Interface Discord complète'
    },
    'features': [
        'Templates D&D 5e personnalisés',
        'Suggestions par classe/niveau', 
        'Validation automatique',
        'Corrections intelligentes',
        'Gestion longueur Discord',
        'Calculs XP/PV automatiques'
    ],
    'discord_limits': {
        'message_length': 2000,
        'safe_length': 1800,
        'embed_fields': 25,
        'embed_total_length': 6000
    }
}

def get_module_info() -> dict:
    """
    Retourne les informations sur le module maj_fiche.
    
    Returns:
        dict: Informations complètes du module
    """
    return MODULE_CONFIG

def create_command_instance():
    """
    Factory function pour créer une instance de la commande principale.
    Utile pour les tests et l'instanciation programmatique.
    
    Returns:
        MajFicheSlashCommand: Instance configurée de la commande
    """
    return MajFicheSlashCommand()

def validate_template_content(content: str) -> dict:
    """
    Fonction utilitaire pour valider un template de fiche.
    Peut être utilisée indépendamment de Discord.
    
    Args:
        content: Le contenu du template à valider
        
    Returns:
        dict: Résultat de la validation avec score et suggestions
    """
    validator = TemplateValidator()
    return validator.verify_template(content)

def generate_basic_template(nom_pj: str, classe: str, **kwargs) -> str:
    """
    Fonction utilitaire pour générer un template de base.
    Peut être utilisée indépendamment de Discord.
    
    Args:
        nom_pj: Nom du personnage
        classe: Classe du personnage
        **kwargs: Options supplémentaires (niveau_actuel, niveau_cible, etc.)
        
    Returns:
        str: Template généré
    """
    generator = TemplateGenerator()
    return generator.generate_full_template(nom_pj, classe, **kwargs)

# Vérification des dépendances à l'import
try:
    # Vérifier que les modules requis sont disponibles
    import discord
    from discord import app_commands
    
    # Vérifier la version de discord.py si nécessaire
    discord_version = getattr(discord, '__version__', '0.0.0')
    
    # Marquer le module comme correctement initialisé
    _MODULE_INITIALIZED = True
    
except ImportError as e:
    print(f"⚠️ Erreur d'import dans le module maj_fiche: {e}")
    _MODULE_INITIALIZED = False

def is_module_ready() -> bool:
    """
    Vérifie si le module est correctement initialisé et prêt à utiliser.
    
    Returns:
        bool: True si le module est prêt
    """
    return _MODULE_INITIALIZED

# Fonction de diagnostic pour le debugging
def diagnose_module() -> dict:
    """
    Effectue un diagnostic complet du module maj_fiche.
    Utile pour le debugging et la vérification de l'installation.
    
    Returns:
        dict: Rapport de diagnostic détaillé
    """
    diagnosis = {
        'module_ready': is_module_ready(),
        'version': __version__,
        'components_available': {},
        'dependencies': {},
        'features_working': {}
    }
    
    # Vérifier chaque composant
    try:
        from .main_command import MajFicheBaseCommand
        diagnosis['components_available']['base'] = True
    except Exception as e:
        diagnosis['components_available']['base'] = f"Erreur: {e}"
    
    try:
        from .template_generator import TemplateGenerator
        diagnosis['components_available']['generator'] = True
    except Exception as e:
        diagnosis['components_available']['generator'] = f"Erreur: {e}"
    
    try:
        from .validation_system import TemplateValidator
        diagnosis['components_available']['validator'] = True
    except Exception as e:
        diagnosis['components_available']['validator'] = f"Erreur: {e}"
    
    try:
        from .slash_command_interface import MajFicheSlashCommand
        diagnosis['components_available']['interface'] = True
    except Exception as e:
        diagnosis['components_available']['interface'] = f"Erreur: {e}"
    
    # Vérifier les dépendances externes
    try:
        import discord
        diagnosis['dependencies']['discord'] = getattr(discord, '__version__', 'Version inconnue')
    except ImportError:
        diagnosis['dependencies']['discord'] = "Non disponible"
    
    try:
        from discord import app_commands
        diagnosis['dependencies']['app_commands'] = True
    except ImportError:
        diagnosis['dependencies']['app_commands'] = "Non disponible"
    
    # Tester les fonctionnalités de base
    try:
        # Test de génération de template
        generator = TemplateGenerator()
        test_template = generator.generate_full_template("Test", "Guerrier")
        diagnosis['features_working']['template_generation'] = len(test_template) > 100
    except Exception as e:
        diagnosis['features_working']['template_generation'] = f"Erreur: {e}"
    
    try:
        # Test de validation
        validator = TemplateValidator()
        test_result = validator.verify_template("Test template")
        diagnosis['features_working']['validation'] = 'score' in test_result
    except Exception as e:
        diagnosis['features_working']['validation'] = f"Erreur: {e}"
    
    try:
        # Test d'instanciation de commande
        command = create_command_instance()
        diagnosis['features_working']['command_creation'] = hasattr(command, 'name')
    except Exception as e:
        diagnosis['features_working']['command_creation'] = f"Erreur: {e}"
    
    return diagnosis

# Message d'initialisation pour le debugging
if __name__ == "__main__":
    print("🔍 Diagnostic du module maj_fiche:")
    diag = diagnose_module()
    
    print(f"📦 Version: {diag['version']}")
    print(f"✅ Module prêt: {diag['module_ready']}")
    
    print("\n🧩 Composants:")
    for component, status in diag['components_available'].items():
        status_icon = "✅" if status is True else "❌"
        print(f"  {status_icon} {component}: {status}")
    
    print("\n📚 Dépendances:")
    for dep, status in diag['dependencies'].items():
        status_icon = "✅" if status not in ["Non disponible", False] else "❌"
        print(f"  {status_icon} {dep}: {status}")
    
    print("\n🔧 Fonctionnalités:")
    for feature, status in diag['features_working'].items():
        status_icon = "✅" if status is True else "❌"
        print(f"  {status_icon} {feature}: {status}")
    
    print(f"\n📋 Résumé: Module {'prêt' if diag['module_ready'] else 'non prêt'} à utiliser")

# Configuration par défaut exportée
DEFAULT_CONFIG = {
    'max_template_length': MODULE_CONFIG['discord_limits']['message_length'],
    'safe_template_length': MODULE_CONFIG['discord_limits']['safe_length'],
    'auto_split_templates': True,
    'auto_corrections': True,
    'class_suggestions': True,
    'xp_calculations': True,
    'validation_strict': False
}