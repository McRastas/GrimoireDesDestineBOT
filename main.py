import discord
from discord.ext import commands
from datetime import datetime, timezone, timedelta

TOKEN = ''  # remplace ça par le token du bot
GUILD_ID = 123456789012345678  # optionnel, pour le test

COMMAND_PREFIX = '!'
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents)

@bot.event
async def on_ready():
    print(f'Connecté en tant que {bot.user}')

@bot.command(name='faerun')
async def faerun_date(ctx):
    # Date réelle
    today = datetime.now(timezone.utc)

    # Calendrier de Harptos = même structure que le nôtre, mais avec 1397 comme année de base
    year_dr = today.year - 628
    months_harptos = [
        "Hammer", "Alturiak", "Ches", "Tarsakh", "Mirtul", "Kythorn",
        "Flamerule", "Eleasis", "Eleint", "Marpenoth", "Uktar", "Nightal"
    ]

    # Chaque mois fait 30 jours. Les jours spéciaux sont ignorés ici pour simplifier.
    # Convertit la date actuelle en "jour de l'année"
    day_of_year = today.timetuple().tm_yday

    # Gestion simple : chaque mois = 30 jours
    month_index = (day_of_year - 1) // 30
    day_in_month = ((day_of_year - 1) % 30) + 1

    if month_index >= len(months_harptos):
        month_index = len(months_harptos) - 1
        day_in_month = 30  # cas du 31/12

    month_name = months_harptos[month_index]

    await ctx.send(f"Aujourd’hui dans Faerûn, nous sommes le **{day_in_month} {month_name}, {year_dr} DR**.")

bot.run(TOKEN)
