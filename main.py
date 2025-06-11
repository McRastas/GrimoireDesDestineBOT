
#!/usr/bin/env python3
"""
Bot Discord Faerûn - Affiche les dates du calendrier de Faerûn
"""

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
    """Configuration centralisée de l'application"""
    DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
    COMMAND_PREFIX = '!'
    FLASK_HOST = '0.0.0.0'
    FLASK_PORT = 8080
    
    # Calendrier de Faerûn
    MONTHS_HARPTOS = [
        "Hammer", "Alturiak", "Ches", "Tarsakh", "Mirtul", "Kythorn",
        "Flamerule", "Eleasis", "Eleint", "Marpenoth", "Uktar", "Nightal"
    ]
    
    # Décalage pour convertir l'année réelle en années DR (Dale Reckoning)
    DR_YEAR_OFFSET = 628

class FaerunCalendar:
    """Gestion du calendrier de Faerûn"""
    
    @staticmethod
    def get_faerun_date() -> tuple[int, str, int]:
        """
        Retourne la date actuelle dans le calendrier de Faerûn
        Returns:
            tuple: (jour, mois, année_DR)
        """
        today = datetime.now(timezone.utc)
        year_dr = today.year - Config.DR_YEAR_OFFSET
        
        day_of_year = today.timetuple().tm_yday
        month_index = min((day_of_year - 1) // 30, len(Config.MONTHS_HARPTOS) - 1)
        day_in_month = ((day_of_year - 1) % 30) + 1
        
        month_name = Config.MONTHS_HARPTOS[month_index]
        
        return day_in_month, month_name, year_dr

class WebServer:
    """Serveur Flask pour maintenir le bot actif"""
    
    def __init__(self):
        self.app = Flask(__name__)
        self._setup_routes()
    
    def _setup_routes(self):
        """Configuration des routes Flask"""
        @self.app.route('/')
        def home():
            return {
                "status": "active",
                "message": "Bot Faerûn actif",
                "version": "1.0.0"
            }
        
        @self.app.route('/health')
        def health():
            return {"status": "healthy"}
    
    def run(self):
        """Lance le serveur Flask"""
        self.app.run(
            host=Config.FLASK_HOST,
            port=Config.FLASK_PORT,
            debug=False
        )
    
    def start_in_thread(self):
        """Lance le serveur dans un thread séparé"""
        thread = Thread(target=self.run, daemon=True)
        thread.start()
        logger.info(f"Serveur web démarré sur {Config.FLASK_HOST}:{Config.FLASK_PORT}")

class FaerunBot:
    """Bot Discord pour les dates de Faerûn"""
    
    def __init__(self):
        # Configuration des intents Discord
        intents = discord.Intents.default()
        intents.message_content = True
        
        # Initialisation du bot
        self.bot = commands.Bot(
            command_prefix=Config.COMMAND_PREFIX,
            intents=intents,
            help_command=None  # Désactive la commande d'aide par défaut
        )
        
        self._setup_events()
        self._setup_commands()
    
    def _setup_events(self):
        """Configuration des événements du bot"""
        @self.bot.event
        async def on_ready():
            logger.info(f'Bot connecté : {self.bot.user}')
            logger.info(f'Serveurs connectés : {len(self.bot.guilds)}')
    
    def _setup_commands(self):
        """Configuration des commandes du bot"""
        @self.bot.command(name='faerun', help='Affiche la date actuelle dans le calendrier de Faerûn')
        async def faerun_date(ctx):
            try:
                day, month, year = FaerunCalendar.get_faerun_date()
                
                embed = discord.Embed(
                    title="📅 Date de Faerûn",
                    description=f"**{day} {month}, {year} DR**",
                    color=0x8B4513  # Couleur bronze/terre
                )
                embed.set_footer(text="Calendrier de Harptos")
                
                await ctx.send(embed=embed)
                logger.info(f"Commande faerun exécutée par {ctx.author}")
                
            except Exception as e:
                logger.error(f"Erreur lors de l'exécution de la commande faerun: {e}")
                await ctx.send("❌ Une erreur s'est produite lors du calcul de la date.")
        
        @self.bot.command(name='help', help='Affiche cette aide')
        async def help_command(ctx):
            embed = discord.Embed(
                title="🛡️ Commandes du Bot Faerûn",
                color=0x5865F2
            )
            embed.add_field(
                name=f"{Config.COMMAND_PREFIX}faerun",
                value="Affiche la date actuelle dans le calendrier de Faerûn",
                inline=False
            )
            embed.add_field(
                name=f"{Config.COMMAND_PREFIX}help",
                value="Affiche cette aide",
                inline=False
            )
            embed.set_footer(text="Bot créé pour les aventures en Faerûn")
            
            await ctx.send(embed=embed)
    
    def run(self):
        """Lance le bot Discord"""
        if not Config.DISCORD_TOKEN:
            logger.error("Token Discord manquant ! Vérifiez la variable d'environnement DISCORD_TOKEN")
            return
        
        try:
            self.bot.run(Config.DISCORD_TOKEN)
        except Exception as e:
            logger.error(f"Erreur lors du lancement du bot: {e}")

def main():
    """Point d'entrée principal de l'application"""
    logger.info("Démarrage de l'application Bot Faerûn")
    
    # Démarrage du serveur web
    web_server = WebServer()
    web_server.start_in_thread()
    
    # Démarrage du bot Discord
    bot = FaerunBot()
    bot.run()

if __name__ == "__main__":
    main()
