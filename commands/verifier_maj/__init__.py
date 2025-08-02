# commands/verifier_maj/__init__.py
"""
Module de vérification de template de mise à jour de fiche D&D.
Structure organisée similaire à maj_fiche avec corrections des erreurs Discord.
"""

import discord
from discord import app_commands
import logging
from typing import Optional
from ..base import BaseCommand

# Imports des modules du package
from .discord_handler import MessageHandler
from .validation_engine import ValidationEngine
from .response_builder import ResponseBuilder

logger = logging.getLogger(__name__)


class VerifierMajCommand(BaseCommand):
    """
    Commande principale pour vérifier les templates de mise à jour de fiche D&D.
    Version refactorisée avec gestion des erreurs Discord corrigée.
    """
    
    def __init__(self, bot):
        super().__init__(bot)
        
        # Initialisation des composants
        self.message_handler = MessageHandler(bot)
        self.validation_engine = ValidationEngine()
        self.response_builder = ResponseBuilder()
        
        logger.info("VerifierMajCommand initialisé avec succès")
    
    @property
    def name(self) -> str:
        return "verifier-maj"
    
    @property
    def description(self) -> str:
        return "Vérifie et propose des corrections pour un template de mise à jour de fiche D&D"
    
    def register(self, tree: app_commands.CommandTree):
        """Enregistrement avec paramètres optimisés et gestion d'erreur corrigée."""
        
        @tree.command(name=self.name, description=self.description)
        @app_commands.describe(
            lien_message="Lien vers le message à vérifier (clic droit > Copier le lien du message)",
            mode_correction="Type de correction à appliquer",
            proposer_ameliorations="Proposer des améliorations supplémentaires"
        )
        @app_commands.choices(mode_correction=[
            app_commands.Choice(name="🔧 Corrections automatiques + suggestions", value="auto"),
            app_commands.Choice(name="📋 Vérification uniquement", value="check"),
            app_commands.Choice(name="✨ Corrections + optimisations avancées", value="advanced")
        ])
        @app_commands.choices(proposer_ameliorations=[
            app_commands.Choice(name="✅ Oui - Suggérer des améliorations", value="oui"),
            app_commands.Choice(name="❌ Non - Validation simple", value="non")
        ])
        async def verifier_maj_command(
            interaction: discord.Interaction,
            lien_message: str,
            mode_correction: str = "auto",
            proposer_ameliorations: str = "oui"
        ):
            await self.callback(
                interaction, 
                lien_message, 
                mode_correction, 
                proposer_ameliorations == "oui"
            )
    
    async def callback(
        self, 
        interaction: discord.Interaction, 
        lien_message: str,
        mode_correction: str = "auto",
        proposer_ameliorations: bool = True
    ):
        """Fonction principale ultra-simplifiée avec gestion d'erreur corrigée."""
        
        try:
            # Différer la réponse immédiatement pour éviter les timeouts
            await interaction.response.defer(ephemeral=True)
            
            logger.info(f"Début de vérification pour {interaction.user} - Lien: {lien_message[:50]}...")
            
            # 1. Valider le format du lien
            if not self.message_handler.validate_link_format(lien_message):
                await self.response_builder.send_link_validation_error(interaction, lien_message)
                return
            
            # 2. Récupérer le message
            message = await self.message_handler.get_message_from_link(lien_message)
            if not message:
                await self.response_builder.send_message_not_found_error(interaction)
                return
            
            # 3. Vérifier que le message contient du contenu
            if not message.content or len(message.content.strip()) < 20:
                await self.response_builder.send_error(
                    interaction, 
                    "Le message sélectionné ne contient pas assez de contenu pour être analysé.",
                    "📝 Contenu insuffisant"
                )
                return
            
            logger.info(f"Message récupéré: {len(message.content)} caractères")
            
            # 4. Valider le template
            result = self.validation_engine.validate_template(message.content, mode_correction)
            
            logger.info(f"Validation terminée: {result.get('completion_percentage', 0):.1f}%")
            
            # 5. Envoyer la réponse
            await self.response_builder.send_validation_result(
                interaction, message, result, proposer_ameliorations
            )
            
            logger.info(f"Vérification terminée avec succès pour {interaction.user}")
            
        except discord.InteractionResponded:
            # L'interaction a déjà été traitée - ne rien faire
            logger.warning(f"Interaction déjà traitée pour {interaction.user}")
            
        except Exception as e:
            logger.error(f"Erreur dans verifier-maj pour {interaction.user}: {e}", exc_info=True)
            
            # Essayer d'envoyer une réponse d'erreur
            await self.response_builder.send_error(
                interaction,
                f"Une erreur inattendue s'est produite lors de la vérification.\n\n"
                f"**Type d'erreur :** {type(e).__name__}\n"
                f"**Message :** {str(e)[:200]}...\n\n"
                f"💡 **Solutions :**\n"
                f"• Vérifiez que le lien est correct et complet\n"
                f"• Réessayez dans quelques instants\n"
                f"• Contactez un administrateur si le problème persiste",
                "⚠️ Erreur inattendue"
            )


# Fonctions utilitaires exportées
def validate_template_content(content: str, mode: str = "auto") -> dict:
    """
    Fonction utilitaire pour valider un template de fiche.
    Peut être utilisée indépendamment de Discord.
    
    Args:
        content: Le contenu du template à valider
        mode: Mode de validation ("auto", "check", "advanced")
        
    Returns:
        dict: Résultat de la validation avec score et suggestions
    """
    try:
        engine = ValidationEngine()
        return engine.validate_template(content, mode)
    except Exception as e:
        logger.error(f"Erreur dans validate_template_content: {e}")
        return {
            'score': 0,
            'total_checks': 1,
            'completion_percentage': 0.0,
            'warnings': [f"Erreur de validation: {str(e)}"]
        }


