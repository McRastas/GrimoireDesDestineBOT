# commands/maj_fiche/slash_command_interface.py
import discord
from discord import app_commands
from typing import Optional
import logging
from .main_command import MajFicheBaseCommand
from .template_generator import TemplateGenerator

logger = logging.getLogger(__name__)


class MajFicheSlashCommand(MajFicheBaseCommand):
    """
    Interface de commande slash Discord pour la mise à jour de fiche.
    Gère l'enregistrement des paramètres et l'interaction avec Discord.
    VERSION CORRIGÉE - Gestion simplifiée des réponses Discord
    """

    def __init__(self, bot):  # ✅ AJOUT du paramètre bot
        super().__init__(bot)   # ✅ PASSAGE de bot au parent
        self.template_generator = TemplateGenerator()

    # ... reste du fichier inchangé ...

    @property
    def name(self) -> str:
        return "maj-fiche"

    @property
    def description(self) -> str:
        return "Génère un template de mise à jour de fiche de personnage D&D"

    def register(self, tree: app_commands.CommandTree):
        """Enregistrement de la commande slash avec tous les paramètres et choix."""

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
        @app_commands.choices(classe=self.CLASSES_CHOICES)
        @app_commands.choices(niveau_actuel=self.NIVEAUX_ACTUELS)
        @app_commands.choices(niveau_cible=self.NIVEAUX_CIBLES)
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
        Traite la commande et génère le template de mise à jour.
        VERSION CORRIGÉE - Gestion d'erreur robuste et réponses simplifiées
        """
        try:
            # CORRECTION 1: DEFER au lieu de response.send_message
            # Évite les conflits de réponse Discord
            await interaction.response.defer(ephemeral=True)
            
            logger.info(f"Génération template pour {nom_pj} ({classe}) par {interaction.user}")
            
            # Validation des paramètres d'entrée
            validation_errors = self.validate_parameters(
                nom_pj, classe, niveau_actuel, niveau_cible, xp_actuels, xp_obtenus
            )
            
            # CORRECTION 2: Validation de base pour éviter les erreurs de génération
            if not nom_pj or not nom_pj.strip():
                await interaction.followup.send(
                    "❌ **Erreur de paramètres**\n\nLe nom du personnage ne peut pas être vide.",
                    ephemeral=True
                )
                return
            
            # Génération du template avec gestion d'erreur
            try:
                template = self.template_generator.generate_full_template(
                    nom_pj=nom_pj.strip(),
                    classe=classe,
                    niveau_actuel=niveau_actuel,
                    niveau_cible=niveau_cible,
                    titre_quete=titre_quete,
                    mj=mj,
                    xp_actuels=xp_actuels,
                    xp_obtenus=xp_obtenus,
                    include_marchand=include_marchand,
                    include_inventaire=include_inventaire
                )
            except Exception as template_error:
                logger.error(f"Erreur génération template: {template_error}")
                await interaction.followup.send(
                    f"❌ **Erreur lors de la génération du template**\n\n"
                    f"Erreur : {str(template_error)}\n\n"
                    f"Vérifiez vos paramètres et réessayez.",
                    ephemeral=True
                )
                return

            # CORRECTION 3: Création de l'embed de réponse simplifiée
            embed = self._create_simple_response_embed(
                nom_pj, classe, niveau_actuel, niveau_cible,
                validation_errors, len(template)
            )
            
            # Envoi de l'embed de confirmation
            await interaction.followup.send(embed=embed, ephemeral=True)
            
            # CORRECTION 4: Envoi du template de manière robuste
            await self._send_template_robust(interaction, template, validation_errors)
            
            logger.info(f"Template généré avec succès pour {nom_pj}")
            
        except Exception as e:
            # CORRECTION 5: Gestion d'erreur globale robuste
            logger.error(f"Erreur callback maj-fiche: {e}", exc_info=True)
            
            error_msg = (
                f"❌ **Erreur inattendue**\n\n"
                f"Une erreur s'est produite lors de la génération du template.\n"
                f"**Erreur :** {str(e)}\n\n"
                f"💡 **Solutions :**\n"
                f"• Vérifiez vos paramètres\n"
                f"• Réessayez dans quelques instants\n"
                f"• Contactez un administrateur si le problème persiste"
            )
            
            # Vérifier si on a déjà répondu pour éviter les erreurs
            try:
                if interaction.response.is_done():
                    await interaction.followup.send(error_msg, ephemeral=True)
                else:
                    await interaction.response.send_message(error_msg, ephemeral=True)
            except:
                # Dernier recours - log l'erreur
                logger.error(f"Impossible d'envoyer le message d'erreur pour {interaction.user}")

    def _create_simple_response_embed(
        self,
        nom_pj: str,
        classe: str,
        niveau_actuel: Optional[int],
        niveau_cible: Optional[int],
        validation_errors: list,
        template_length: int
    ) -> discord.Embed:
        """
        Crée un embed de réponse simplifié et robuste.
        CORRECTION: Version simplifiée sans risque d'erreur
        """
        embed = discord.Embed(
            title="✅ Template D&D Généré avec Succès",
            description=f"Votre template pour **{nom_pj}** est prêt !",
            color=0x2ecc71
        )
        
        # Informations de base
        info_text = f"**Classe :** {classe}"
        if niveau_actuel and niveau_cible:
            info_text += f"\n**Progression :** Niveau {niveau_actuel} → {niveau_cible}"
        elif niveau_actuel:
            info_text += f"\n**Niveau :** {niveau_actuel}"
        
        embed.add_field(
            name="🎲 Informations du Personnage",
            value=info_text,
            inline=True
        )
        
        # Statistiques du template
        stats_text = f"**Caractères :** {template_length}"
        if template_length > 1900:
            stats_text += " ⚠️ (sera divisé)"
        else:
            stats_text += " ✅ (taille OK)"
        
        embed.add_field(
            name="📊 Statistiques",
            value=stats_text,
            inline=True
        )
        
        # Alertes de validation si nécessaires
        if validation_errors:
            embed.add_field(
                name="⚠️ Alertes",
                value="\n".join([f"• {error}" for error in validation_errors[:3]]),
                inline=False
            )
        
        # Instructions d'utilisation
        embed.add_field(
            name="📝 Instructions",
            value=(
                "1. **Copiez** le template ci-dessous\n"
                "2. **Complétez** les placeholders [EN_MAJUSCULES]\n"
                "3. **Postez** dans le canal approprié"
            ),
            inline=False
        )
        
        embed.set_footer(
            text=f"Généré par {nom_pj} • Template D&D 5e"
        )
        embed.timestamp = discord.utils.utcnow()
        
        return embed

    async def _send_template_robust(
        self, 
        interaction: discord.Interaction, 
        template: str, 
        validation_errors: list
    ):
        """
        Envoie le template de manière robuste avec gestion des longueurs.
        CORRECTION: Méthode simplifiée et sûre
        """
        try:
            # Limite de sécurité Discord (2000 - marge pour les markdown et embed)
            SAFE_LIMIT = 1800
            
            if len(template) <= SAFE_LIMIT:
                # Template court - envoi direct dans un embed
                embed = discord.Embed(
                    title="📋 Votre Template de Mise à Jour",
                    description=f"```\n{template}\n```",
                    color=0x3498db
                )
                
                if validation_errors:
                    embed.add_field(
                        name="⚠️ Remarques",
                        value="\n".join([f"• {error}" for error in validation_errors[:2]]),
                        inline=False
                    )
                
                await interaction.followup.send(embed=embed, ephemeral=True)
                
            else:
                # Template long - division en parties
                await self._send_long_template(interaction, template, validation_errors)
                
        except Exception as e:
            logger.error(f"Erreur envoi template: {e}")
            # Fallback - envoi en texte simple
            try:
                await interaction.followup.send(
                    f"📋 **Template généré** (envoi simplifié suite à une erreur technique)\n```\n{template[:1500]}\n```",
                    ephemeral=True
                )
                if len(template) > 1500:
                    await interaction.followup.send(
                        f"```\n{template[1500:]}\n```",
                        ephemeral=True
                    )
            except:
                await interaction.followup.send(
                    "❌ Erreur lors de l'envoi du template. Veuillez réessayer.",
                    ephemeral=True
                )

    async def _send_long_template(
        self, 
        interaction: discord.Interaction, 
        template: str, 
        validation_errors: list
    ):
        """
        Divise et envoie un template long en plusieurs parties.
        CORRECTION: Logique de division simplifiée et robuste
        """
        # Diviser le template en lignes pour préserver la structure
        lines = template.split('\n')
        parts = []
        current_part = ""
        
        for line in lines:
            # Vérifier si ajouter cette ligne dépasserait la limite
            test_part = current_part + line + '\n'
            if len(test_part) > 1800 and current_part:
                # Sauvegarder la partie actuelle et commencer une nouvelle
                parts.append(current_part.strip())
                current_part = line + '\n'
            else:
                current_part = test_part
        
        # Ajouter la dernière partie
        if current_part:
            parts.append(current_part.strip())
        
        # Envoyer chaque partie
        for i, part in enumerate(parts):
            embed = discord.Embed(
                title=f"📋 Template D&D - Partie {i+1}/{len(parts)}",
                description=f"```\n{part}\n```",
                color=0x3498db
            )
            
            # Ajouter les alertes seulement à la première partie
            if i == 0 and validation_errors:
                embed.add_field(
                    name="⚠️ Remarques",
                    value="\n".join([f"• {error}" for error in validation_errors[:2]]),
                    inline=False
                )
            
            await interaction.followup.send(embed=embed, ephemeral=True)