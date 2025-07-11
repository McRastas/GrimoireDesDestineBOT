import logging
from datetime import datetime, timezone, timedelta
import asyncio
import re

import discord
from discord import app_commands

from config import Config
from calendar_faerun import FaerunDate

# Configuration plus détaillée des logs
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class FaerunBot(discord.Client):
    """Bot Discord principal pour le calendrier Faerûn."""

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.synced = False

    async def setup_hook(self):
        """Méthode appelée lors du démarrage du bot pour configurer les commandes."""
        logger.info("=== DÉBUT DE SETUP_HOOK ===")

        # Enregistrer les commandes
        await self.add_commands()

        # Vérifier les commandes enregistrées
        logger.info("Commandes enregistrées dans le tree:")
        for cmd in self.tree.get_commands():
            logger.info(f"  - {cmd.name}: {cmd.description}")

        logger.info("=== FIN DE SETUP_HOOK ===")

    async def add_commands(self):
        """Ajoute toutes les commandes au tree."""
        logger.info("Ajout des commandes au tree...")

        # Commande de test simple
        @self.tree.command(name="test", description="Commande de test simple")
        async def test_command(interaction: discord.Interaction):
            await interaction.response.send_message("✅ Le bot fonctionne !",
                                                    ephemeral=True)

        # /info
        @self.tree.command(name="info", description="Informations sur le bot")
        async def info_command(interaction: discord.Interaction):
            embed = discord.Embed(title="🤖 Informations du Bot",
                                  description="Bot Faerûn - Calendrier D&D",
                                  color=0x00ff00)
            embed.add_field(name="Guildes",
                            value=len(self.guilds),
                            inline=True)
            embed.add_field(name="Utilisateurs",
                            value=len(self.users),
                            inline=True)
            embed.add_field(name="Commandes",
                            value=len(self.tree.get_commands()),
                            inline=True)
            await interaction.response.send_message(embed=embed,
                                                    ephemeral=True)

        # /faerun
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

        # /faerunfestival
        @self.tree.command(name="faerunfestival",
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

        # /faeruncomplet
        @self.tree.command(
            name="faeruncomplet",
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

        # /faerunjdr
        @self.tree.command(
            name="faerunjdr",
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

        # /mentionsomeone
        @self.tree.command(
            name="mentionsomeone",
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

        # /mentionlist
        @self.tree.command(
            name="mentionlist",
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
                auteurs = {}
                async for msg in interaction.channel.history(
                        limit=1000, oldest_first=True):
                    if msg.author.bot:
                        continue
                    auteurs[msg.author.id] = msg.author
                if isinstance(interaction.channel,
                              discord.Thread) and interaction.channel.owner_id:
                    auteurs.pop(interaction.channel.owner_id, None)
                if not auteurs:
                    await interaction.response.send_message(
                        "Aucun utilisateur actif trouvé dans ce canal.",
                        ephemeral=True)
                    return
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
                logger.error(f"Erreur dans la commande /mention_list : {e}",
                             exc_info=True)
                try:
                    if not interaction.response.is_done():
                        await interaction.response.send_message(
                            "❌ Une erreur inattendue est survenue.",
                            ephemeral=True)
                except Exception:
                    pass

        # /recapmj
        @self.tree.command(
            name="recapmj",
            description=
            "Compte le nombre de messages dans #recompenses sur 30j où le MJ mentionne au moins 2 personnes"
        )
        @app_commands.describe(
            membre="Le membre dont on veut la stat (par défaut toi)")
        async def recap_mj_command(interaction: discord.Interaction,
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
                (f"**{cible.display_name}** a posté **{nb_messages} poste de récompense** dans #recompenses (sur 30j) où il/elle mentionne au moins deux personnes différentes."
                 ),
                color=0x7289DA)
            await interaction.response.send_message(embed=embed,
                                                    ephemeral=True)

        # /mesquetes
        @self.tree.command(
            name="mesquetes",
            description=
            "Liste les quêtes où tu es mentionné dans #départ-à-l-aventure (dates futures)"
        )
        @app_commands.describe(
            membre="Le membre à rechercher (par défaut toi-même)")
        async def mes_quetes_command(interaction: discord.Interaction,
                                     membre: discord.Member = None):
            # Defer la réponse pour éviter le timeout
            await interaction.response.defer(ephemeral=True)

            cible = membre or interaction.user
            channel = discord.utils.get(interaction.guild.text_channels,
                                        name='départ-à-l-aventure')
            if not channel:
                await interaction.followup.send(
                    "❌ Le canal #départ-à-l-aventure est introuvable.")
                return

            now = datetime.now(timezone.utc)
            thirty_days_ago = now - timedelta(days=30)

            # D'abord, récupérer tous les messages des 30 derniers jours où le joueur est mentionné
            messages_avec_mention = []
            messages_parcourus = 0

            async for message in channel.history(limit=1000,
                                                 after=thirty_days_ago):
                messages_parcourus += 1
                if message.author.bot:
                    continue
                if cible in message.mentions:
                    messages_avec_mention.append(message)

            # Maintenant, analyser ces messages pour trouver des dates
            resultats_futures = []
            resultats_sans_date = []

            for message in messages_avec_mention:
                premiere_ligne = message.content.split('\n', 1)[0].strip()

                # Chercher une date dans le message avec plusieurs formats
                date_patterns = [
                    # JJ/MM/AAAA ou JJ-MM-AAAA
                    r'(\d{1,2})[/\-](\d{1,2})[/\-](\d{4})',
                    # JJ/MM/AA ou JJ-MM-AA
                    r'(\d{1,2})[/\-](\d{1,2})[/\-](\d{2})',
                    # JJ/MM ou JJ-MM (sans année)
                    r'(\d{1,2})[/\-](\d{1,2})(?![/\-\d])',
                    # JJ.MM.AAAA ou JJ.MM
                    r'(\d{1,2})\.(\d{1,2})(?:\.(\d{2,4}))?',
                    # JJ MM AAAA (avec espaces)
                    r'(\d{1,2})\s+(\d{1,2})\s+(\d{4})',
                ]

                date_trouvee = False
                for pattern in date_patterns:
                    date_match = re.search(pattern, message.content)
                    if date_match:
                        try:
                            jour = int(date_match.group(1))
                            mois = int(date_match.group(2))

                            # Validation basique
                            if not (1 <= jour <= 31 and 1 <= mois <= 12):
                                continue

                            # Gestion de l'année selon le nombre de groupes capturés
                            if len(date_match.groups()
                                   ) >= 3 and date_match.group(3):
                                annee = int(date_match.group(3))
                                if annee < 100:  # Année sur 2 chiffres
                                    annee = 2000 + annee
                            else:
                                # Pas d'année spécifiée
                                # Logique améliorée pour gérer la fin d'année
                                annee = now.year

                                # Si on est en fin d'année (novembre/décembre) et que la date est en début d'année
                                if now.month >= 11 and mois <= 2:
                                    # On suppose que c'est pour l'année prochaine
                                    annee = now.year + 1
                                # Si on est en début d'année (janvier/février) et que la date est en fin d'année
                                elif now.month <= 2 and mois >= 11:
                                    # On suppose que c'est pour l'année en cours (déjà passé)
                                    continue  # On ignore cette date car elle est passée
                                else:
                                    # Cas normal : on vérifie si la date est passée
                                    try:
                                        test_date = datetime(
                                            annee,
                                            mois,
                                            jour,
                                            tzinfo=timezone.utc)
                                        if test_date < now:
                                            # La date est passée cette année, on prend l'année prochaine
                                            annee = now.year + 1
                                    except ValueError:
                                        # Date invalide pour cette année, essayer l'année prochaine
                                        annee = now.year + 1

                            # Créer la date de la quête
                            quest_date = datetime(annee,
                                                  mois,
                                                  jour,
                                                  tzinfo=timezone.utc)
                            jours_restants = (quest_date - now).days

                            # Ne garder que les quêtes futures ou d'aujourd'hui (max 60 jours)
                            if 0 <= jours_restants <= 60:
                                date_formatee = f"{jour:02d}/{mois:02d}/{annee}"

                                if jours_restants == 0:
                                    quand = "🔴 **AUJOURD'HUI**"
                                elif jours_restants == 1:
                                    quand = "🟠 **Demain**"
                                elif jours_restants <= 7:
                                    quand = f"🟡 Dans {jours_restants} jours"
                                else:
                                    quand = f"🟢 Dans {jours_restants} jours"

                                resultats_futures.append({
                                    'jours':
                                    jours_restants,
                                    'texte':
                                    f"{quand} ({date_formatee})\n└─ {premiere_ligne[:80]}{'...' if len(premiere_ligne) > 80 else ''}"
                                })
                                date_trouvee = True
                                break  # Sortir de la boucle des patterns
                        except ValueError:
                            # Date invalide, essayer le pattern suivant
                            continue

                if not date_trouvee:
                    # Pas de date trouvée avec aucun pattern
                    resultats_sans_date.append(premiere_ligne)

            # Trier les quêtes futures par date
            resultats_futures.sort(key=lambda x: x['jours'])

            # Construire l'embed
            embed = discord.Embed(
                title=f"📅 Quêtes à venir - {cible.display_name}",
                color=0x3498db)

            if resultats_futures:
                desc_futures = "\n\n".join(
                    [r['texte'] for r in resultats_futures[:10]])
                embed.add_field(
                    name=f"🎯 Quêtes planifiées ({len(resultats_futures)})",
                    value=desc_futures,
                    inline=False)
            else:
                embed.add_field(
                    name="🎯 Quêtes planifiées",
                    value="*Aucune quête avec date future trouvée*",
                    inline=False)

            # Ajouter les mentions sans date si peu de quêtes futures
            if resultats_sans_date and len(resultats_futures) < 5:
                desc_sans_date = "\n".join([
                    f"• {q[:60]}..." if len(q) > 60 else f"• {q}"
                    for q in resultats_sans_date[:5]
                ])
                embed.add_field(
                    name=
                    f"📌 Mentions récentes sans date ({len(resultats_sans_date)})",
                    value=desc_sans_date,
                    inline=False)

            embed.set_footer(
                text=
                f"Analysé {messages_parcourus} messages des 30 derniers jours | {len(messages_avec_mention)} mentions trouvées"
            )

            await interaction.followup.send(embed=embed)

        logger.info(f"Commandes ajoutées: {len(self.tree.get_commands())}")

    async def on_ready(self):
        """Événement déclenché quand le bot est prêt"""
        logger.info("=== BOT CONNECTÉ ===")
        logger.info(f"Bot: {self.user} (ID: {self.user.id})")
        logger.info(f"Présent dans {len(self.guilds)} serveur(s)")

        for guild in self.guilds:
            logger.info(f"  - Serveur: {guild.name} (ID: {guild.id})")

            # Récupérer les permissions du bot dans ce serveur
            me = guild.me
            logger.info(f"Permissions dans {guild.name}:")
            logger.info(
                f"  - send_messages: {me.guild_permissions.send_messages}")
            logger.info(
                f"  - read_messages: {me.guild_permissions.read_messages}")
            logger.info(f"  - embed_links: {me.guild_permissions.embed_links}")
            logger.info(
                f"  - use_application_commands: {me.guild_permissions.use_application_commands}"
            )

        logger.info("=== BOT PRÊT ===")

        # Synchroniser les commandes avec Discord
        if not self.synced:
            await self.sync_commands()
            self.synced = True

    async def sync_commands(self):
        """Synchronise les commandes slash."""
        logger.info("=== DÉBUT SYNCHRONISATION ===")

        try:
            commands_count = len(self.tree.get_commands())
            logger.info(
                f"Nombre de commandes à synchroniser: {commands_count}")

            if commands_count == 0:
                logger.error("❌ AUCUNE COMMANDE TROUVÉE")
                return

            if Config.GUILD_ID:
                logger.info(
                    f"Synchronisation pour la guild: {Config.GUILD_ID}")
                guild = discord.Object(id=Config.GUILD_ID)

                # Copier les commandes globales vers la guild
                self.tree.copy_global_to(guild=guild)
                logger.info("Commandes copiées vers la guild")

                # Synchroniser avec Discord
                synced = await self.tree.sync(guild=guild)
                logger.info(
                    f"✅ {len(synced)} commandes synchronisées pour la guild {Config.GUILD_ID}"
                )

                # Lister les commandes synchronisées
                for cmd in synced:
                    logger.info(f"  - Synchronisé: {cmd.name}")

            else:
                logger.info("Synchronisation globale")
                synced = await self.tree.sync()
                logger.info(
                    f"✅ {len(synced)} commandes synchronisées globalement")

        except discord.HTTPException as e:
            logger.error(f"❌ Erreur HTTP lors de la synchronisation: {e}")
            logger.error(f"Status: {e.status}, Text: {e.text}")
        except Exception as e:
            logger.error(f"❌ Erreur lors de la synchronisation: {e}")
            logger.exception("Détails de l'erreur:")

        logger.info("=== FIN SYNCHRONISATION ===")

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

        # Commande de purge
        elif message.content.strip() == "!purge_commands":
            if not message.author.guild_permissions.administrator:
                return

            # Supprimer le message de commande
            try:
                await message.delete()
            except:
                pass

            embed = discord.Embed(title="🧹 Purge des commandes",
                                  description="Nettoyage en cours...",
                                  color=0xff9900)
            status_msg = await message.channel.send(embed=embed)

            try:
                # Purger les commandes de la guild actuelle
                guild_commands = await self.tree.fetch_commands(
                    guild=message.guild)
                if guild_commands:
                    for cmd in guild_commands:
                        await cmd.delete()

                # Vider le tree local
                self.tree.clear_commands(guild=message.guild)

                # Re-ajouter les commandes
                await self.add_commands()

                # Resynchroniser
                await asyncio.sleep(1)
                synced = await self.tree.sync(guild=message.guild)

                embed.color = 0x00ff00
                embed.description = "✅ Purge terminée et commandes resynchronisées"
                embed.add_field(
                    name="🔄 Nouvelles commandes",
                    value=f"{len(synced)} commande(s) synchronisée(s)",
                    inline=False)

                await status_msg.edit(embed=embed)
                await asyncio.sleep(10)
                await status_msg.delete()

            except Exception as e:
                embed.color = 0xff0000
                embed.description = f"❌ Erreur lors de la purge: {str(e)}"
                await status_msg.edit(embed=embed)
                await asyncio.sleep(10)
                await status_msg.delete()

        # Commande clear simple
        elif message.content.strip() == "!clear_commands":
            if not message.author.guild_permissions.administrator:
                return

            # Supprimer le message de commande
            try:
                await message.delete()
            except:
                pass

            try:
                # Supprimer toutes les commandes de la guild
                commands = await self.tree.fetch_commands(guild=message.guild)

                if commands:
                    for cmd in commands:
                        await cmd.delete()
                    msg = await message.channel.send(
                        f"✅ {len(commands)} commande(s) supprimée(s) de ce serveur"
                    )
                else:
                    msg = await message.channel.send(
                        "❌ Aucune commande trouvée sur ce serveur")

                await asyncio.sleep(10)
                await msg.delete()

            except Exception as e:
                msg = await message.channel.send(f"❌ Erreur: {e}")
                await asyncio.sleep(10)
                await msg.delete()