def quick_template_check(content: str) -> bool:
    """
    Vérification rapide pour savoir si un contenu ressemble à un template.
    
    Args:
        content: Le contenu à vérifier
        
    Returns:
        bool: True si le contenu semble être un template valide
    """
    try:
        engine = ValidationEngine()
        return engine.quick_validate(content)
    except Exception:
        return False


def parse_discord_link(link: str) -> Optional[tuple]:
    """
    Parse un lien Discord et retourne les IDs.
    
    Args:
        link: Lien Discord à parser
        
    Returns:
        Optional[tuple]: (guild_id, channel_id, message_id) ou None
    """
    try:
        handler = MessageHandler(None)  # Bot non nécessaire pour le parsing
        return handler.parse_discord_link(link)
    except Exception:
        return None


# Classes exportées pour réutilisation
__all__ = [
    'VerifierMajCommand',      # Commande principale
    'MessageHandler',          # Gestionnaire de messages Discord
    'ValidationEngine',        # Moteur de validation
    'ResponseBuilder',         # Constructeur de réponses
    'validate_template_content', # Fonction utilitaire
    'quick_template_check',    # Vérification rapide
    'parse_discord_link'       # Parser de liens
]

# Métadonnées du module
__version__ = "1.0.0"
__author__ = "Bot Faerûn Team"
__description__ = "Système de vérification de templates D&D 5e - Version refactorisée"

# Configuration du module
MODULE_CONFIG = {
    'version': __version__,
    'components': {
        'handler': 'MessageHandler - Gestion des liens et messages Discord',
        'engine': 'ValidationEngine - Validation et correction des templates', 
        'builder': 'ResponseBuilder - Construction des réponses Discord',
        'command': 'VerifierMajCommand - Commande principale'
    },
    'features': [
        'Validation de templates D&D 5e',
        'Corrections automatiques',
        'Support des liens Discord',
        'Gestion des limites Discord',
        'Réponses structurées',
        'Gestion d\'erreurs robuste'
    ],
    'fixes': [
        'Correction limite de 1024 caractères pour les champs',
        'Gestion des interactions déjà répondues',
        'Protection contre les timeouts Discord',
        'Division automatique des contenus longs',
        'Validation des liens améliorée'
    ]
}


def get_module_info() -> dict:
    """
    Retourne les informations sur le module verifier_maj.
    
    Returns:
        dict: Informations complètes du module
    """
    return MODULE_CONFIG


def create_command_instance(bot):
    """
    Factory function pour créer une instance de la commande principale.
    
    Args:
        bot: Instance du bot Discord
        
    Returns:
        VerifierMajCommand: Instance configurée de la commande
    """
    return VerifierMajCommand(bot)


# Diagnostic pour le debugging
def diagnose_module() -> dict:
    """
    Effectue un diagnostic du module verifier_maj.
    
    Returns:
        dict: Rapport de diagnostic
    """
    diagnosis = {
        'module_ready': True,
        'version': __version__,
        'components_available': {},
        'features_working': {}
    }
    
    # Vérifier chaque composant
    try:
        from .discord_handler import MessageHandler
        diagnosis['components_available']['handler'] = True
    except Exception as e:
        diagnosis['components_available']['handler'] = f"Erreur: {e}"
        diagnosis['module_ready'] = False
    
    try:
        from .validation_engine import ValidationEngine
        diagnosis['components_available']['engine'] = True
    except Exception as e:
        diagnosis['components_available']['engine'] = f"Erreur: {e}"
        diagnosis['module_ready'] = False
    
    try:
        from .response_builder import ResponseBuilder
        diagnosis['components_available']['builder'] = True
    except Exception as e:
        diagnosis['components_available']['builder'] = f"Erreur: {e}"
        diagnosis['module_ready'] = False
    
    # Tester les fonctionnalités
    try:
        result = quick_template_check("Nom: Test\nClasse: Guerrier\nNiveau: 5")
        diagnosis['features_working']['quick_check'] = result
    except Exception as e:
        diagnosis['features_working']['quick_check'] = f"Erreur: {e}"
    
    try:
        parsed = parse_discord_link("https://discord.com/channels/123/456/789")
        diagnosis['features_working']['link_parsing'] = parsed is not None
    except Exception as e:
        diagnosis['features_working']['link_parsing'] = f"Erreur: {e}"
    
    return diagnosis


# Message d'initialisation pour le debugging
if __name__ == "__main__":
    print("🔍 Diagnostic du module verifier_maj:")
    diag = diagnose_module()
    
    print(f"📦 Version: {diag['version']}")
    print(f"✅ Module prêt: {diag['module_ready']}")
    
    print("\n🧩 Composants:")
    for component, status in diag['components_available'].items():
        status_icon = "✅" if status is True else "❌"
        print(f"  {status_icon} {component}: {status}")
    
    print("\n🔧 Fonctionnalités:")
    for feature, status in diag['features_working'].items():
        status_icon = "✅" if status is True else "❌"
        print(f"  {status_icon} {feature}: {status}")
    
    print(f"\n📋 Résumé: Module {'prêt' if diag['module_ready'] else 'non prêt'} à utiliser")