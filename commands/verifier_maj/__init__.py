"""
Module de vérification de template de mise à jour de fiche D&D.
Structure organisée similaire à maj_fiche.
"""

from .discord_handler import MessageHandler
from .validation_engine import ValidationEngine
from .response_builder import ResponseBuilder
from ..base import BaseCommand

class VerifierMajCommand(BaseCommand):
    """Commande principale simplifiée pour vérifier les templates."""
    
    def __init__(self, bot):
        super().__init__(bot)
        self.message_handler = MessageHandler(bot)
        self.validation_engine = ValidationEngine()
        self.response_builder = ResponseBuilder()
    
    @property
    def name(self) -> str:
        return "verifier-maj"
    
    @property
    def description(self) -> str:
        return "Vérifie et propose des corrections pour un template de mise à jour de fiche D&D"
    
    async def callback(self, interaction, lien_message, mode_correction="auto", proposer_ameliorations=True):
        """Fonction principale ultra-simplifiée."""
        try:
            # 1. Récupérer le message
            message = await self.message_handler.get_message_from_link(lien_message)
            if not message:
                await self.response_builder.send_error(interaction, "Message introuvable")
                return
            
            # 2. Valider le template
            result = self.validation_engine.validate_template(message.content, mode_correction)
            
            # 3. Envoyer la réponse
            await self.response_builder.send_validation_result(
                interaction, message, result, proposer_ameliorations
            )
            
        except Exception as e:
            await self.response_builder.send_error(interaction, str(e))