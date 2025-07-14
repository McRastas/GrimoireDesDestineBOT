"""
Commande Discord : /test-logs (ADMIN SEULEMENT)

DESCRIPTION:
    Teste le système de logs Discord du bot
    VISIBLE UNIQUEMENT pour les membres avec le rôle admin configuré

FONCTIONNEMENT:
    - Vérifie la configuration du canal admin
    - Teste les permissions d'envoi
    - Envoie un message de test dans le canal admin
    - Rapport détaillé des résultats

UTILISATION:
    /test-logs (Façonneurs seulement)
"""

import discord
from discord import app_commands
from .base import BaseCommand
from utils.permissions import has_admin_role
from utils.discord_logger import get_discord_logger
from utils.channels import ChannelHelper
from config import Config


class TestLogsCommand(BaseCommand):

    @property
    def name(self) -> str:
        return "test-logs"

    @property
    def description(self) -> str:
        return "Teste le système de logs Discord (Façonneurs seulement)"

    def register(self, tree: app_commands.CommandTree):
        """Enregistrement avec restriction de permissions."""

        @tree.command(name=self.name, description=self.description)
        # RESTRICTION : Commande visible seulement pour les admin
        @app_commands.check(self._is_admin)
        async def test_logs_command(interaction: discord.Interaction):
            await self.callback(interaction)

        # Gérer l'erreur de permission
        @test_logs_command.error
        async def test_logs_error(interaction: discord.Interaction,
                                  error: app_commands.AppCommandError):
            if isinstance(error, app_commands.CheckFailure):
                await interaction.response.send_message(
                    f"❌ Cette commande est réservée aux membres avec le rôle `{Config.ADMIN_ROLE_NAME}`.",
                    ephemeral=True)

    async def _is_admin(self, interaction: discord.Interaction) -> bool:
        """Vérifie si l'utilisateur a les permissions admin."""
        return has_admin_role(interaction.user)

    async def callback(self, interaction: discord.Interaction):
        # Double vérification des permissions (sécurité)
        if not has_admin_role(interaction.user):
            await interaction.response.send_message(
                f"❌ Accès refusé. Rôle `{Config.ADMIN_ROLE_NAME}` requis.",
                ephemeral=True)
            return

        # Defer pour éviter timeout
        await interaction.response.defer(ephemeral=True)

        # Récupérer le logger Discord
        discord_logger = get_discord_logger()
        if not discord_logger:
            await interaction.followup.send(
                "❌ Système de logs Discord non initialisé.", ephemeral=True)
            return

        # Log de l'action admin
        discord_logger.admin_action("Test Système Logs", interaction.user,
                                    "Commande /test-logs utilisée")

        # Tester le système de logs
        result = await discord_logger.test_logging(interaction.guild)

        # Créer l'embed de résultat
        embed = discord.Embed(title="🧪 Test du Système de Logs Discord",
                              timestamp=discord.utils.utcnow())

        # Canal admin trouvé ?
        if result['channel_found']:
            embed.color = 0x00ff00 if result['test_sent'] else 0xff9900

            embed.add_field(name="📍 Canal Admin Configuré",
                            value=f"✅ #{result['channel_name']}",
                            inline=True)

            # Permissions
            perm_status = "✅ Autorisées" if result[
                'can_send'] else "❌ Manquantes"
            embed.add_field(name="🔐 Permissions",
                            value=perm_status,
                            inline=True)

            # Test d'envoi
            test_status = "✅ Réussi" if result['test_sent'] else "❌ Échec"
            embed.add_field(name="📨 Test d'Envoi",
                            value=test_status,
                            inline=True)

            # Description selon le résultat
            if result['test_sent']:
                embed.description = (
                    "✅ **Système de logs parfaitement opérationnel !**\n"
                    f"Un message de test a été envoyé dans #{result['channel_name']}."
                )

                # Envoyer quelques logs de démonstration
                discord_logger.info(
                    "Test des logs - Message INFO",
                    user=
                    f"{interaction.user.display_name} ({interaction.user.id})",
                    guild=f"{interaction.guild.name} ({interaction.guild.id})")

                discord_logger.warning(
                    "Test des logs - Message WARNING de démonstration")

            elif not result['can_send']:
                embed.description = (
                    "⚠️ **Canal trouvé mais permissions insuffisantes**\n"
                    "Le bot ne peut pas envoyer de messages dans ce canal.")
                embed.add_field(
                    name="🔧 Solution",
                    value=
                    (f"Accordez au bot les permissions suivantes dans #{result['channel_name']} :\n"
                     "• Voir le canal\n"
                     "• Envoyer des messages\n"
                     "• Intégrer des liens"),
                    inline=False)
            else:
                embed.description = (
                    "❌ **Erreur lors du test d'envoi**\n"
                    f"Permissions OK mais impossible d'envoyer dans #{result['channel_name']}."
                )
                if 'error' in result:
                    embed.add_field(name="🐛 Erreur",
                                    value=f"```{result['error']}```",
                                    inline=False)

        else:
            embed.color = 0xe74c3c
            embed.description = ("❌ **Canal admin non configuré**\n"
                                 "Le système de logs ne peut pas fonctionner.")

            embed.add_field(
                name="🔧 Configuration Requise",
                value=("Configurez une de ces variables d'environnement :\n"
                       "• `CHANNEL_ADMIN_NAME=bot-admin`\n"
                       "• `CHANNEL_ADMIN_ID=123456789`\n"
                       "• Dans `CHANNELS_CONFIG` JSON"),
                inline=False)

            embed.add_field(
                name="💡 Aide",
                value=
                "Utilisez `/config-channels action:guide` pour plus d'infos",
                inline=False)

        # Informations sur la configuration actuelle
        admin_config = Config.get_channel_config('admin')
        if admin_config:
            config_text = []
            if admin_config.get('name'):
                config_text.append(f"Nom: #{admin_config['name']}")
            if admin_config.get('id'):
                config_text.append(f"ID: `{admin_config['id']}`")

            if config_text:
                embed.add_field(name="⚙️ Configuration Actuelle",
                                value=" | ".join(config_text),
                                inline=False)

        # Footer avec info utilisateur
        embed.set_footer(
            text=
            f"Test effectué par {interaction.user.display_name} • {Config.ADMIN_ROLE_NAME}"
        )

        await interaction.followup.send(embed=embed)
