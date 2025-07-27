"""
Système de logs quotidiens pour le Bot Faerûn.

Ce module génère des fichiers de logs quotidiens au format DDMMYYYY
pour tracer l'utilisation des commandes et les événements du bot.

VERSION CORRIGÉE - Résout les problèmes de nommage des fichiers.
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
    
    def _get_today_filename(self) -> str:
        """
        Génère le nom de fichier pour aujourd'hui.
        CORRECTION PRINCIPALE : Format cohérent logs-DDMMYYYY.log
        """
        today = datetime.now().strftime('%d%m%Y')
        return os.path.join(self.logs_dir, f"logs-{today}.log")
    
    def _setup_loggers(self):
        """Configure les loggers avec rotation quotidienne."""
        
        # LOGGER COMMANDES
        self.command_logger = logging.getLogger('faerun_commands')
        self.command_logger.setLevel(logging.INFO)
        
        # Éviter la duplication si déjà configuré
        if not self.command_logger.handlers:
            # CORRECTION : Utiliser directement le nom de fichier cohérent
            today_filename = self._get_today_filename()
            
            # Handler avec rotation quotidienne
            command_handler = TimedRotatingFileHandler(
                filename=today_filename,
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
            
            # CORRECTION : Fonction de nommage cohérente
            command_handler.namer = self._get_rotated_filename
            
            self.command_logger.addHandler(command_handler)
            print(f"✓ Logger configuré avec fichier : {today_filename}")
    
    def _get_rotated_filename(self, default_name: str) -> str:
        """
        Génère le nom de fichier au format logs-DDMMYYYY.log
        CORRECTION : Gestion cohérente de la rotation
        """
        try:
            # Extraire la date du nom par défaut
            # Format TimedRotatingFileHandler : /path/logs-DDMMYYYY.log.2024-01-15
            if '.log.' in default_name:
                # Séparer le chemin et la date
                base_path, date_suffix = default_name.rsplit('.log.', 1)
                
                # Parser la date (format ISO : YYYY-MM-DD)
                date_obj = datetime.strptime(date_suffix, '%Y-%m-%d')
                formatted_date = date_obj.strftime('%d%m%Y')
                
                # Reconstruire le nom : logs-DDMMYYYY.log
                directory = os.path.dirname(base_path)
                return os.path.join(directory, f"logs-{formatted_date}.log")
        except (ValueError, IndexError) as e:
            print(f"⚠️ Erreur parsing nom fichier log : {e}")
        
        # Fallback : garder le nom par défaut
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
                # Nettoyer le message d'erreur pour éviter les injections
                clean_error = str(error_msg).replace('\n', ' ').replace('\r', '')[:200]
                log_message += f" | Error: {clean_error}"
            
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
                # Nettoyer les détails
                clean_details = str(details).replace('\n', ' ').replace('\r', '')[:300]
                admin_message += f" | Details: {clean_details}"
            
            # Les actions admin sont loggées en WARNING pour les distinguer
            self.command_logger.warning(admin_message)
            
        except Exception as e:
            print(f"Erreur lors du logging d'action admin : {e}")

    def get_today_stats(self) -> dict:
        """
        Retourne les statistiques du jour actuel.
        CORRECTION : Utilise le bon nom de fichier
        """
        today_file = self._get_today_filename()  # CORRECTION : Utilise la méthode cohérente
        
        stats = {
            'total_commands': 0,
            'successful_commands': 0,
            'failed_commands': 0,
            'admin_actions': 0,
            'unique_users': set(),
            'most_used_commands': {}
        }
        
        try:
            if os.path.exists(today_file):
                with open(today_file, 'r', encoding='utf-8') as f:
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
    
    def get_file_info(self) -> dict:
        """
        Retourne les informations sur le fichier de logs du jour.
        NOUVEAU : Méthode pour récupérer les infos du fichier
        """
        today_file = self._get_today_filename()
        
        try:
            if os.path.exists(today_file):
                size = os.path.getsize(today_file)
                if size < 1024:
                    size_str = f"{size} bytes"
                elif size < 1024*1024:
                    size_str = f"{size//1024} KB"
                else:
                    size_str = f"{size//(1024*1024)} MB"
                
                return {
                    'exists': True,
                    'filename': os.path.basename(today_file),
                    'size_str': size_str,
                    'path': today_file
                }
            else:
                return {
                    'exists': False,
                    'filename': os.path.basename(today_file),
                    'size_str': 'Fichier non créé',
                    'path': today_file
                }
        except Exception as e:
            return {
                'exists': False,
                'filename': 'Erreur',
                'size_str': f'Erreur: {e}',
                'path': today_file
            }

    def cleanup_old_logs(self, days_to_keep: int = 30):
        """
        Nettoie les anciens fichiers de logs.
        CORRECTION : Pattern de recherche cohérent
        """
        try:
            import glob
            from datetime import timedelta
            
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            
            # CORRECTION : Pattern cohérent avec le nommage
            pattern = os.path.join(self.logs_dir, "logs-????????.log")
            old_files = glob.glob(pattern)
            
            deleted_count = 0
            for file_path in old_files:
                try:
                    # Extraire la date du nom de fichier
                    filename = os.path.basename(file_path)
                    if filename.startswith('logs-') and filename.endswith('.log'):
                        date_part = filename[5:-4]  # Enlever "logs-" et ".log"
                        if len(date_part) == 8 and date_part.isdigit():
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