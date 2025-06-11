import discord
from discord.ext import commands
from datetime import datetime, timezone
import os
from flask import Flask
from threading import Thread

# --- Serveur web minimal pour rester actif avec UptimeRobot ---
app = Flask('')

@app.route('/')
def home():
    return "Bot Faerûn actif."

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- Configuration du bot ---
TOKEN = os.getenv('DISCORD_TOKEN')  # récupère le token depuis les secrets
COMMAND_PREFIX = '!'
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents)

@bot.event
async def on_ready():
    print(f'Connecté en tant que {bot.user}')

@bot.command(name='faerun')
async def faerun_date(ctx):
    today = datetime.now(timezone.utc)
    year_dr = today.year - 628
    months_harptos = [
        "Hammer", "Alturiak", "Ches", "Tarsakh", "Mirtul", "Kythorn",
        "Flamerule", "Eleasis", "Eleint", "Marpenoth", "Uktar", "Nightal"
    ]
    day_of_year = today.timetuple().tm_yday
    month_index = (day_of_year - 1) // 30
    day_in_month = ((day_of_year - 1) % 30) + 1

    if month_index >= len(months_harptos):
        month_index = len(months_harptos) - 1
        day_in_month = 30

    month_name = months_harptos[month_index]
    await ctx.send(f"Aujourd’hui dans Faerûn, nous sommes le **{day_in_month} {month_name}, {year_dr} DR**.")

# --- Lancement ---
keep_alive()
bot.run(TOKEN)
