import os
import logging
from datetime import datetime, timezone
from threading import Thread

import discord
from discord.ext import commands
from flask import Flask

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
class Config:
    DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
    COMMAND_PREFIX = '!'
    FLASK_HOST = '0.0.0.0'
    FLASK_PORT = 8080

    MONTHS_HARPTOS = [
        "Hammer", "Alturiak", "Ches", "Tarsakh", "Mirtul", "Kythorn",
        "Flamerule", "Eleasis", "Eleint", "Marpenoth", "Uktar", "Nightal"
    ]

    FESTIVALS = {
        30: "Midwinter",
        120: "Greengrass",
        210: "Midsummer",
        211: "Shieldmeet",  # Leap year only
        300: "Highharvestide",
        330: "Feast of the Moon"
    }

    WEEKDAYS = ["Sunday", "Moonday", "Godsday", "Waterday", "Earthday", "Freeday", "Starday", "Marketday", "Solday", "Spiritday"]
    DR_YEAR_OFFSET = 628

class FaerunCalendar:
    @staticmethod
    def is_leap_year(year):
        return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

    @staticmethod
    def get_season(day_of_year):
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
        today = datetime.now(timezone.utc)
        year_dr = today.year - Config.DR_YEAR_OFFSET
        day_of_year = today.timetuple().tm_yday
        leap = FaerunCalendar.is_leap_year(today.year)

        day_map = day_of_year
        if not leap and day_of_year >= 211:
            day_map -= 1

        if day_map in Config.FESTIVALS:
            return {
                "day": None,
                "month": None,
                "year": year_dr,
                "festival": Config.FESTIVALS[day_map],
                "season": FaerunCalendar.get_season(day_map),
                "weekday": None,
                "week": (day_map - 1) // 10 + 1
            }

        month_index = (day_map - 1) // 30
        day_in_month = ((day_map - 1) % 30) + 1
        month_name = Config.MONTHS_HARPTOS[month_index]

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
        today = datetime.now(timezone.utc)
        year_dr = today.year - Config.DR_YEAR_OFFSET
        day_of_year = today.timetuple().tm_yday
        festivals = []

        for day, name in sorted(Config.FESTIVALS.items()):
            if day == 211 and not FaerunCalendar.is_leap_year(today.year):
                continue
            if day > day_of_year:
                festivals.append((day, name))

        if not festivals:
            return {"name": "Midwinter", "day": 30, "month": "Hammer", "year": year_dr + 1}

        next_day, name = festivals[0]
        month_index = (next_day - 1) // 30
        month_name = Config.MONTHS_HARPTOS[month_index] if month_index < len(Config.MONTHS_HARPTOS) else "Festival"
        return {"name": name, "day": next_day % 30 or 30, "month": month_name, "year": year_dr}

class WebServer:
    def __init__(self):
        self.app = Flask(__name__)
        self._setup_routes()

    def _setup_routes(self):
        @self.app.route('/')
        def home():
            return {"status": "active", "message": "Bot Faerûn actif", "version": "1.0.0"}

        @self.app.route('/health')
        def health():
            return {"status": "healthy"}

    def run(self):
        self.app.run(host=Config.FLASK_HOST, port=Config.FLASK_PORT, debug=False)

    def start_in_thread(self):
        thread = Thread(target=self.run, daemon=True)
        thread.start()
        logger.info(f"Serveur web démarré sur {Config.FLASK_HOST}:{Config.FLASK_PORT}")

class FaerunBot:
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True

        self.bot = commands.Bot(
            command_prefix=Config.COMMAND_PREFIX,
            intents=intents,
            help_command=None
        )

        self._setup_events()
        self._setup_commands()

    def _setup_events(self):
        @self.bot.event
        async def on_ready():
            logger.info(f'Bot connecté : {self.bot.user}')
            logger.info(f'Serveurs connectés : {len(self.bot.guilds)}')

    def _setup_commands(self):
        @self.bot.command(name='faerun', help="Affiche la date Faerûnienne complète")
        async def faerun_command(ctx):
            fae = FaerunCalendar.get_faerun_date()

            if fae["festival"]:
                description = f"🎉 **{fae['festival']}**, {fae['year']} DR\nSeason: {fae['season']}, Week {fae['week']}"
            else:
                description = f"**{fae['weekday']}, {fae['day']} {fae['month']} {fae['year']} DR**\nSeason: {fae['season']}, Week {fae['week']}"

            embed = discord.Embed(title="📅 Date de Faerûn", description=description, color=0x8B4513)
            embed.set_footer(text="Calendrier de Harptos")
            await ctx.send(embed=embed)

        @self.bot.command(name='faerun-semaine', help="Affiche le numéro de semaine Faerûnienne")
        async def week_command(ctx):
            fae = FaerunCalendar.get_faerun_date()
            await ctx.send(f"📆 Nous sommes dans la semaine **{fae['week']}** de l'année {fae['year']} DR.")

        @self.bot.command(name='faerun-festival', help="Affiche le prochain festival")
        async def next_festival(ctx):
            fest = FaerunCalendar.get_next_festival()
            await ctx.send(f"🎊 Le prochain festival est **{fest['name']}**, le {fest['day']} {fest['month']} {fest['year']} DR.")

        @self.bot.command(name='help-faerun', help="Affiche l'aide")
        async def help_command(ctx):
            embed = discord.Embed(title="🛡️ Commandes du Bot Faerûn", color=0x5865F2)
            embed.add_field(name=f"{Config.COMMAND_PREFIX}faerun", value="Date complète dans le calendrier de Faerûn", inline=False)
            embed.add_field(name=f"{Config.COMMAND_PREFIX}faerun-semaine", value="Numéro de semaine actuelle", inline=False)
            embed.add_field(name=f"{Config.COMMAND_PREFIX}faerun-festival", value="Prochain festival à venir", inline=False)
            embed.add_field(name=f"{Config.COMMAND_PREFIX}help-faerun", value="Affiche cette aide", inline=False)
            embed.set_footer(text="Bot pour D&D Faerûn")
            await ctx.send(embed=embed)

    def run(self):
        if not Config.DISCORD_TOKEN:
            logger.error("Token Discord manquant !")
            return
        try:
            self.bot.run(Config.DISCORD_TOKEN)
        except Exception as e:
            logger.error(f"Erreur au lancement du bot : {e}")


def main():
    logger.info("Démarrage du bot Faerûn")
    web_server = WebServer()
    web_server.start_in_thread()
    bot = FaerunBot()
    bot.run()


if __name__ == "__main__":
    main()