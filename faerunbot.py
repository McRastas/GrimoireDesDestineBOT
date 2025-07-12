import logging
import asyncio

import discord
from discord import app_commands

from config import Config
from commands import ALL_COMMANDS

# Configuration du niveau de log global
LOG_LEVEL = logging.INFO  # ← Changez juste cette ligne !

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
                return

            if Config.GUILD_ID:
                guild = discord.Object(id=Config.GUILD_ID)
                self.tree.copy_global_to(guild=guild)
                synced = await self.tree.sync(guild=guild)
                logger.info(
                    f"✅ {len(synced)} commandes synchronisées (guild: {Config.GUILD_ID})"
                )
            else:
                synced = await self.tree.sync()
                logger.info(
                    f"✅ {len(synced)} commandes synchronisées (global)")

        except discord.HTTPException as e:
            logger.error(f"Erreur HTTP synchronisation: {e.status}")
        except Exception as e:
            logger.error(f"Erreur synchronisation: {e}")

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
            if not message.author.guild_permissions.administrator:
                msg = await message.channel.send(
                    "❌ Permission refusée - Administrateur requis")
                await asyncio.sleep(5)
                await msg.delete()
                return

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

                await status_msg.edit(content=None, embed=embed)
                # Supprimer après 10 secondes
                await asyncio.sleep(10)
                await status_msg.delete()

            except Exception as e:
                logger.error(f"Erreur sync manuelle: {e}")
                await status_msg.edit(content=f"❌ Erreur: {e}")
                await asyncio.sleep(10)
                await status_msg.delete()

        # Commande de debug
        elif message.content.strip() == "!debug_bot":
            if not message.author.guild_permissions.administrator:
                return

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

            msg = await message.channel.send(embed=embed)
            # Supprimer après 15 secondes
            await asyncio.sleep(15)
            await msg.delete()

        # Commande de rechargement des commandes
        elif message.content.strip() == "!reload_commands":
            if not message.author.guild_permissions.administrator:
                return

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

                await status_msg.edit(embed=embed)
                await asyncio.sleep(10)
                await status_msg.delete()

            except Exception as e:
                embed.color = 0xff0000
                embed.description = f"❌ Erreur lors du rechargement: {str(e)}"
                await status_msg.edit(embed=embed)
                await asyncio.sleep(10)
                await status_msg.delete()
