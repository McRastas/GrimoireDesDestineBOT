import os
import logging
from datetime import datetime, timezone
from threading import Thread

import discord
from discord.ext import commands
from flask import Flask

# Configuration du logging pour tracer les événements du bot
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# Classe de configuration centralisée
class Config:
    """Configuration centralisée pour le bot Discord et le serveur web."""

    # Variables d'environnement
    DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
    COMMAND_PREFIX = os.getenv('COMMAND_PREFIX', '!')
    FLASK_HOST = '0.0.0.0'
    FLASK_PORT = int(os.getenv('FLASK_PORT', 8080))

    @classmethod
    def validate(cls):
        """Valide que toutes les variables d'environnement requises sont présentes."""
        if not cls.DISCORD_TOKEN:
            raise ValueError(
                "DISCORD_TOKEN manquant dans les variables d'environnement")
        return True

    # Calendrier de Harptos - Mois de Faerûn
    MONTHS_HARPTOS = [
        "Hammer", "Alturiak", "Ches", "Tarsakh", "Mirtul", "Kythorn",
        "Flamerule", "Eleasis", "Eleint", "Marpenoth", "Uktar", "Nightal"
    ]

    # Festivals de Faerûn avec leur jour dans l'année
    FESTIVALS = {
        30: "Midwinter",  # Fin de l'hiver
        120: "Greengrass",  # Début du printemps
        210: "Midsummer",  # Milieu de l'été
        211: "Shieldmeet",  # Années bissextiles uniquement
        300: "Highharvestide",  # Fin de l'automne
        330: "Feast of the Moon"  # Début de l'hiver
    }

    # Jours de la semaine de Faerûn (tenday = 10 jours)
    WEEKDAYS = [
        "Sunday", "Moonday", "Godsday", "Waterday", "Earthday", "Freeday",
        "Starday", "Marketday", "Solday", "Spiritday"
    ]

    # Décalage entre l'année réelle et l'année DR (Dale Reckoning)
    DR_YEAR_OFFSET = 628


class FaerunCalendar:
    """Classe utilitaire pour gérer le calendrier de Faerûn (Harptos)."""

    @staticmethod
    def is_leap_year(year):
        """Détermine si une année est bissextile selon les règles grégoriennes."""
        return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

    @staticmethod
    def get_season(day_of_year):
        """Retourne la saison basée sur le jour de l'année."""
        if day_of_year < 91:
            return "Winter"
        elif day_of_year < 183:
            return "Spring"
        elif day_of_year < 275:
            return "Summer"
        else:
            return "Autumn"

    @staticmethod
    def get_faerun_date():
        """
        Convertit la date actuelle en date du calendrier de Faerûn.
        
        Returns:
            dict: Dictionnaire contenant jour, mois, année, festival, saison, etc.
        """
        today = datetime.now(timezone.utc)
        year_dr = today.year - Config.DR_YEAR_OFFSET  # Conversion en année DR
        day_of_year = today.timetuple().tm_yday
        leap = FaerunCalendar.is_leap_year(today.year)

        # Ajustement pour les années non-bissextiles (pas de Shieldmeet)
        day_map = day_of_year
        if not leap and day_of_year >= 211:
            day_map -= 1

        # Vérification si c'est un jour de festival
        if day_map in Config.FESTIVALS:
            return {
                "day": None,
                "month": None,
                "year": year_dr,
                "festival": Config.FESTIVALS[day_map],
                "season": FaerunCalendar.get_season(day_map),
                "weekday": None,
                "week":
                (day_map - 1) // 10 + 1  # Semaines de 10 jours (tenday)
            }

        # Calcul du jour et mois normaux (12 mois de 30 jours chacun)
        month_index = (day_map - 1) // 30
        day_in_month = ((day_map - 1) % 30) + 1
        month_name = Config.MONTHS_HARPTOS[month_index]

        # Calcul du jour de la semaine (cycle de 10 jours)
        weekday = Config.WEEKDAYS[(day_map - 1) % 10]
        season = FaerunCalendar.get_season(day_map)
        week = (day_map - 1) // 10 + 1

        return {
            "day": day_in_month,
            "month": month_name,
            "year": year_dr,
            "festival": None,
            "season": season,
            "weekday": weekday,
            "week": week
        }

    @staticmethod
    def get_next_festival():
        """
        Trouve le prochain festival à venir.
        
        Returns:
            dict: Informations sur le prochain festival
        """
        today = datetime.now(timezone.utc)
        year_dr = today.year - Config.DR_YEAR_OFFSET
        day_of_year = today.timetuple().tm_yday
        festivals = []

        # Recherche des festivals restants dans l'année
        for day, name in sorted(Config.FESTIVALS.items()):
            # Ignore Shieldmeet si ce n'est pas une année bissextile
            if day == 211 and not FaerunCalendar.is_leap_year(today.year):
                continue
            if day > day_of_year:
                festivals.append((day, name))

        # Si aucun festival restant cette année, retourne Midwinter de l'année suivante
        if not festivals:
            return {
                "name": "Midwinter",
                "day": 30,
                "month": "Hammer",
                "year": year_dr + 1
            }

        # Calcul des détails du prochain festival
        next_day, name = festivals[0]
        month_index = (next_day - 1) // 30
        month_name = Config.MONTHS_HARPTOS[month_index] if month_index < len(
            Config.MONTHS_HARPTOS) else "Festival"
        return {
            "name": name,
            "day": next_day % 30 or 30,
            "month": month_name,
            "year": year_dr
        }


