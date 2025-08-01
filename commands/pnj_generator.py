# commands/pnj_generator.py - Fichier Principal
import discord
from discord import app_commands
from typing import Optional
import logging
from .base import BaseCommand
from .pnj_generator_core import PNJGenerator
from .pnj_generator_formatters import PNJFormatters

logger = logging.getLogger(__name__)


class PnjGeneratorCommand(BaseCommand):
    """Générateur de PNJ avec format optimisé Roll20"""

    def __init__(self, bot):
        super().__init__(bot)
        self.pnj_generator = PNJGenerator()
        self.formatters = PNJFormatters()

    @property
    def name(self) -> str:
        return "pnj-generator"

    @property
    def description(self) -> str:
        return "Génère un PNJ complet pour D&D avec format Roll20"

    def register(self, tree: app_commands.CommandTree):
        """Enregistrement de la commande avec option format Roll20"""

        @tree.command(name=self.name, description=self.description)
        @app_commands.describe(
            type_pnj="Type de PNJ à générer",
            genre="Genre du PNJ",
            race="Race du PNJ",
            format_roll20="Format optimisé pour Roll20 (recommandé)"
        )
        @app_commands.choices(type_pnj=[
            app_commands.Choice(name="🛡️ Garde", value="garde"),
            app_commands.Choice(name="💰 Marchand", value="marchand"),
            app_commands.Choice(name="👑 Noble", value="noble"),
            app_commands.Choice(name="🍺 Aubergiste", value="aubergiste"),
            app_commands.Choice(name="⛪ Prêtre", value="pretre"),
            app_commands.Choice(name="🗡️ Aventurier", value="aventurier"),
            app_commands.Choice(name="🔨 Artisan", value="artisan"),
            app_commands.Choice(name="🌾 Paysan", value="paysan"),
            app_commands.Choice(name="🗝️ Voleur", value="voleur"),
            app_commands.Choice(name="🔮 Mage", value="mage")
        ])
        @app_commands.choices(genre=[
            app_commands.Choice(name="♂️ Masculin", value="masculin"),
            app_commands.Choice(name="♀️ Féminin", value="feminin"),
            app_commands.Choice(name="🎲 Aléatoire", value="aleatoire")
        ])
        @app_commands.choices(race=[
            app_commands.Choice(name="👤 Humain", value="humain"),
            app_commands.Choice(name="🧝 Elfe", value="elfe"),
            app_commands.Choice(name="⚒️ Nain", value="nain"),
            app_commands.Choice(name="🌿 Halfelin", value="halfelin"),
            app_commands.Choice(name="🌙 Demi-Elfe", value="demi-elfe"),
            app_commands.Choice(name="😈 Tieffelin", value="tieffelin"),
            app_commands.Choice(name="🎲 Aléatoire", value="aleatoire")
        ])
        @app_commands.choices(format_roll20=[
            app_commands.Choice(name="✅ Roll20 (Recommandé)", value=True),
            app_commands.Choice(name="💬 Discord", value=False)
        ])
        async def pnj_generator_command(
            interaction: discord.Interaction,
            type_pnj: str,
            genre: str = "aleatoire",
            race: str = "aleatoire",
            format_roll20: bool = True
        ):
            await self.callback(interaction, type_pnj, genre, race, format_roll20)

    async def callback(self,
                       interaction: discord.Interaction,
                       type_pnj: str,
                       genre: str = "aleatoire",
                       race: str = "aleatoire",
                       format_roll20: bool = True):
        """Callback principal avec gestion des deux formats"""
        try:
            # Générer le PNJ via le générateur
            pnj = self.pnj_generator.generate_pnj(type_pnj, genre, race)

            # Choisir le format de sortie via les formatters
            if format_roll20:
                content = self.formatters.format_pnj_for_roll20(pnj, type_pnj)
                embed_title = "🎭 PNJ Généré (Format Roll20)"
                instructions = (
                    "1. **Copiez** le texte ci-dessous\n"
                    "2. **Collez** dans les notes de votre fiche Roll20\n"
                    "3. **Adaptez** selon vos besoins de campagne"
                )
            else:
                content = self.formatters.format_pnj_for_discord(pnj, type_pnj)
                embed_title = "🎭 PNJ Généré (Format Discord)"
                instructions = (
                    "1. **Copiez** le contenu formaté\n"
                    "2. **Utilisez** directement dans Discord\n"
                    "3. **Modifiez** selon vos besoins"
                )

            # Créer l'embed d'information
            embed = discord.Embed(
                title=embed_title,
                description=f"**{pnj['nom']}** - {pnj['race']} {type_pnj.title()}",
                color=0x3498db
            )

            embed.add_field(
                name="👤 Aperçu",
                value=f"**Genre:** {pnj['genre'].title()}\n**Âge:** {pnj['age']} ans",
                inline=True
            )

            embed.add_field(
                name="🎭 Trait Principal",
                value=f"{pnj['personnalite']['trait_positif'].title()}",
                inline=True
            )

            embed.add_field(
                name="📋 Instructions",
                value=instructions,
                inline=False
            )

            # Vérifier la longueur et envoyer
            if len(content) > 1900:
                await self._send_long_content(interaction, content, embed)
            else:
                await interaction.response.send_message(embed=embed)
                if format_roll20:
                    await interaction.followup.send(f"```\n{content}\n```")
                else:
                    await interaction.followup.send(content)

        except Exception as e:
            logger.error(f"Erreur génération PNJ: {e}")
            await interaction.response.send_message(
                "❌ Erreur lors de la génération du PNJ. Veuillez réessayer.",
                ephemeral=True
            )

    async def _send_long_content(self, interaction: discord.Interaction, content: str, embed: discord.Embed):
        """Envoie du contenu long en le divisant si nécessaire"""
        
        await interaction.response.send_message(embed=embed)
        
        # Diviser le contenu si trop long
        if len(content) > 1900:
            parts = []
            lines = content.split('\n')
            current_part = ""
            
            for line in lines:
                if len(current_part) + len(line) + 1 > 1900:
                    if current_part:
                        parts.append(current_part)
                    current_part = line
                else:
                    current_part += ("\n" if current_part else "") + line
            
            if current_part:
                parts.append(current_part)
            
            for i, part in enumerate(parts):
                await interaction.followup.send(f"```\n{part}\n```")
        else:
            await interaction.followup.send(f"```\n{content}\n```")