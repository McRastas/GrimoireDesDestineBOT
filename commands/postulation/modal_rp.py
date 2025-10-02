# commands/postulation/modal_rp.py
"""
Modal Discord pour saisir le message RP de postulation.
"""

import discord
import logging
from typing import Dict, Optional, Callable
from .config import get_config

logger = logging.getLogger(__name__)


class PostulationRPModal(discord.ui.Modal):
    """Modal pour saisir le message RP de postulation."""
    
    def __init__(
        self, 
        character: Dict[str, str],
        callback_func: Callable,
        user: discord.User
    ):
        """
        Initialise le modal RP.
        
        Args:
            character: Personnage sélectionné (données formatées)
            callback_func: Fonction à appeler après soumission
            user: Utilisateur Discord qui a ouvert le modal
        """
        config = get_config()
        messages = config['messages']
        discord_config = config['discord']
        
        title = f"Postulation - {character['nom_pj']}"
        
        # Limiter le titre à 45 caractères (limite Discord)
        if len(title) > 45:
            title = f"Postulation - {character['nom_pj'][:30]}..."
        
        super().__init__(title=title, timeout=300)  # 5 minutes de timeout
        
        self.character = character
        self.callback_func = callback_func
        self.user = user
        self.max_length = discord_config['max_rp_length']
        
        # Champ de texte pour le message RP
        self.rp_message = discord.ui.TextInput(
            label=messages['rp_label'],
            style=discord.TextStyle.paragraph,  # Texte multiligne
            placeholder=messages['rp_placeholder'],
            required=True,
            min_length=10,
            max_length=self.max_length
        )
        
        self.add_item(self.rp_message)
        
        logger.debug(f"Modal RP créé pour {character['nom_pj']} par {user.name}")
    
    async def on_submit(self, interaction: discord.Interaction):
        """
        Appelé quand l'utilisateur soumet le modal.
        
        Args:
            interaction: Interaction Discord
        """
        rp_text = self.rp_message.value.strip()
        
        logger.info(f"Modal RP soumis par {self.user.name} pour {self.character['nom_pj']}")
        logger.debug(f"Message RP: {rp_text[:100]}...")
        
        # Vérifier la longueur du message
        if len(rp_text) < 10:
            await interaction.response.send_message(
                "❌ Votre message RP est trop court (minimum 10 caractères).",
                ephemeral=True
            )
            return
        
        # Appeler la fonction callback avec les données
        try:
            await self.callback_func(
                interaction=interaction,
                character=self.character,
                rp_message=rp_text,
                user=self.user
            )
        except Exception as e:
            logger.error(f"Erreur lors du callback du modal: {e}", exc_info=True)
            
            # Si l'interaction n'a pas encore été répondue
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
    
    async def on_error(self, interaction: discord.Interaction, error: Exception):
        """
        Appelé en cas d'erreur dans le modal.
        
        Args:
            interaction: Interaction Discord
            error: Exception levée
        """
        logger.error(f"Erreur dans le modal RP: {error}", exc_info=True)
        
        try:
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    "❌ Une erreur est survenue. Veuillez réessayer.",
                    ephemeral=True
                )
            else:
                await interaction.followup.send(
                    "❌ Une erreur est survenue. Veuillez réessayer.",
                    ephemeral=True
                )
        except:
            logger.error("Impossible d'envoyer le message d'erreur")


