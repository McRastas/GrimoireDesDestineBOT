"""
Système de logs quotidiens pour le Bot Faerûn.

Ce module génère des fichiers de logs quotidiens au format DDMMYYYY
pour tracer l'utilisation des commandes et les événements du bot.
"""

import logging
import os
from datetime import datetime, timezone
from logging.handlers import TimedRotatingFileHandler
import discord
from typing import Optional


class DailyFileLogger:
    """Gestionnaire de logs quotidiens avec rotation automatique."""
    
    def __init__(self, logs_dir: str = "/app/logs"):
        self.logs_dir = logs_dir
        self.command_logger = None
        self._setup_logs_directory()
        self._setup_loggers()
    
    def _setup_logs_directory(self):
        """Crée le répertoire de logs s'il n'existe pas."""
        try:
            os.makedirs(self.logs_dir, exist_ok=True)
            print(f"✓ Répertoire de logs initialisé : {self.logs_dir}")
        except Exception as e:
            print(f"⚠️ Erreur création répertoire logs : {e}")
            # Fallback vers un répertoire local
            self.logs_dir = "./logs"
            os.makedirs(self.logs_dir, exist_ok=True)
            print(f"✓ Fallback répertoire logs : {self.logs_dir}")
    
    def _setup_loggers(self):
        """Configure les loggers avec rotation quotidienne."""
        
        # LOGGER COMMANDES
        self.command_logger = logging.getLogger('faerun_commands')
        self.command_logger.setLevel(logging.INFO)
        
        # Éviter la duplication si déjà configuré
        if not self.command_logger.handlers:
            # Handler avec rotation quotidienne
            command_handler = TimedRotatingFileHandler(
                filename=os.path.join(self.logs_dir, "commands.log"),
                when='midnight',
                interval=1,
                backupCount=30,  # Garder 30 jours
                encoding='utf-8'
            )
            
            # Format pour les commandes
            command_formatter = logging.Formatter(
                '%(asctime)s | %(levelname)s | %(message)s',
                datefmt='%d/%m/%Y %H:%M:%S'
            )
            command_handler.setFormatter(command_formatter)
            
            # Nommage des fichiers avec format DDMMYYYY
            command_handler.namer = self._get_log_filename
            
            self.command_logger.addHandler(command_handler)
    
    def _get_log_filename(self, default_name: str) -> str:
        """
        Génère le nom de fichier au format DDMMYYYY.
        """
        # Extraire la date du nom par défaut
        # Format par défaut : commands.log.2024-01-15
        parts = default_name.split('.')
        if len(parts) >= 3 and '-' in parts[-1]:
            date_str = parts[-1]  # ex: "2024-01-15"
            try:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                formatted_date = date_obj.strftime('%d%m%Y')
                
                # Reconstruire le nom : commands_15012024.log
                base_name = parts[0]  # "commands"
                return f"{base_name}_{formatted_date}.log"
            except ValueError:
                pass
        
        # Fallback si parsing échoue
        return default_name
    
    def log_command_usage(self, 
                         interaction: discord.Interaction, 
                         command_name: str, 
                         success: bool = True,
                         error_msg: Optional[str] = None):
        """
        Log l'utilisation d'une commande.
        """
        try:
            # Informations utilisateur
            user_info = f"{interaction.user.display_name} ({interaction.user.id})"
            
            # Informations serveur
            if interaction.guild:
                guild_info = f"{interaction.guild.name} ({interaction.guild.id})"
            else:
                guild_info = "DM"
            
            # Informations canal
            if hasattr(interaction.channel, 'name'):
                channel_info = f"#{interaction.channel.name}"
            else:
                channel_info = str(interaction.channel)
            
            # Statut
            status = "SUCCESS" if success else "ERROR"
            
            # Message de log principal
            log_message = (
                f"{status} | /{command_name} | "
                f"User: {user_info} | "
                f"Guild: {guild_info} | "
                f"Channel: {channel_info}"
            )
            
            # Ajouter l'erreur si présente
            if error_msg:
                log_message += f" | Error: {error_msg}"
            
            # Logger selon le niveau
            if success:
                self.command_logger.info(log_message)
            else:
                self.command_logger.error(log_message)
                
        except Exception as e:
            # Ne pas faire échouer le bot si le logging échoue
            print(f"Erreur lors du logging de commande : {e}")


# Instance globale
daily_logger: Optional[DailyFileLogger] = None


def init_daily_logger(logs_dir: str = "/app/logs") -> DailyFileLogger:
    """Initialise le logger quotidien."""
    global daily_logger
    daily_logger = DailyFileLogger(logs_dir)
    print(f"✓ Système de logs quotidiens initialisé dans {logs_dir}")
    return daily_logger


def get_daily_logger() -> Optional[DailyFileLogger]:
    """Récupère l'instance du logger quotidien."""
    return daily_logger