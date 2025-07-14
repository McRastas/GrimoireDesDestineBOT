"""
Commande Discord : /config-channels

DESCRIPTION:
    Affiche et gère la configuration générique des canaux du bot

FONCTIONNEMENT:
    - Affiche tous les canaux configurés et leur statut
    - Permet de lister les canaux du serveur
    - Teste la connectivité des canaux configurés
    - Guide de configuration avec exemples et suggestions automatiques
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
            app_commands.Choice(name="Tester configuration", value="test"),
            app_commands.Choice(name="Suggestion automatique",
                                value="suggest"),
            app_commands.Choice(name="Guide de configuration", value="guide")
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
        elif action == "suggest":
            await self._suggest_config(interaction)
        elif action == "guide":
            await self._show_guide(interaction)

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
        working_count = 0

        for channel_key, info in all_channels.items():
            config = info['config']
            status = "✅" if info['found'] else "❌"

            if info['found']:
                working_count += 1

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

        # Statut global
        total_configured = len(all_channels)
        if total_configured == 0:
            status_color = 0xe74c3c
            status_text = "⚠️ Aucune configuration"
        elif working_count == total_configured:
            status_color = 0x2ecc71
            status_text = "✅ Tous les canaux fonctionnent"
        else:
            status_color = 0xf39c12
            status_text = f"⚠️ {working_count}/{total_configured} canaux fonctionnent"

        embed.color = status_color
        embed.add_field(name="📊 Statut Global",
                        value=status_text,
                        inline=False)

        # Actions disponibles
        embed.add_field(
            name="🛠️ Actions Disponibles",
            value=("• `/config-channels action:test` - Tester la config\n"
                   "• `/config-channels action:suggest` - Suggestions auto\n"
                   "• `/config-channels action:guide` - Guide complet\n"
                   "• `/config-channels action:list` - Canaux du serveur"),
            inline=False)

        embed.set_footer(
            text=
            f"Serveur: {interaction.guild.name} | Redémarrage requis après modification"
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def _list_server_channels(self, interaction: discord.Interaction):
        """Liste les canaux du serveur pour aide à la configuration."""

        embed = discord.Embed(
            title="📋 Canaux du Serveur",
            description=
            f"Liste des canaux texte disponibles sur {interaction.guild.name}",
            color=0x2ecc71)

        # Utiliser la méthode du helper
        channel_list = ChannelHelper.format_channel_list(interaction.guild,
                                                         include_ids=True)

        if channel_list:
            embed.add_field(name=f"📝 Canaux Texte",
                            value=channel_list,
                            inline=False)

        total_channels = len(interaction.guild.text_channels)
        if total_channels > 20:
            embed.add_field(
                name="ℹ️ Information",
                value=
                f"*{total_channels - 20} canaux supplémentaires non affichés*",
                inline=False)

        embed.add_field(
            name="💡 Conseil",
            value=
            "Utilisez l'ID du canal pour une configuration plus fiable (ne change pas si le canal est renommé)",
            inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def _test_config(self, interaction: discord.Interaction):
        """Teste la configuration actuelle avec rapport détaillé."""

        rapport = ChannelHelper.test_all_channels(interaction.guild)

        embed = discord.Embed(
            title="🧪 Test de Configuration",
            description="Résultat des tests de connectivité des canaux",
            color=0x2ecc71 if rapport['manquants'] == 0 else 0xe74c3c)

        # Canaux fonctionnels
        if rapport['fonctionnels'] > 0:
            working_lines = []
            for channel_key, details in rapport['details'].items():
                if details['status'] == 'OK':
                    working_lines.append(
                        f"✅ **{channel_key}** → {details['channel']}")

            if working_lines:
                embed.add_field(
                    name=f"✅ Canaux Fonctionnels ({rapport['fonctionnels']})",
                    value="\n".join(working_lines),
                    inline=False)

        # Canaux en erreur
        if rapport['manquants'] > 0:
            error_lines = []
            for channel_key, details in rapport['details'].items():
                if details['status'] == 'MANQUANT':
                    config = details['config']
                    error_detail = f"❌ **{channel_key}**"
                    if config.get('name'):
                        error_detail += f" → #{config['name']}"
                    if config.get('id'):
                        error_detail += f" (ID: `{config['id']}`)"
                    error_detail += " *introuvable*"
                    error_lines.append(error_detail)

            if error_lines:
                embed.add_field(
                    name=f"❌ Canaux Non Trouvés ({rapport['manquants']})",
                    value="\n".join(error_lines),
                    inline=False)

        # Statut global détaillé
        if rapport['total'] == 0:
            status = "⚠️ Aucune configuration détectée"
            embed.add_field(
                name="💡 Recommandation",
                value=
                "Utilisez `/config-channels action:suggest` pour des suggestions automatiques",
                inline=False)
        elif rapport['manquants'] == 0:
            status = f"✅ Parfait ! Tous les {rapport['fonctionnels']} canaux configurés fonctionnent"
        else:
            status = f"⚠️ {rapport['fonctionnels']}/{rapport['total']} canaux fonctionnent"
            embed.add_field(
                name="💡 Recommandation",
                value=
                "Configurez les canaux manquants ou utilisez `/config-channels action:suggest`",
                inline=False)

        embed.add_field(name="📊 Résultat", value=status, inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def _suggest_config(self, interaction: discord.Interaction):
        """Propose une configuration automatique basée sur les canaux existants."""

        embed = discord.Embed(
            title="💡 Suggestions de Configuration",
            description=
            "Configuration automatique basée sur les canaux existants",
            color=0xf39c12)

        # Utiliser la méthode du helper
        suggestions = ChannelHelper.suggest_channel_config(interaction.guild)

        embed.add_field(name="🤖 Analyse Automatique",
                        value=suggestions,
                        inline=False)

        embed.add_field(
            name="📝 Comment Appliquer",
            value=("1. Copiez la configuration JSON suggérée\n"
                   "2. Définissez la variable d'environnement :\n"
                   "   `CHANNELS_CONFIG={\"votre_config_json\"}`\n"
                   "3. Redémarrez le bot\n"
                   "4. Utilisez `/config-channels action:test` pour vérifier"),
            inline=False)

        embed.add_field(
            name="🔧 Configuration Manuelle",
            value=
            "Si les suggestions ne conviennent pas, utilisez `/config-channels action:guide`",
            inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def _show_guide(self, interaction: discord.Interaction):
        """Affiche le guide complet de configuration."""

        embed = discord.Embed(
            title="📖 Guide de Configuration des Canaux",
            description="Guide complet pour configurer les canaux du bot",
            color=0x9b59b6)

        embed.add_field(
            name="🎯 Canaux Supportés",
            value=("• **recompenses** - Canal des récompenses/mentions\n"
                   "• **quetes** - Canal départ à l'aventure\n"
                   "• **logs** - Canal des logs du bot\n"
                   "• **admin** - Canal d'administration du bot"),
            inline=False)

        embed.add_field(
            name="⚙️ Méthode 1 - JSON (Recommandé)",
            value=
            ("```env\n"
             "CHANNELS_CONFIG={\n"
             '  \"recompenses\": {\"name\": \"recompenses\"},\n'
             '  \"quetes\": {\"name\": \"départ-aventure\", \"id\": 123456},\n'
             '  \"logs\": {\"id\": 789012}\n'
             "}\n"
             "```"),
            inline=False)

        embed.add_field(name="⚙️ Méthode 2 - Variables Individuelles",
                        value=("```env\n"
                               "CHANNEL_RECOMPENSES_NAME=recompenses\n"
                               "CHANNEL_QUETES_ID=123456789\n"
                               "CHANNEL_LOGS_NAME=bot-logs\n"
                               "CHANNEL_ADMIN_NAME=bot-admin\n"
                               "```"),
                        inline=False)

        embed.add_field(
            name="💡 Bonnes Pratiques",
            value=
            ("• **Priorité ID > nom** - L'ID est prioritaire sur le nom\n"
             "• **IDs recommandés** - Plus fiables (ne changent pas)\n"
             "• **Permissions** - Le bot doit avoir accès aux canaux\n"
             "• **Test** - Utilisez `/config-channels action:test` après config"
             ),
            inline=False)

        embed.add_field(
            name="🔍 Obtenir un ID de Canal",
            value=("1. Activez le Mode Développeur Discord\n"
                   "2. Clic droit sur le canal → Copier l'ID\n"
                   "3. Ou utilisez `/config-channels action:list`"),
            inline=False)

        embed.set_footer(
            text="Redémarrez le bot après modification de la configuration")

        await interaction.response.send_message(embed=embed, ephemeral=True)
