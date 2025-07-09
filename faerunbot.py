import logging
from datetime import datetime, timezone, timedelta

import discord
from discord import app_commands

from config import Config
from calendar_faerun import FaerunDate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FaerunBot(discord.Client):
    """Bot Discord principal pour le calendrier Faerûn."""

    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        logger.info(f"Configuration des commandes slash...")
        logger.info(f"GUILD_ID configuré : {getattr(Config, 'GUILD_ID', 'Non défini')}")
        
        # /faerun : Date complète
        @self.tree.command(name="faerun",
                           description="Affiche la date Faerûnienne complète")
        async def faerun_command(interaction: discord.Interaction):
            fae = FaerunDate(datetime.now(timezone.utc))
            embed = discord.Embed(title="📅 Date de Faerûn",
                                  description=fae.to_locale_string(),
                                  color=0x8B4513)
            embed.set_footer(text="Calendrier de Harptos")
            await interaction.response.send_message(embed=embed,
                                                    ephemeral=True)

        # /faerun_festival : Prochain festival
        @self.tree.command(name="faerun_festival",
                           description="Affiche le prochain festival")
        async def faerun_festival_command(interaction: discord.Interaction):
            now = datetime.now()
            for jours_test in range(366):
                test_date = now + timedelta(days=jours_test)
                fae = FaerunDate.from_datetime(test_date)
                festival = fae.get_festival()
                if festival:
                    embed = discord.Embed(
                        title="🎊 Prochain festival de Faerûn",
                        description=
                        f"**{festival}**, le {test_date.day} {fae.get_month()} {fae.get_dr_year()} DR ({test_date.strftime('%d/%m/%Y')})",
                        color=0xFFD700)
                    await interaction.response.send_message(embed=embed,
                                                            ephemeral=True)
                    return
            await interaction.response.send_message(
                "Aucun festival trouvé cette année (bizarre).", ephemeral=True)

        # /faerun_complet : Infos complètes
        @self.tree.command(
            name="faerun_complet",
            description="Affiche toutes les infos de date Faerûnienne")
        async def faerun_complet_command(interaction: discord.Interaction):
            fae = FaerunDate(datetime.now(timezone.utc))
            embed = discord.Embed(title="📅 Infos complètes de Faerûn",
                                  color=0x8B4513)
            embed.add_field(name="📅 Date",
                            value=fae.to_locale_string(),
                            inline=True)
            embed.add_field(name="🗓️ Année",
                            value=f"{fae.get_dr_year()} DR",
                            inline=True)
            embed.add_field(name="🌍 Saison",
                            value=fae.get_season(),
                            inline=True)
            embed.add_field(name="📊 Semaine",
                            value=f"Semaine {fae.get_week_of_year()}",
                            inline=True)
            embed.set_footer(text="Calendrier de Harptos • Forgotten Realms")
            await interaction.response.send_message(embed=embed,
                                                    ephemeral=True)

        # /faerun_jdr <date>
        @self.tree.command(
            name="faerun_jdr",
            description="Convertit une date (JJ-MM-AAAA) en date Faerûnienne")
        @app_commands.describe(date_str="Date au format JJ-MM-AAAA")
        async def faerun_jdr_command(interaction: discord.Interaction,
                                     date_str: str):
            try:
                target_date = datetime.strptime(date_str, "%d-%m-%Y")
            except ValueError:
                await interaction.response.send_message(
                    "❌ Format de date invalide. Utilisez JJ-MM-AAAA (ex: 15-02-2023)",
                    ephemeral=True)
                return
            fae = FaerunDate(target_date)
            embed = discord.Embed(title="📅 Conversion de date Faerûnienne",
                                  description=fae.to_locale_string(),
                                  color=0x8B4513)
            await interaction.response.send_message(embed=embed,
                                                    ephemeral=True)

        # /mentions [membre] : Nombre de mentions dans #recompenses
        @self.tree.command(
            name="mention_someone",
            description="Compte les mentions dans #recompenses sur 30j")
        @app_commands.describe(
            membre="Le membre dont on veut le nombre de mentions")
        async def mentions_command(interaction: discord.Interaction,
                                   membre: discord.Member = None):
            cible = membre or interaction.user
            channel = discord.utils.get(interaction.guild.text_channels,
                                        name='recompenses')
            if not channel:
                await interaction.response.send_message(
                    "❌ Le canal #recompenses est introuvable.", ephemeral=True)
                return
            count = 0
            now = datetime.now(timezone.utc)
            thirty_days_ago = now - timedelta(days=30)
            async for message in channel.history(limit=1000,
                                                 after=thirty_days_ago):
                if cible in message.mentions:
                    count += 1
            embed = discord.Embed(
                title="📢 Statistiques de mentions",
                description=
                f"**{cible.display_name}** a été mentionné **{count} fois** dans #recompenses sur 30 jours.",
                color=0x7289DA)
            await interaction.response.send_message(embed=embed,
                                                    ephemeral=True)

        # /mentions_all : Stats de tous les posteurs de ce salon dans #recompenses
        @self.tree.command(
            name="mention_list",
            description=
            "Compte les mentions de tous les posteurs de ce salon dans #recompenses (30 derniers jours)"
        )
        async def mentions_all_command(interaction: discord.Interaction):
            try:
                recompenses_channel = discord.utils.get(
                    interaction.guild.text_channels, name='recompenses')
                if not recompenses_channel:
                    await interaction.response.send_message(
                        "❌ Le canal #recompenses est introuvable.",
                        ephemeral=True)
                    return

                now = datetime.now(timezone.utc)
                thirty_days_ago = now - timedelta(days=30)

                # Membres ayant posté au moins 1 message ici (hors bots)
                auteurs = {}
                async for msg in interaction.channel.history(
                        limit=1000, oldest_first=True):
                    if msg.author.bot:
                        continue
                    auteurs[msg.author.id] = msg.author

                # Si thread, ignorer le créateur du thread
                if isinstance(interaction.channel,
                              discord.Thread) and interaction.channel.owner_id:
                    auteurs.pop(interaction.channel.owner_id, None)

                if not auteurs:
                    await interaction.response.send_message(
                        "Aucun utilisateur actif trouvé dans ce canal.",
                        ephemeral=True)
                    return

                # Compte combien de fois chaque auteur a été mentionné dans #recompenses sur 30j
                mention_counts = {user_id: 0 for user_id in auteurs}
                async for msg in recompenses_channel.history(
                        limit=1000, after=thirty_days_ago):
                    for user_id, user in auteurs.items():
                        if user in msg.mentions:
                            mention_counts[user_id] += 1

                lignes = [
                    f"• **{auteurs[user_id].display_name}** : {count} mention(s)"
                    for user_id, count in sorted(mention_counts.items(),
                                                 key=lambda item: item[1],
                                                 reverse=True)
                ]
                description = "\n".join(
                    lignes) if lignes else "Aucune donnée trouvée."

                embed = discord.Embed(
                    title="📊 Mentions dans #recompenses (30 derniers jours)",
                    description=description,
                    color=0x00b0f4)
                await interaction.response.send_message(embed=embed,
                                                        ephemeral=True)
            except Exception as e:
                logger.error(f"Erreur dans la commande /mention_all : {e}",
                             exc_info=True)
                try:
                    if not interaction.response.is_done():
                        await interaction.response.send_message(
                            "❌ Une erreur inattendue est survenue.",
                            ephemeral=True)
                except Exception:
                    pass

        # /recap_mj : Messages de récompense multi-mention
        @self.tree.command(
            name="recap_mj",
            description=
            "Compte le nombre de messages dans #recompenses sur 30j où le membre mentionne au moins deux personnes"
        )
        @app_commands.describe(
            membre="Le membre dont on veut la stat (par défaut toi)")
        async def postes_recompense_multi_command(
                interaction: discord.Interaction,
                membre: discord.Member = None):
            cible = membre or interaction.user
            channel = discord.utils.get(interaction.guild.text_channels,
                                        name='recompenses')
            if not channel:
                await interaction.response.send_message(
                    "❌ Le canal #recompenses est introuvable.", ephemeral=True)
                return

            now = datetime.now(timezone.utc)
            thirty_days_ago = now - timedelta(days=30)
            nb_messages = 0
            total_mentions = 0

            async for message in channel.history(limit=1000,
                                                 after=thirty_days_ago):
                if message.author.id == cible.id:
                    mentions_uniques = set(user.id for user in message.mentions
                                           if user.id != cible.id)
                    if len(mentions_uniques) >= 2:
                        nb_messages += 1
                        total_mentions += len(mentions_uniques)

            embed = discord.Embed(
                title="📋 Messages multi-mentions dans #recompenses",
                description=
                (f"**{cible.display_name}** a posté **{nb_messages} poste de récompense** "
                 f"dans #recompenses (sur 30j) où il/elle mentionne au moins deux personnes différentes."
                 ),
                color=0x7289DA)
            await interaction.response.send_message(embed=embed,
                                                    ephemeral=True)

        @self.tree.command(
            name="mes_quêtes",
            description="Liste les quêtes où tu es mentionné dans #départ-à-l-aventure (avec date/heure si trouvée)"
        )
        @app_commands.describe(membre="Le membre à rechercher (par défaut toi-même)")
        async def mes_quetes_command(
            interaction: discord.Interaction,
            membre: discord.Member = None
        ):
            cible = membre or interaction.user
            channel = discord.utils.get(interaction.guild.text_channels, name='départ-à-l-aventure')
            if not channel:
                await interaction.response.send_message(
                    "❌ Le canal #départ-à-l-aventure est introuvable.",
                    ephemeral=True)
                return

            now = datetime.now(timezone.utc)
            thirty_days_ago = now - timedelta(days=30)

            resultats = []
            async for message in channel.history(limit=1000, after=thirty_days_ago, oldest_first=True):
                # Ignore les messages des bots
                if message.author.bot:
                    continue
                # Vérifie que la cible est mentionnée
                if cible in message.mentions:
                    # Prend la première ligne, ou tout le message s'il n'y a qu'une ligne
                    premiere_ligne = message.content.split('\n', 1)[0].strip()
                    date_post = message.created_at.astimezone(timezone.utc).strftime("%d/%m/%Y %Hh%M UTC")
                    resultats.append(f"- {premiere_ligne} *(posté le {date_post})*")

            if not resultats:
                desc = f"Aucune quête trouvée pour {cible.display_name} dans les 30 derniers jours."
            else:
                desc = "\n".join(resultats[:20])  # Max 20 résultats pour Discord (sinon ça coupe)

            embed = discord.Embed(
                title=f"Quêtes mentionnant {cible.display_name} (30j)",
                description=desc,
                color=0x3498db
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # Synchroniser les commandes après les avoir définies
        try:
            if getattr(Config, "GUILD_ID", None):
                synced = await self.tree.sync(guild=discord.Object(id=Config.GUILD_ID))
                logger.info(f"Synchronisées {len(synced)} slash commands pour la guild ID: {Config.GUILD_ID}")
            else:
                synced = await self.tree.sync()
                logger.info(f"Synchronisées {len(synced)} slash commands globalement")
                logger.info("💡 Conseil: Définis GUILD_ID dans les secrets pour une sync plus rapide en développement")
        except Exception as e:
            logger.error(f"Erreur lors de la sync des slash commands : {e}", exc_info=True)
        
        logger.info("Commandes slash configurées et synchronisées")

    async def on_ready(self):
        logger.info(f'Bot connecté : {self.user} (ID: {self.user.id})')
        # Afficher les guilds où le bot est présent
        logger.info(f"Bot présent dans {len(self.guilds)} serveur(s):")
        for guild in self.guilds:
            logger.info(f"  - {guild.name} (ID: {guild.id})")