class CharacterSelectView(discord.ui.View):
    """View avec menu de sélection de personnage."""
    
    def __init__(
        self, 
        characters: list[Dict[str, str]],
        user: discord.User,
        callback_func: Callable
    ):
        """
        Initialise la vue de sélection.
        
        Args:
            characters: Liste des personnages formatés
            user: Utilisateur Discord
            callback_func: Fonction callback après sélection
        """
        super().__init__(timeout=180)  # 3 minutes de timeout
        self.characters = characters
        self.user = user
        self.callback_func = callback_func
        
        # Importer le sélecteur pour les fonctions utilitaires
        from .character_selector import CharacterSelector
        self.selector = CharacterSelector()
        
        # Créer le menu de sélection
        self.create_select_menu()
        
        logger.debug(f"Vue de sélection créée avec {len(characters)} personnages pour {user.name}")
    
    def create_select_menu(self):
        """Crée le menu de sélection de personnage."""
        config = get_config()
        messages = config['messages']
        
        # Créer les options du menu
        options = []
        for char in self.characters:
            option = discord.SelectOption(
                label=self.selector.create_select_option_label(char),
                description=self.selector.create_select_option_description(char),
                value=char['nom_pj']  # Utiliser le nom comme valeur unique
            )
            options.append(option)
        
        # Créer le SelectMenu
        select = discord.ui.Select(
            placeholder=messages['select_placeholder'],
            min_values=1,
            max_values=1,
            options=options
        )
        
        # Définir le callback
        select.callback = self.select_callback
        
        # Ajouter le menu à la vue
        self.add_item(select)
    
    async def select_callback(self, interaction: discord.Interaction):
        """
        Appelé quand un personnage est sélectionné.
        
        Args:
            interaction: Interaction Discord
        """
        # Vérifier que c'est bien l'utilisateur qui a créé la vue
        if interaction.user.id != self.user.id:
            await interaction.response.send_message(
                "❌ Ce menu n'est pas pour vous !",
                ephemeral=True
            )
            return
        
        # Récupérer le personnage sélectionné
        selected_name = interaction.data['values'][0]
        selected_character = self.selector.find_character_by_name(
            self.characters, 
            selected_name
        )
        
        if not selected_character:
            logger.error(f"Personnage non trouvé: {selected_name}")
            await interaction.response.send_message(
                "❌ Erreur: personnage non trouvé.",
                ephemeral=True
            )
            return
        
        logger.info(f"{self.user.name} a sélectionné {selected_name}")
        
        # Ouvrir le modal pour saisir le message RP
        modal = PostulationRPModal(
            character=selected_character,
            callback_func=self.callback_func,
            user=self.user
        )
        
        await interaction.response.send_modal(modal)
    
    async def on_timeout(self):
        """Appelé quand la vue expire."""
        logger.debug(f"Vue de sélection expirée pour {self.user.name}")
        # Désactiver tous les composants
        for item in self.children:
            item.disabled = True


class PostulationCancelButton(discord.ui.Button):
    """Bouton pour annuler une postulation."""
    
    def __init__(self):
        super().__init__(
            label="❌ Annuler",
            style=discord.ButtonStyle.danger,
            custom_id="postulation_cancel"
        )
    
    async def callback(self, interaction: discord.Interaction):
        """Appelé quand le bouton est cliqué."""
        await interaction.response.send_message(
            "✅ Postulation annulée.",
            ephemeral=True
        )
        
        # Supprimer le message original
        try:
            await interaction.message.delete()
        except:
            logger.warning("Impossible de supprimer le message de sélection")


def create_character_selection_embed(user: discord.User, character_count: int) -> discord.Embed:
    """
    Crée l'embed pour la sélection de personnage.
    
    Args:
        user: Utilisateur Discord
        character_count: Nombre de personnages disponibles
        
    Returns:
        discord.Embed: Embed de sélection
    """
    config = get_config()
    discord_config = config['discord']
    
    embed = discord.Embed(
        title="🎭 Sélection de personnage",
        description=(
            f"**{user.mention}**, choisissez le personnage avec lequel vous souhaitez postuler.\n\n"
            f"📊 **{character_count} personnage(s) disponible(s)**"
        ),
        color=discord_config['embed_color']
    )
    
    embed.add_field(
        name="📝 Étapes",
        value=(
            "1️⃣ Sélectionnez votre personnage dans le menu\n"
            "2️⃣ Rédigez votre message RP\n"
            "3️⃣ Validez votre postulation"
        ),
        inline=False
    )
    
    embed.set_footer(text="⏱️ Vous avez 3 minutes pour sélectionner votre personnage")
    
    return embed


if __name__ == "__main__":
    print("🧪 Test du module modal_rp")
    print("=" * 60)
    
    # Test de création d'embed
    print("\n📋 Test de création d'embed de sélection")
    
    # Simuler un utilisateur (pour test uniquement)
    class MockUser:
        def __init__(self):
            self.name = "TestUser"
            self.id = 123456789
            self.mention = "@TestUser"
    
    user = MockUser()
    embed = create_character_selection_embed(user, 3)
    
    print(f"✅ Embed créé:")
    print(f"   • Titre: {embed.title}")
    print(f"   • Description: {embed.description[:50]}...")
    print(f"   • Couleur: {hex(embed.color.value)}")
    print(f"   • Champs: {len(embed.fields)}")
    
    print("\n" + "=" * 60)
    print("✅ Tests terminés")
    print("\nNote: Les tests complets nécessitent un environnement Discord")