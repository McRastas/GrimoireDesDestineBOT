"""
Commande Discord : /config-channels

DESCRIPTION:
    Affiche et gère la configuration générique des canaux du bot

FONCTIONNEMENT:
    - Affiche tous les canaux configurés et leur statut
    - Permet de lister les canaux du serveur
    - Teste la connectivité des canaux configurés
    - Guide de configuration avec exemples
    - Réservé aux administrateurs

UTILISATION:
    /config-channels [action]
"""

import discord
from discord import app_commands
from .base import BaseCommand
from utils.channels import ChannelHelper
from utils.permissions import has_admin_role, send_permission_denied
from config import Config


class ConfigChannelsCommand(BaseCommand):

    @property
    def name(self) -> str:
        return "config-channels"

    @property
    def description(self) -> str:
        return "Gère la configuration des canaux du bot"

    def register(self, tree: app_commands.CommandTree):
        """Enregistrement avec paramètres optionnels."""

        @tree.command(name=self.name, description=self.description)
        @app_commands.describe(action="Action à effectuer")
        @app_commands.choices(action=[
            app_commands.Choice(name="Voir configuration", value="show"),
            app_commands.Choice(name="Lister canaux serveur", value="list"),
            app_commands.Choice(name="Tester configuration", value="test")
        ])
        async def config_channels_command(interaction: discord.Interaction,
                                          action: str = "show"):
            await self.callback(interaction, action)

    async def callback(self,
                       interaction: discord.Interaction,
                       action: str = "show"):
        # Vérifier les permissions
        if not has_admin_role(interaction.user):
            await send_permission_denied(interaction.channel)
            return

        if action == "show":
            await self._show_config(interaction)
        elif action == "list":
            await self._list_server_channels(interaction)
        elif action == "test":
            await self._test_config(interaction)

    async def _show_config(self, interaction: discord.Interaction):
        """Affiche la configuration actuelle des canaux."""

        all_channels = ChannelHelper.get_all_configured_channels(
            interaction.guild)

        embed = discord.Embed(
            title="🔧 Configuration des Canaux",
            description="Configuration actuelle de tous les canaux du bot",
            color=0x3498db)

        # Canaux configurés
        configured_text = []
        for channel_key, info in all_channels.items():
            config = info['config']
            status = "✅" if info['found'] else "❌"

            line = f"{status} **{channel_key}**"
            if config.get('name'):
                line += f" → #{config['name']}"
            if config.get('id'):
                line += f" (ID: `{config['id']}`)"
            if info['channel']:
                line += f" {info['channel'].mention}"

            configured_text.append(line)

        if configured_text:
            embed.add_field(name="📋 Canaux Configurés",
                            value="\n".join(configured_text),
                            inline=False)
        else:
            embed.add_field(name="📋 Canaux Configurés",
                            value="*Aucun canal configuré*",
                            inline=False)

        # Guide de configuration
        embed.add_field(
            name="⚙️ Guide de Configuration",
            value=("**Méthode 1 - JSON (Recommandé) :**\n"
                   "```json\n"
                   "CHANNELS_CONFIG={\n"
                   '  "recompenses": {"name": "recompenses"},\n'
                   '  "quetes": {"name": "départ-aventure", "id": 123456},\n'
                   '  "logs": {"id": 789012}\n'
                   "}\n"
                   "```\n"
                   "**Méthode 2 - Variables individuelles :**\n"
                   "```env\n"
                   "CHANNEL_RECOMPENSES_NAME=recompenses\n"
                   "CHANNEL_QUETES_ID=123456789\n"
                   "CHANNEL_LOGS_NAME=bot-logs\n"
                   "```"),
            inline=False)

        embed.set_footer(
            text=
            f"Serveur: {interaction.guild.name} | Redémarrage requis après modification"
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def _list_server_channels(self, interaction: discord.Interaction):
        """Liste les canaux du serveur pour aide à la configuration."""

        channels = interaction.guild.text_channels[:15]  # Limiter à 15

        embed = discord.Embed(
            title="📋 Canaux du Serveur",
            description=
            f"Liste des canaux texte disponibles sur {interaction.guild.name}",
            color=0x2ecc71)

        channel_list = []
        for channel in channels:
            channel_list.append(f"#{channel.name} (ID: `{channel.id}`)")

        if channel_list:
            embed.add_field(name=f"📝 Canaux Texte ({len(channels)} affichés)",
                            value="\n".join(channel_list),
                            inline=False)

        if len(interaction.guild.text_channels) > 15:
            embed.add_field(
                name="ℹ️ Information",
                value=
                f"*{len(interaction.guild.text_channels) - 15} canaux supplémentaires non affichés*",
                inline=False)

        embed.add_field(
            name="💡 Conseil",
            value=
            "Utilisez l'ID du canal pour une configuration plus fiable (ne change pas si le canal est renommé)",
            inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def _test_config(self, interaction: discord.Interaction):
        """Teste la configuration actuelle."""

        all_channels = ChannelHelper.get_all_configured_channels(
            interaction.guild)

        embed = discord.Embed(
            title="🧪 Test de Configuration",
            description="Résultat des tests de connectivité des canaux",
            color=0xe74c3c if any(
                not info['found']
                for info in all_channels.values()) else 0x2ecc71)

        working_channels = []
        broken_channels = []

        for channel_key, info in all_channels.items():
            if info['found']:
                working_channels.append(
                    f"✅ **{channel_key}** → {info['channel'].mention}")
            else:
                config = info['config']
                error_detail = f"❌ **{channel_key}**"
                if config.get('name'):
                    error_detail += f" → #{config['name']}"
                if config.get('id'):
                    error_detail += f" (ID: `{config['id']}`)"
                error_detail += " *introuvable*"
                broken_channels.append(error_detail)

        if working_channels:
            embed.add_field(name="✅ Canaux Fonctionnels",
                            value="\n".join(working_channels),
                            inline=False)

        if broken_channels:
            embed.add_field(name="❌ Canaux Non Trouvés",
                            value="\n".join(broken_channels),
                            inline=False)

        if not working_channels and not broken_channels:
            embed.add_field(name="ℹ️ Aucune Configuration",
                            value="Aucun canal n'est configuré actuellement",
                            inline=False)

        # Statut global
        total_configured = len(all_channels)
        working_count = len(working_channels)

        if total_configured == 0:
            status = "⚠️ Aucune configuration"
        elif working_count == total_configured:
            status = "✅ Tous les canaux fonctionnent"
        else:
            status = f"⚠️ {working_count}/{total_configured} canaux fonctionnent"

        embed.add_field(name="📊 Statut Global", value=status, inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)
