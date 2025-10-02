# commands/postulation/main_command.py
"""
Commande principale pour la postulation des joueurs.
"""

import discord
from discord import app_commands
import logging
from typing import Optional, Dict

from ..base import BaseCommand
from .config import get_config, validate_config
from .google_sheets_client import GoogleSheetsClient
from .character_selector import CharacterSelector
from .modal_rp import (
    CharacterSelectView, 
    PostulationRPModal,
    create_character_selection_embed
)

logger = logging.getLogger(__name__)


class PostulationCommand(BaseCommand):
    """Commande Discord pour la postulation des joueurs."""
    
    def __init__(self, bot):
        """
        Initialise la commande postulation.
        
        Args:
            bot: Instance du bot Discord
        """
        super().__init__(bot)
        
        # Valider la configuration
        if not validate_config():
            logger.error("❌ Configuration postulation invalide")
            raise ValueError("Configuration postulation invalide")
        
        # Charger la configuration
        self.config = get_config()
        self.google_config = self.config['google_sheets']
        self.discord_config = self.config['discord']
        self.messages = self.config['messages']
        
        # Initialiser les composants
        self.sheets_client = GoogleSheetsClient(self.google_config['sheet_id'])
        self.character_selector = CharacterSelector()
        
        logger.info("✅ PostulationCommand initialisé")
        logger.info(f"   • Sheet: {self.google_config['sheet_name']}")
        logger.info(f"   • Use Webhook: {self.discord_config['use_webhook']}")
    
    @property
    def name(self) -> str:
        """Nom de la commande."""
        return "postuler"
    
    @property
    def description(self) -> str:
        """Description de la commande."""
        return "Postuler à une quête avec l'un de vos personnages"
    
    async def callback(self, interaction: discord.Interaction):
        """
        Fonction appelée lors de l'exécution de /postuler.
        
        Args:
            interaction: Interaction Discord
        """
        user = interaction.user
        discord_id = str(user.id)
        
        logger.info(f"📝 Commande /postuler utilisée par {user.name} (ID: {discord_id})")
        
        # Réponse immédiate (defer)
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Récupérer les personnages du joueur
            logger.info(f"Récupération des personnages pour {user.name}")
            
            raw_characters = await self.sheets_client.get_player_characters(
                discord_id=discord_id,
                sheet_name=self.google_config['sheet_name'],
                gid=self.google_config['sheet_gid'],
                columns_config=self.config['columns']
            )
            
            if not raw_characters:
                logger.warning(f"Aucun personnage trouvé pour {user.name}")
                await interaction.followup.send(
                    f"❌ {self.messages['no_characters']}\n\n"
                    f"**Votre ID Discord :** `{discord_id}`\n"
                    f"Vérifiez que cet ID est bien enregistré dans le tableau des personnages.",
                    ephemeral=True
                )
                return
            
            logger.info(f"Trouvé {len(raw_characters)} personnage(s) brut(s)")
            
            # Préparer les personnages pour la sélection
            formatted_characters = self.character_selector.prepare_characters_for_select_menu(
                raw_characters
            )
            
            if not formatted_characters:
                await interaction.followup.send(
                    "❌ Aucun personnage actif disponible.\n\n"
                    "Vérifiez que vos personnages ont le statut **ACTIF** dans le tableau.",
                    ephemeral=True
                )
                return
            
            logger.info(f"✅ {len(formatted_characters)} personnage(s) actif(s) disponible(s)")
            
            # Créer l'embed de sélection
            embed = create_character_selection_embed(user, len(formatted_characters))
            
            # Créer la vue de sélection avec callback
            view = CharacterSelectView(
                characters=formatted_characters,
                user=user,
                callback_func=self._handle_postulation_submission
            )
            
            # Envoyer le message avec le menu de sélection
            await interaction.followup.send(
                embed=embed,
                view=view,
                ephemeral=True
            )
            
            logger.info(f"✅ Menu de sélection envoyé à {user.name}")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'exécution de /postuler: {e}", exc_info=True)
            
            error_message = (
                f"❌ {self.messages['error_loading']}\n\n"
                f"**Détails de l'erreur :** {str(e)}"
            )
            
            try:
                await interaction.followup.send(error_message, ephemeral=True)
            except:
                logger.error("Impossible d'envoyer le message d'erreur")
    
    async def _handle_postulation_submission(
        self,
        interaction: discord.Interaction,
        character: Dict[str, str],
        rp_message: str,
        user: discord.User
    ):
        """
        Gère la soumission de la postulation après le modal.
        
        Args:
            interaction: Interaction Discord
            character: Personnage sélectionné
            rp_message: Message RP saisi
            user: Utilisateur qui a posté
        """
        logger.info(f"📨 Soumission postulation: {user.name} avec {character['nom_pj']}")
        
        try:
            # Créer l'embed de postulation
            embed = self._create_postulation_embed(character, rp_message, user)
            
            # Déterminer où poster (thread ou channel)
            target_channel = interaction.channel
            
            # Vérifier si on peut utiliser un webhook
            if self.discord_config['use_webhook'] and self.discord_config['webhook_fallback']:
                success = await self._post_with_webhook(
                    target_channel, 
                    embed, 
                    user,
                    character
                )
                
                if not success:
                    # Fallback: poster avec le bot + mention
                    await self._post_with_bot(target_channel, embed, user)
            else:
                # Poster directement avec le bot
                await self._post_with_bot(target_channel, embed, user)
            
            # Confirmer à l'utilisateur
            await interaction.response.send_message(
                f"✅ {self.messages['success']}\n\n"
                f"Votre postulation avec **{character['nom_pj']}** a été envoyée !",
                ephemeral=True
            )
            
            logger.info(f"✅ Postulation envoyée avec succès pour {user.name}")
            
        except Exception as e:
            logger.error(f"Erreur lors de la soumission de postulation: {e}", exc_info=True)
            
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    "❌ Une erreur est survenue lors de l'envoi de votre postulation.",
                    ephemeral=True
                )
            else:
                await interaction.followup.send(
                    "❌ Une erreur est survenue lors de l'envoi de votre postulation.",
                    ephemeral=True
                )
    
    def _create_postulation_embed(
        self, 
        character: Dict[str, str], 
        rp_message: str,
        user: discord.User
    ) -> discord.Embed:
        """
        Crée l'embed de postulation.
        
        Args:
            character: Personnage sélectionné
            rp_message: Message RP
            user: Utilisateur
            
        Returns:
            discord.Embed: Embed formaté
        """
        embed = discord.Embed(
            title=self.messages['title'],
            description=f"**{character['nom_pj']}** ({user.mention})",
            color=self.discord_config['embed_color']
        )
        
        # Informations du personnage
        embed.add_field(
            name="🧝 Race",
            value=character['race'],
            inline=True
        )
        
        embed.add_field(
            name="⚔️ Classe",
            value=character['classes'],
            inline=True
        )
        
        embed.add_field(
            name="📊 Niveau",
            value=character['niveau_total'],
            inline=True
        )
        
        # Message RP
        embed.add_field(
            name="📜 Message RP",
            value=f">>> {rp_message}",
            inline=False
        )
        
        # Image du token si disponible
        if character.get('token_url'):
            embed.set_thumbnail(url=character['token_url'])
        
        # Footer avec info du joueur
        embed.set_footer(
            text=f"Postulé par {user.name}",
            icon_url=user.display_avatar.url if user.display_avatar else None
        )
        
        embed.timestamp = discord.utils.utcnow()
        
        return embed
    
    async def _post_with_webhook(
        self, 
        channel: discord.TextChannel,
        embed: discord.Embed,
        user: discord.User,
        character: Dict[str, str]
    ) -> bool:
        """
        Poste la postulation via un webhook (apparaît comme le joueur).
        
        Args:
            channel: Canal où poster
            embed: Embed à envoyer
            user: Utilisateur
            character: Personnage
            
        Returns:
            bool: True si succès, False si échec
        """
        try:
            # Vérifier les permissions
            if not channel.permissions_for(channel.guild.me).manage_webhooks:
                logger.warning("Pas de permission manage_webhooks, fallback sur bot")
                return False
            
            # Chercher un webhook existant du bot
            webhooks = await channel.webhooks()
            bot_webhook = None
            
            for webhook in webhooks:
                if webhook.user == channel.guild.me:
                    bot_webhook = webhook
                    break
            
            # Créer un webhook si nécessaire
            if not bot_webhook:
                bot_webhook = await channel.create_webhook(
                    name="Postulation Bot",
                    reason="Webhook pour postulations de quêtes"
                )
                logger.info(f"Webhook créé dans {channel.name}")
            
            # Envoyer via le webhook avec le nom et avatar du joueur
            await bot_webhook.send(
                embed=embed,
                username=user.display_name,
                avatar_url=user.display_avatar.url if user.display_avatar else None
            )
            
            logger.info(f"✅ Postulation envoyée via webhook pour {user.name}")
            return True
            
        except discord.Forbidden:
            logger.warning("Permissions insuffisantes pour webhook")
            return False
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi via webhook: {e}")
            return False
    
    async def _post_with_bot(
        self,
        channel: discord.TextChannel,
        embed: discord.Embed,
        user: discord.User
    ):
        """
        Poste la postulation directement avec le bot.
        
        Args:
            channel: Canal où poster
            embed: Embed à envoyer
            user: Utilisateur
        """
        try:
            await channel.send(
                content=f"**Postulation de {user.mention}**",
                embed=embed
            )
            logger.info(f"✅ Postulation envoyée avec le bot pour {user.name}")
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi avec le bot: {e}")
            raise


# Fonction d'export pour __init__.py
def setup(bot):
    """
    Configure la commande postulation.
    
    Args:
        bot: Instance du bot Discord
    """
    return PostulationCommand(bot)


if __name__ == "__main__":
    print("🧪 Test du module main_command")
    print("=" * 60)
    
    # Vérifier que la configuration est valide
    print("\n📋 Validation de la configuration")
    if validate_config():
        print("✅ Configuration valide")
        
        config = get_config()
        print(f"\n🔧 Configuration chargée:")
        print(f"   • Sheet ID: {config['google_sheets']['sheet_id'][:20]}...")
        print(f"   • Sheet Name: {config['google_sheets']['sheet_name']}")
        print(f"   • Use Webhook: {config['discord']['use_webhook']}")
        print(f"   • Max RP Length: {config['discord']['max_rp_length']}")
    else:
        print("❌ Configuration invalide")
    
    print("\n" + "=" * 60)
    print("✅ Tests terminés")
    print("\nNote: Les tests complets nécessitent un bot Discord actif")