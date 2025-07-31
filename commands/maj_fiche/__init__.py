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
    command = MajFicheCommand(bot)  # CORRECTION: Passer le bot
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

# CORRECTION CRITIQUE: Adapter la classe pour hériter de BaseCommand
from ..base import BaseCommand
import discord
from discord import app_commands
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class MajFicheCommand(BaseCommand):
    """
    Commande principale maj-fiche adaptée pour le système de bot Faerûn.
    CORRECTION: Hérite maintenant de BaseCommand pour compatibilité système.
    """
    
    def __init__(self, bot):
        super().__init__(bot)
        self.slash_command = MajFicheSlashCommand(bot)  # ✅ CORRECTION: Passage de bot
        self.template_generator = TemplateGenerator()
    
    @property
    def name(self) -> str:
        return "maj-fiche"
    
    @property
    def description(self) -> str:
        return "Génère un template de mise à jour de fiche de personnage D&D"
    
    # ... reste de la classe identique ...
    
    def register(self, tree: app_commands.CommandTree):
        """
        Enregistrement personnalisé avec tous les paramètres Discord.
        CORRECTION: Utilise la logique du slash_command mais dans le format BaseCommand
        """
        
        @tree.command(name=self.name, description=self.description)
        @app_commands.describe(
            nom_pj="Nom du personnage",
            classe="Classe du personnage", 
            niveau_actuel="Niveau actuel du personnage",
            niveau_cible="Nouveau niveau visé (optionnel)",
            titre_quete="Titre de la quête (optionnel)",
            mj="Nom du MJ (optionnel)",
            xp_actuels="XP actuels (optionnel)",
            xp_obtenus="XP obtenus cette session (optionnel)",
            include_marchand="Inclure la section Marchand",
            include_inventaire="Inclure la section Inventaire détaillée"
        )
        @app_commands.choices(classe=self.slash_command.CLASSES_CHOICES)
        @app_commands.choices(niveau_actuel=self.slash_command.NIVEAUX_ACTUELS)
        @app_commands.choices(niveau_cible=self.slash_command.NIVEAUX_CIBLES)
        @app_commands.choices(include_marchand=[
            app_commands.Choice(name="✅ Oui - Inclure section Marchand", value="oui"),
            app_commands.Choice(name="❌ Non - Pas de section Marchand", value="non")
        ])
        @app_commands.choices(include_inventaire=[
            app_commands.Choice(name="✅ Oui - Inventaire détaillé", value="oui"),
            app_commands.Choice(name="❌ Non - Inventaire minimal", value="non")
        ])
        async def maj_fiche_command(
            interaction: discord.Interaction,
            nom_pj: str,
            classe: str,
            niveau_actuel: Optional[int] = None,
            niveau_cible: Optional[int] = None,
            titre_quete: Optional[str] = None,
            mj: Optional[str] = None,
            xp_actuels: Optional[int] = None,
            xp_obtenus: Optional[int] = None,
            include_marchand: str = "non",
            include_inventaire: str = "oui"
        ):
            # CORRECTION: Déléguer à la méthode callback avec les bons paramètres
            await self.callback(
                interaction, nom_pj, classe, niveau_actuel, niveau_cible,
                titre_quete, mj, xp_actuels, xp_obtenus, 
                include_marchand == "oui", include_inventaire == "oui"
            )
    
    async def callback(
        self, 
        interaction: discord.Interaction,
        nom_pj: str,
        classe: str,
        niveau_actuel: Optional[int] = None,
        niveau_cible: Optional[int] = None,
        titre_quete: Optional[str] = None,
        mj: Optional[str] = None,
        xp_actuels: Optional[int] = None,
        xp_obtenus: Optional[int] = None,
        include_marchand: bool = False,
        include_inventaire: bool = True
    ):
        """
        Callback principal - délègue à la logique du slash_command.
        CORRECTION: Point d'entrée unifié compatible BaseCommand
        """
        
        # CORRECTION: Utiliser la logique corrigée du slash_command
        await self.slash_command.callback(
            interaction, nom_pj, classe, niveau_actuel, niveau_cible,
            titre_quete, mj, xp_actuels, xp_obtenus, 
            include_marchand, include_inventaire
        )


