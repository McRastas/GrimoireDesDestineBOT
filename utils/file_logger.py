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
                filename=os.path.join(self.logs_dir, "logs.log"),  # MODIFIÉ
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
        Génère le nom de fichier au format logs-DDMMYYYY.log
        """
        # Extraire la date du nom par défaut
        # Format par défaut : logs.log.2024-01-15
        parts = default_name.split('.')
        if len(parts) >= 3 and '-' in parts[-1]:
            date_str = parts[-1]  # ex: "2024-01-15"
            try:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                formatted_date = date_obj.strftime('%d%m%Y')
                
                # Reconstruire le nom : logs-15012024.log
                return f"logs-{formatted_date}.log"
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

    def log_admin_action(self, 
                        user: discord.Member, 
                        action: str, 
                        details: str = ""):
        """
        Log une action d'administration.
        """
        try:
            admin_message = (
                f"ADMIN | {action} | "
                f"User: {user.display_name} ({user.id}) | "
                f"Guild: {user.guild.name} ({user.guild.id})"
            )
            
            if details:
                admin_message += f" | Details: {details}"
            
            # Les actions admin sont loggées en WARNING pour les distinguer
            self.command_logger.warning(admin_message)
            
        except Exception as e:
            print(f"Erreur lors du logging d'action admin : {e}")

    def get_today_stats(self) -> dict:
        """
        Retourne les statistiques du jour actuel.
        """
        today = datetime.now().strftime('%d%m%Y')
        command_file = os.path.join(self.logs_dir, f"logs-{today}.log")  # MODIFIÉ
        
        stats = {
            'total_commands': 0,
            'successful_commands': 0,
            'failed_commands': 0,
            'admin_actions': 0,
            'unique_users': set(),
            'most_used_commands': {}
        }
        
        try:
            if os.path.exists(command_file):
                with open(command_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if '|' in line:
                            parts = line.split('|')
                            if len(parts) >= 3:
                                status = parts[1].strip()
                                command_part = parts[2].strip()
                                
                                stats['total_commands'] += 1
                                
                                if status == 'SUCCESS':
                                    stats['successful_commands'] += 1
                                elif status == 'ERROR':
                                    stats['failed_commands'] += 1
                                elif status == 'ADMIN':
                                    stats['admin_actions'] += 1
                                
                                # Extraire nom de commande
                                if command_part.startswith('/'):
                                    cmd_name = command_part.split()[0][1:]
                                    stats['most_used_commands'][cmd_name] = stats['most_used_commands'].get(cmd_name, 0) + 1
                                elif status == 'ADMIN':
                                    # Pour les actions admin, extraire l'action
                                    action_name = command_part.strip()
                                    stats['most_used_commands'][f"ADMIN_{action_name}"] = stats['most_used_commands'].get(f"ADMIN_{action_name}", 0) + 1
                                
                                # Extraire utilisateur
                                if 'User:' in line:
                                    user_part = line.split('User:')[1].split('|')[0].strip()
                                    stats['unique_users'].add(user_part)
        
        except Exception as e:
            print(f"Erreur lecture stats : {e}")
        
        # Convertir set en nombre
        stats['unique_users'] = len(stats['unique_users'])
        
        return stats

    def cleanup_old_logs(self, days_to_keep: int = 30):
        """
        Nettoie les anciens fichiers de logs.
        """
        try:
            import glob
            from datetime import timedelta
            
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            
            # Chercher tous les fichiers de logs avec pattern
            pattern = os.path.join(self.logs_dir, "logs-????????.log")  # MODIFIÉ
            old_files = glob.glob(pattern)
            
            deleted_count = 0
            for file_path in old_files:
                try:
                    # Extraire la date du nom de fichier
                    filename = os.path.basename(file_path)
                    date_part = filename.replace('logs-', '').replace('.log', '')  # MODIFIÉ
                    file_date = datetime.strptime(date_part, '%d%m%Y')
                    
                    if file_date < cutoff_date:
                        os.remove(file_path)
                        deleted_count += 1
                        print(f"✓ Supprimé: {filename}")
                        
                except (ValueError, IndexError):
                    continue
            
            if deleted_count > 0:
                print(f"✓ Nettoyage terminé: {deleted_count} anciens fichiers supprimés")
            else:
                print("✓ Aucun fichier à nettoyer")
                
        except Exception as e:
            print(f"⚠️ Erreur lors du nettoyage des logs: {e}")


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