class WebServer:
    """Serveur web Flask pour maintenir le bot actif et fournir des endpoints de santé."""

    def __init__(self):
        self.app = Flask(__name__)
        self._setup_routes()

    def _setup_routes(self):
        """Configure les routes du serveur web."""

        @self.app.route('/')
        def home():
            """Endpoint principal retournant le statut du bot."""
            return {
                "status": "active",
                "message": "Bot Faerûn actif",
                "version": "1.0.0"
            }

        @self.app.route('/health')
        def health():
            """Endpoint de santé pour les vérifications de disponibilité."""
            return {"status": "healthy"}

    def run(self):
        """Démarre le serveur Flask."""
        self.app.run(host=Config.FLASK_HOST,
                     port=Config.FLASK_PORT,
                     debug=False)

    def start_in_thread(self):
        """Démarre le serveur dans un thread séparé pour ne pas bloquer le bot."""
        thread = Thread(target=self.run, daemon=True)
        thread.start()
        logger.info(
            f"Serveur web démarré sur {Config.FLASK_HOST}:{Config.FLASK_PORT}")


class FaerunBot:
    """Bot Discord principal pour les commandes de calendrier Faerûn."""

    def __init__(self):
        # Configuration des intents Discord
        intents = discord.Intents.default()
        intents.message_content = True  # Nécessaire pour lire le contenu des messages

        # Initialisation du bot avec préfixe personnalisé
        self.bot = commands.Bot(
            command_prefix=Config.COMMAND_PREFIX,
            intents=intents,
            help_command=
            None  # Désactive l'aide par défaut pour utiliser la nôtre
        )

        self._setup_events()
        self._setup_commands()

    def _setup_events(self):
        """Configure les événements du bot Discord."""

        @self.bot.event
        async def on_ready():
            """Événement déclenché quand le bot est prêt."""
            logger.info(f'Bot connecté : {self.bot.user}')
            logger.info(f'Serveurs connectés : {len(self.bot.guilds)}')

        @self.bot.event
        async def on_command_error(ctx, error):
            """Gestionnaire d'erreurs pour les commandes."""
            if isinstance(error, commands.CommandNotFound):
                await ctx.send(
                    f"❓ Commande inconnue. Utilisez `{Config.COMMAND_PREFIX}help-faerun` pour voir les commandes disponibles."
                )
            elif isinstance(error, commands.MissingRequiredArgument):
                await ctx.send(
                    f"❌ Argument manquant. Utilisez `{Config.COMMAND_PREFIX}help-faerun` pour plus d'informations."
                )
            else:
                logger.error(f"Erreur de commande: {error}")
                await ctx.send("❌ Une erreur inattendue s'est produite.")

    def _setup_commands(self):
        """Configure toutes les commandes du bot."""

        @self.bot.command(name='faerun',
                          help="Affiche la date Faerûnienne complète")
        async def faerun_command(ctx):
            """Commande principale pour afficher la date complète de Faerûn."""
            try:
                logger.info(f"Commande faerun exécutée par {ctx.author.name}")
                fae = FaerunCalendar.get_faerun_date()

                # Affichage différent selon si c'est un festival ou un jour normal
                if fae["festival"]:
                    description = f"🎉 **{fae['festival']}**, {fae['year']} DR\nSeason: {fae['season']}, Week {fae['week']}"
                else:
                    description = f"**{fae['weekday']}, {fae['day']} {fae['month']} {fae['year']} DR**\nSeason: {fae['season']}, Week {fae['week']}"

                embed = discord.Embed(title="📅 Date de Faerûn",
                                      description=description,
                                      color=0x8B4513)
                embed.set_footer(text="Calendrier de Harptos")
                await ctx.send(embed=embed)
            except Exception as e:
                logger.error(f"Erreur dans la commande faerun: {e}")
                await ctx.send(
                    "❌ Une erreur s'est produite lors de l'affichage de la date."
                )

        @self.bot.command(name='faerun-semaine',
                          help="Affiche le numéro de semaine Faerûnienne")
        async def week_command(ctx):
            """Affiche le numéro de semaine actuel (tenday)."""
            fae = FaerunCalendar.get_faerun_date()
            await ctx.send(
                f"📆 Nous sommes dans la semaine **{fae['week']}** de l'année {fae['year']} DR."
            )

        @self.bot.command(name='faerun-festival',
                          help="Affiche le prochain festival")
        async def next_festival(ctx):
            """Affiche le prochain festival avec sa date en format classique."""
            fest = FaerunCalendar.get_next_festival()

            # Calcul de la date classique correspondante au festival
            today = datetime.now(timezone.utc)
            current_day_of_year = today.timetuple().tm_yday
            festival_day = fest['day'] if fest['day'] != 30 or fest[
                'name'] != 'Midwinter' else 30

            # Estimation de la date classique du festival
            if fest['year'] > today.year - Config.DR_YEAR_OFFSET:
                # Festival de l'année prochaine
                next_year = today.year + 1
                festival_date = datetime(
                    next_year, 1, 30 if fest['name'] == 'Midwinter' else 1)
            else:
                # Festival de cette année - calcul des jours restants
                days_remaining = 0
                for day, name in sorted(Config.FESTIVALS.items()):
                    if name == fest['name']:
                        days_remaining = day - current_day_of_year
                        break

                if days_remaining > 0:
                    from datetime import timedelta
                    festival_date = today + timedelta(days=days_remaining)
                else:
                    festival_date = today

            # Formatage de la date classique
            classic_date = festival_date.strftime("%d/%m/%Y")

            await ctx.send(
                f"🎊 Le prochain festival est **{fest['name']}**, le {fest['day']} {fest['month']} {fest['year']} DR ({classic_date})."
            )

        @self.bot.command(name='help-faerun',
                          aliases=['aide', 'help'],
                          help="Affiche l'aide")
        async def help_command(ctx):
            """Affiche la liste des commandes disponibles."""
            embed = discord.Embed(title="🛡️ Commandes du Bot Faerûn",
                                  color=0x5865F2)
            embed.add_field(name=f"{Config.COMMAND_PREFIX}faerun",
                            value="Date complète dans le calendrier de Faerûn",
                            inline=False)
            embed.add_field(name=f"{Config.COMMAND_PREFIX}faerun-semaine",
                            value="Numéro de semaine actuelle",
                            inline=False)
            embed.add_field(name=f"{Config.COMMAND_PREFIX}faerun-festival",
                            value="Prochain festival à venir",
                            inline=False)
            embed.add_field(
                name=f"{Config.COMMAND_PREFIX}faerun-jdr <date>",
                value="Convertit une date (DD-MM-YYYY) en date Faerûnienne",
                inline=False)
            embed.add_field(name=f"{Config.COMMAND_PREFIX}help-faerun",
                            value="Affiche cette aide",
                            inline=False)
            embed.set_footer(text="Bot pour D&D Faerûn")
            await ctx.send(embed=embed)

        @self.bot.command(name='faerun-saison',
                          help="Affiche la saison actuelle")
        async def season_command(ctx):
            """Affiche la saison actuelle avec un emoji approprié."""
            try:
                fae = FaerunCalendar.get_faerun_date()
                # Dictionnaire des emojis pour chaque saison
                season_emoji = {
                    "Winter": "❄️",
                    "Spring": "🌸",
                    "Summer": "☀️",
                    "Autumn": "🍂"
                }
                emoji = season_emoji.get(fae['season'], "🌍")
                await ctx.send(
                    f"{emoji} Nous sommes en **{fae['season']}** dans l'année {fae['year']} DR."
                )
            except Exception as e:
                logger.error(f"Erreur dans la commande saison: {e}")
                await ctx.send("❌ Impossible d'afficher la saison.")

        @self.bot.command(name='faerun-complet',
                          help="Affiche toutes les informations de date")
        async def full_info_command(ctx):
            """Affiche un résumé complet de toutes les informations de date."""
            try:
                fae = FaerunCalendar.get_faerun_date()
                next_fest = FaerunCalendar.get_next_festival()

                # Création d'un embed riche avec toutes les informations
                embed = discord.Embed(
                    title="📅 Informations complètes de Faerûn", color=0x8B4513)

                # Affichage conditionnel selon festival ou jour normal
                if fae["festival"]:
                    embed.add_field(name="🎉 Festival",
                                    value=fae['festival'],
                                    inline=True)
                else:
                    embed.add_field(
                        name="📅 Date",
                        value=f"{fae['weekday']}, {fae['day']} {fae['month']}",
                        inline=True)

                embed.add_field(name="🗓️ Année",
                                value=f"{fae['year']} DR",
                                inline=True)
                embed.add_field(name="🌍 Saison",
                                value=fae['season'],
                                inline=True)
                embed.add_field(name="📊 Semaine",
                                value=f"Semaine {fae['week']}",
                                inline=True)
                embed.add_field(
                    name="🎊 Prochain festival",
                    value=
                    f"{next_fest['name']}\n{next_fest['day']} {next_fest['month']}",
                    inline=True)

                embed.set_footer(
                    text="Calendrier de Harptos • Forgotten Realms")
                await ctx.send(embed=embed)
            except Exception as e:
                logger.error(f"Erreur dans la commande complet: {e}")
                await ctx.send(
                    "❌ Impossible d'afficher les informations complètes.")

        @self.bot.command(
            name='faerun-jdr',
            help="Convertit une date (DD-MM-YYYY) en date Faerûnienne")
        async def faerun_jdr_command(ctx, date_str: str):
            """Affiche la date Faerûnienne correspondant à la date donnée (DD-MM-YYYY)."""
            try:
                # Parse de la date au format DD-MM-YYYY
                from datetime import datetime
                try:
                    target_date = datetime.strptime(date_str, "%d-%m-%Y")
                except ValueError:
                    await ctx.send(
                        "❌ Format de date invalide. Utilisez le format DD-MM-YYYY (ex: 15-02-2023)"
                    )
                    return

                # Calcul de l'année DR et du jour de l'année
                year_dr = target_date.year - Config.DR_YEAR_OFFSET
                day_of_year = target_date.timetuple().tm_yday
                leap = FaerunCalendar.is_leap_year(target_date.year)

                # Ajustement si non-bissextile
                day_map = day_of_year
                if not leap and day_of_year >= 211:
                    day_map -= 1

                # Vérifie si c'est un festival
                if day_map in Config.FESTIVALS:
                    nom_festival = Config.FESTIVALS[day_map]
                    saison = FaerunCalendar.get_season(day_map)
                    semaine = (day_map - 1) // 10 + 1
                    await ctx.send(
                        f"🎉 Le **{date_str}** correspond à **{nom_festival}**, {year_dr} DR — Saison : {saison}, Semaine {semaine}"
                    )
                    return

                # Calcul du jour et mois normaux
                month_index = (day_map - 1) // 30
                day_in_month = ((day_map - 1) % 30) + 1
                month_name = Config.MONTHS_HARPTOS[month_index]
                weekday = Config.WEEKDAYS[(day_map - 1) % 10]
                saison = FaerunCalendar.get_season(day_map)
                semaine = (day_map - 1) // 10 + 1

                await ctx.send(
                    f"📅 Le **{date_str}** correspond à **{weekday}, {day_in_month} {month_name} {year_dr} DR** — Saison : {saison}, Semaine {semaine}"
                )
            except Exception as e:
                logger.error(f"Erreur dans faerun-jdr: {e}")
                await ctx.send(
                    "❌ Une erreur est survenue lors de la conversion de la date."
                )

    def run(self):
        """Démarre le bot Discord."""
        if not Config.DISCORD_TOKEN:
            logger.error("Token Discord manquant !")
            return
        try:
            self.bot.run(Config.DISCORD_TOKEN)
        except Exception as e:
            logger.error(f"Erreur au lancement du bot : {e}")


def main():
    """Fonction principale - point d'entrée de l'application."""
    try:
        logger.info("Démarrage de l'application Bot Faerûn")

        # Validation de la configuration avant le démarrage
        Config.validate()

        # Démarrage du serveur web pour maintenir le bot actif
        web_server = WebServer()
        web_server.start_in_thread()

        # Démarrage du bot Discord (bloquant)
        bot = FaerunBot()
        bot.run()

    except ValueError as e:
        logger.error(f"Erreur de configuration: {e}")
    except KeyboardInterrupt:
        logger.info("Arrêt du bot demandé par l'utilisateur")
    except Exception as e:
        logger.error(f"Erreur critique: {e}")
        raise


# Point d'entrée du script
if __name__ == "__main__":
    main()
