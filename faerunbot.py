import logging
import asyncio

import discord
from discord import app_commands

from config import Config
from commands import ALL_COMMANDS
from utils.permissions import has_admin_role, send_permission_denied
from utils.discord_logger import init_discord_logger, get_discord_logger
from utils.file_logger import init_daily_logger, get_daily_logger  # NOUVEAU

# Configuration du niveau de log global
LOG_LEVEL = logging.INFO

# Configuration des logs
logging.basicConfig(level=LOG_LEVEL,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Réduire le bruit des logs de discord.py
discord_logger = logging.getLogger('discord')
discord_logger.setLevel(logging.WARNING)


class FaerunBot(discord.Client):
    """Bot Discord principal pour le calendrier Faerûn."""

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.synced = False
        self.command_instances = []

        # Initialiser les systèmes de logs
        self.discord_logger = init_discord_logger(self)
        self.daily_logger = init_daily_logger()  # NOUVEAU

    async def setup_hook(self):
        """Méthode appelée lors du démarrage du bot pour configurer les commandes."""
        logger.info("Chargement des commandes...")
        await self.load_commands()
        logger.info(f"{len(self.tree.get_commands())} commandes prêtes")

    async def load_commands(self):
        """Charge toutes les commandes depuis le module commands."""
        for command_class in ALL_COMMANDS:
            try:
                command_instance = command_class(self)
                command_instance.register(self.tree)
                self.command_instances.append(command_instance)
            except Exception as e:
                logger.error(
                    f"Erreur chargement {command_class.__name__}: {e}")

        logger.info(f"{len(self.command_instances)} commandes chargées")

    async def on_ready(self):
        """Événement déclenché quand le bot est prêt"""
        logger.info(
            f"Bot connecté: {self.user} sur {len(self.guilds)} serveur(s)")

        # Marquer le logger Discord comme prêt
        self.discord_logger.set_ready()

        # Log de démarrage dans Discord ET fichiers quotidiens
        startup_msg = f"Bot connecté avec succès ! Serveurs: {len(self.guilds)}, Commandes: {len(self.tree.get_commands())}"
        self.discord_logger.bot_event("Démarrage", startup_msg)

        # Synchroniser les commandes avec Discord
        if not self.synced:
            await self.sync_commands()
            self.synced = True

    async def sync_commands(self):
        """Synchronise les commandes slash."""
        try:
            commands_count = len(self.tree.get_commands())
            if commands_count == 0:
                logger.error("Aucune commande à synchroniser")
                self.discord_logger.error("Synchronisation impossible - Aucune commande chargée")
                return

            if Config.GUILD_ID:
                guild = discord.Object(id=Config.GUILD_ID)
                self.tree.copy_global_to(guild=guild)
                synced = await self.tree.sync(guild=guild)
                logger.info(
                    f"✅ {len(synced)} commandes synchronisées (guild: {Config.GUILD_ID})"
                )
                self.discord_logger.info(
                    f"Commandes synchronisées avec succès sur le serveur de test",
                    guild=f"Test Server ({Config.GUILD_ID})",
                    command=f"{len(synced)} commandes")
            else:
                synced = await self.tree.sync()
                logger.info(
                    f"✅ {len(synced)} commandes synchronisées (global)")
                self.discord_logger.info(
                    f"Commandes synchronisées globalement",
                    command=f"{len(synced)} commandes")

        except discord.HTTPException as e:
            logger.error(f"Erreur HTTP synchronisation: {e.status}")
            self.discord_logger.error(
                f"Erreur HTTP lors de la synchronisation des commandes",
                error=f"Status {e.status}: {e.text}")
        except Exception as e:
            logger.error(f"Erreur synchronisation: {e}")
            self.discord_logger.error_with_traceback(
                "Erreur critique lors de la synchronisation des commandes", e)

    async def on_app_command_error(self, interaction: discord.Interaction,
                                   error: app_commands.AppCommandError):
        """Gère les erreurs des commandes slash."""
        command_name = interaction.command.name if interaction.command else "inconnue"
        error_msg = str(error)
        
        logger.error(f"Erreur commande {command_name}: {error_msg}")

        # Log dans Discord
        self.discord_logger.error(
            f"Erreur lors de l'exécution d'une commande",
            user=f"{interaction.user.display_name} ({interaction.user.id})",
            guild=f"{interaction.guild.name} ({interaction.guild.id})"
            if interaction.guild else "DM",
            command=f"/{command_name}",
            error=error_msg)

        # NOUVEAU : Log dans fichier quotidien
        self.daily_logger.log_command_usage(
            interaction=interaction,
            command_name=command_name,
            success=False,
            error_msg=error_msg
        )

        # Répondre à l'utilisateur
        error_response = "❌ Une erreur inattendue s'est produite lors de l'exécution de cette commande."

        try:
            if not interaction.response.is_done():
                await interaction.response.send_message(error_response,
                                                        ephemeral=True)
            else:
                await interaction.followup.send(error_response, ephemeral=True)
        except:
            pass

    async def on_app_command_completion(self, interaction: discord.Interaction,
                                        command: app_commands.Command):
        """Log les commandes exécutées avec succès."""
        logger.info(
            f"Commande /{command.name} exécutée par {interaction.user.name}")

        # NOUVEAU : Log dans fichier quotidien pour TOUTES les commandes
        self.daily_logger.log_command_usage(
            interaction=interaction,
            command_name=command.name,
            success=True
        )

        # Log dans Discord seulement pour les commandes admin
        if command.name in [
                'config-channels', 'sync_bot', 'debug_bot', 'reload_commands'
        ]:
            self.discord_logger.command_used(interaction,
                                             command.name,
                                             success=True)

    async def on_guild_join(self, guild: discord.Guild):
        """Log quand le bot rejoint un serveur."""
        logger.info(f"Bot ajouté au serveur: {guild.name} ({guild.id})")
        self.discord_logger.bot_event(
            "Nouveau Serveur",
            f"Bot ajouté au serveur **{guild.name}** ({guild.member_count} membres)",
            guild=f"{guild.name} ({guild.id})")

    async def on_guild_remove(self, guild: discord.Guild):
        """Log quand le bot quitte un serveur."""
        logger.info(f"Bot retiré du serveur: {guild.name} ({guild.id})")
        self.discord_logger.bot_event(
            "Serveur Quitté",
            f"Bot retiré du serveur **{guild.name}**",
            guild=f"{guild.name} ({guild.id})")

    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        # Commande de synchronisation manuelle
        if message.content.strip() == "!sync_bot":
            logger.info(
                f"Commande !sync_bot par {message.author.name} ({message.author.id})"
            )

            # Supprimer le message de commande
            try:
                await message.delete()
            except:
                pass

            # Vérification des permissions
            if not has_admin_role(message.author):
                await send_permission_denied(message.channel)
                return

            # Log de l'action admin
            self.discord_logger.admin_action("Synchronisation Manuelle",
                                             message.author,
                                             "Commande !sync_bot utilisée")

            status_msg = await message.channel.send(
                "🔄 Synchronisation en cours...")

            try:
                # Forcer une nouvelle synchronisation
                guild = discord.Object(id=message.guild.id)
                synced = await self.tree.sync(guild=guild)

                # Message de succès détaillé
                embed = discord.Embed(
                    title="✅ Synchronisation réussie",
                    description=f"{len(synced)} commandes synchronisées",
                    color=0x00ff00)

                # Lister les commandes synchronisées
                if synced:
                    cmd_list = "\n".join([f"• {cmd.name}" for cmd in synced])
                    embed.add_field(name="Commandes",
                                    value=cmd_list,
                                    inline=False)

                embed.add_field(name="Serveur",
                                value=message.guild.name,
                                inline=True)
                embed.add_field(name="ID Serveur",
                                value=str(message.guild.id),
                                inline=True)
                embed.add_field(
                    name="Utilisateur",
                    value=
                    f"{message.author.mention} ({Config.ADMIN_ROLE_NAME})",
                    inline=True)

                await status_msg.edit(content=None, embed=embed)

                # Log de succès
                self.discord_logger.info(
                    f"Synchronisation manuelle réussie - {len(synced)} commandes",
                    user=f"{message.author.display_name} ({message.author.id})",
                    guild=f"{message.guild.name} ({message.guild.id})")

                # Supprimer après 10 secondes
                await asyncio.sleep(10)
                await status_msg.delete()

            except Exception as e:
                logger.error(f"Erreur sync manuelle: {e}")
                await status_msg.edit(content=f"❌ Erreur: {e}")

                # Log de l'erreur
                self.discord_logger.error_with_traceback(
                    "Erreur lors de la synchronisation manuelle",
                    e,
                    user=f"{message.author.display_name} ({message.author.id})",
                    guild=f"{message.guild.name} ({message.guild.id})")

                await asyncio.sleep(10)
                await status_msg.delete()

        # Commande de debug
        elif message.content.strip() == "!debug_bot":
            if not has_admin_role(message.author):
                await send_permission_denied(message.channel)
                return

            # Log de l'action admin
            self.discord_logger.admin_action("Debug Système", message.author,
                                             "Commande !debug_bot utilisée")

            # Supprimer le message de commande
            try:
                await message.delete()
            except:
                pass

            embed = discord.Embed(title="🔍 Debug Bot", color=0xff9900)
            embed.add_field(name="Commandes dans tree",
                            value=len(self.tree.get_commands()),
                            inline=True)
            embed.add_field(name="Guildes",
                            value=len(self.guilds),
                            inline=True)
            embed.add_field(name="Synced", value=self.synced, inline=True)
            embed.add_field(name="Instances chargées",
                            value=len(self.command_instances),
                            inline=True)
            embed.add_field(name="Rôle Admin",
                            value=f"`{Config.ADMIN_ROLE_NAME}`",
                            inline=True)

            # Lister les commandes
            cmd_list = "\n".join(
                [f"• {cmd.name}" for cmd in self.tree.get_commands()])
            if cmd_list:
                embed.add_field(name="Liste des commandes",
                                value=cmd_list,
                                inline=False)

            # Vérifier les commandes de guild
            try:
                guild_commands = await self.tree.fetch_commands(
                    guild=message.guild)
                embed.add_field(name="Commandes sur le serveur",
                                value=len(guild_commands),
                                inline=True)
            except:
                pass

            # Afficher les membres avec le rôle admin
            admin_role = discord.utils.get(message.guild.roles,
                                           name=Config.ADMIN_ROLE_NAME)
            if admin_role:
                admin_members = [
                    member.mention for member in admin_role.members[:5]
                ]
                if admin_members:
                    embed.add_field(name=f"Membres {Config.ADMIN_ROLE_NAME}",
                                    value="\n".join(admin_members),
                                    inline=False)
            else:
                embed.add_field(
                    name="⚠️ Rôle Admin",
                    value=f"Rôle `{Config.ADMIN_ROLE_NAME}` introuvable",
                    inline=False)

            msg = await message.channel.send(embed=embed)
            # Supprimer après 15 secondes
            await asyncio.sleep(15)
            await msg.delete()

        # Commande de rechargement des commandes
        elif message.content.strip() == "!reload_commands":
            if not has_admin_role(message.author):
                await send_permission_denied(message.channel)
                return

            # Log de l'action admin
            self.discord_logger.admin_action(
                "Rechargement Commandes", message.author,
                "Commande !reload_commands utilisée")

            # Supprimer le message de commande
            try:
                await message.delete()
            except:
                pass

            embed = discord.Embed(title="🔄 Rechargement des commandes",
                                  description="Rechargement en cours...",
                                  color=0xff9900)
            status_msg = await message.channel.send(embed=embed)

            try:
                # Vider l'arbre des commandes
                self.tree.clear_commands(guild=None)
                self.command_instances.clear()

                # Recharger les commandes
                await self.load_commands()

                # Resynchroniser
                await asyncio.sleep(1)
                synced = await self.tree.sync(guild=message.guild)

                embed.color = 0x00ff00
                embed.description = "✅ Rechargement terminé et commandes resynchronisées"
                embed.add_field(
                    name="🔄 Commandes rechargées",
                    value=
                    f"{len(self.command_instances)} instance(s) créée(s)\n{len(synced)} commande(s) synchronisée(s)",
                    inline=False)
                embed.add_field(
                    name="Utilisateur",
                    value=
                    f"{message.author.mention} ({Config.ADMIN_ROLE_NAME})",
                    inline=True)

                await status_msg.edit(embed=embed)

                # Log de succès
                self.discord_logger.info(
                    f"Rechargement des commandes réussi - {len(synced)} commandes",
                    user=f"{message.author.display_name} ({message.author.id})",
                    guild=f"{message.guild.name} ({message.guild.id})")

                await asyncio.sleep(10)
                await status_msg.delete()

            except Exception as e:
                embed.color = 0xff0000
                embed.description = f"❌ Erreur lors du rechargement: {str(e)}"
                await status_msg.edit(embed=embed)

                # Log de l'erreur
                self.discord_logger.error_with_traceback(
                    "Erreur lors du rechargement des commandes",
                    e,
                    user=f"{message.author.display_name} ({message.author.id})",
                    guild=f"{message.guild.name} ({message.guild.id})")

                await asyncio.sleep(10)
                await status_msg.delete()

        # Nouvelle commande de test des logs
        elif message.content.strip() == "!test_logs":
            if not has_admin_role(message.author):
                await send_permission_denied(message.channel)
                return

            # Supprimer le message de commande
            try:
                await message.delete()
            except:
                pass

            # Test du système de logs
            result = await self.discord_logger.test_logging(message.guild)

            embed = discord.Embed(title="🧪 Test du Système de Logs",
                                  color=0x3498db)

            if result['channel_found']:
                embed.add_field(name="📍 Canal Admin",
                                value=f"#{result['channel_name']}",
                                inline=True)
                embed.add_field(name="✅ Permissions",
                                value="✅" if result['can_send'] else "❌",
                                inline=True)
                embed.add_field(name="📨 Test Envoyé",
                                value="✅" if result['test_sent'] else "❌",
                                inline=True)

                if result['test_sent']:
                    embed.description = "✅ Système de logs opérationnel !"
                    embed.color = 0x00ff00
                else:
                    embed.description = "⚠️ Problème de permissions ou de configuration"
                    embed.color = 0xff9900
            else:
                embed.description = "❌ Canal admin non configuré"
                embed.color = 0xff0000
                embed.add_field(
                    name="💡 Solution",
                    value=
                    "Configurez la variable CHANNEL_ADMIN_NAME ou CHANNEL_ADMIN_ID",
                    inline=False)

            msg = await message.channel.send(embed=embed)
            await asyncio.sleep(10)
            await msg.delete()