# Classes utilitaires accessibles pour extension (gardées pour compatibilité)
__all__ = [
    'MajFicheCommand',           # Commande principale (export principal) - CORRIGÉE
    'MajFicheBaseCommand',       # Classe de base pour extensions
    'TemplateGenerator',         # Générateur de templates
    'TemplateValidator',         # Système de validation  
    'MajFicheSlashCommand'       # Interface Discord complète
]

# Métadonnées du module
__version__ = "2.0.1"  # Version corrigée
__author__ = "Bot Faerûn Team"
__description__ = "Système complet de mise à jour de fiche D&D 5e - Compatible BaseCommand"

# Configuration du module
MODULE_CONFIG = {
    'version': __version__,
    'components': {
        'base': 'MajFicheBaseCommand - Logique commune et validations',
        'generator': 'TemplateGenerator - Génération de templates personnalisés', 
        'validator': 'TemplateValidator - Validation et corrections automatiques',
        'interface': 'MajFicheSlashCommand - Interface Discord complète',
        'wrapper': 'MajFicheCommand - Wrapper compatible BaseCommand'  # NOUVEAU
    },
    'features': [
        'Templates D&D 5e personnalisés',
        'Suggestions par classe/niveau', 
        'Validation automatique',
        'Corrections intelligentes',
        'Gestion longueur Discord',
        'Calculs XP/PV automatiques',
        'Compatible système BaseCommand'  # NOUVEAU
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

def create_command_instance(bot):
    """
    Factory function pour créer une instance de la commande principale.
    CORRECTION: Prend maintenant le bot en paramètre pour compatibilité BaseCommand.
    
    Args:
        bot: Instance du bot Discord
        
    Returns:
        MajFicheCommand: Instance configurée de la commande compatible BaseCommand
    """
    return MajFicheCommand(bot)

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
        'features_working': {},
        'basecommand_compatible': True  # NOUVEAU
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
        
    try:
        from ..base import BaseCommand
        diagnosis['components_available']['basecommand'] = True
    except Exception as e:
        diagnosis['components_available']['basecommand'] = f"Erreur: {e}"
        diagnosis['basecommand_compatible'] = False
    
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
    
    # NOUVEAU: Test de compatibilité BaseCommand
    try:
        # Test d'instanciation de commande compatible BaseCommand
        # Simulation d'un bot pour le test
        class MockBot:
            pass
        
        mock_bot = MockBot()
        command = MajFicheCommand(mock_bot)
        diagnosis['features_working']['basecommand_creation'] = hasattr(command, 'name') and hasattr(command, 'bot')
    except Exception as e:
        diagnosis['features_working']['basecommand_creation'] = f"Erreur: {e}"
    
    return diagnosis

# Configuration par défaut exportée
DEFAULT_CONFIG = {
    'max_template_length': MODULE_CONFIG['discord_limits']['message_length'],
    'safe_template_length': MODULE_CONFIG['discord_limits']['safe_length'],
    'auto_split_templates': True,
    'auto_corrections': True,
    'class_suggestions': True,
    'xp_calculations': True,
    'validation_strict': False,
    'basecommand_compatible': True  # NOUVEAU
}

# Message d'initialisation pour le debugging
if __name__ == "__main__":
    print("🔍 Diagnostic du module maj_fiche:")
    diag = diagnose_module()
    
    print(f"📦 Version: {diag['version']}")
    print(f"✅ Module prêt: {diag['module_ready']}")
    print(f"🔧 BaseCommand compatible: {diag['basecommand_compatible']}")
    
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
    
    print(f"\n📋 Résumé: Module {'prêt' if diag['module_ready'] and diag['basecommand_compatible'] else 'non prêt'} à utiliser")