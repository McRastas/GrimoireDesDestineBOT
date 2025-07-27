"""
Commande Discord : /stats-logs (ADMIN SEULEMENT)

DESCRIPTION:
    Affiche les statistiques d'utilisation des logs quotidiens
    VISIBLE UNIQUEMENT pour les membres avec le rôle admin configuré

FONCTIONNEMENT:
    - Commande invisible pour les utilisateurs normaux
    - Visible seulement pour les Façonneurs (ou rôle admin configuré)
    - Lit les fichiers de logs du jour et affiche les statistiques
    - Montre les commandes les plus utilisées, les erreurs, etc.

UTILISATION:
    /stats-logs (Façonneurs seulement)
"""

import discord
from discord import app_commands
from datetime import datetime
import os
from .base import BaseCommand
from utils.permissions import has_admin_role
from utils.file_logger import get_daily_logger
from config import Config


class StatsLogsCommand(BaseCommand):

    @property
    def name(self) -> str:
        return "stats-logs"

    @property
    def description(self) -> str:
        return "Affiche les statistiques des logs quotidiens (Façonneurs seulement)"

    def register(self, tree: app_commands.CommandTree):
        """Enregistrement avec restriction de permissions."""

        @tree.command(name=self.name, description=self.description)
        # RESTRICTION : Commande visible seulement pour les admin
        @app_commands.check(self._is_admin)
        async def stats_logs_command(interaction: discord.Interaction):
            await self.callback(interaction)

        # Gérer l'erreur de permission
        @stats_logs_command.error
        async def stats_logs_error(interaction: discord.Interaction,
                                   error: app_commands.AppCommandError):
            if isinstance(error, app_commands.CheckFailure):
                await interaction.response.send_message(
                    f"❌ Cette commande est réservée aux membres avec le rôle `{Config.ADMIN_ROLE_NAME}`.",
                    ephemeral=True)

    async def _is_admin(self, interaction: discord.Interaction) -> bool:
        """Vérifie si l'utilisateur a les permissions admin."""
        return has_admin_role(interaction.user)

    async def callback(self, interaction: discord.Interaction):
        # Double vérification des permissions (sécurité)
        if not has_admin_role(interaction.user):
            await interaction.response.send_message(
                f"❌ Accès refusé. Rôle `{Config.ADMIN_ROLE_NAME}` requis.",
                ephemeral=True)
            return

        daily_logger = get_daily_logger()
        if not daily_logger:
            await interaction.response.send_message(
                "❌ Système de logs quotidiens non initialisé.", 
                ephemeral=True)
            return

        # Defer car peut prendre un moment à analyser les logs
        await interaction.response.defer(ephemeral=True)
        
        # Analyser les logs du jour
        stats = self._analyze_today_logs(daily_logger)
        today_str = datetime.now().strftime('%d/%m/%Y')
        
        embed = discord.Embed(
            title="📊 Statistiques des Logs Quotidiens",
            description=f"**Activité du {today_str}**\n*Données extraites des fichiers de logs*",
            color=0x3498db,
            timestamp=discord.utils.utcnow()
        )

        # === COMMANDES ===
        if stats['total_commands'] > 0:
            success_rate = (stats['successful_commands'] / stats['total_commands']) * 100
            
            commands_text = (
                f"**Total :** {stats['total_commands']}\n"
                f"**✅ Réussies :** {stats['successful_commands']}\n"
                f"**❌ Échouées :** {stats['failed_commands']}\n"
                f"**📊 Taux de succès :** {success_rate:.1f}%"
            )
            
            # Couleur selon le taux de succès
            if success_rate >= 95:
                status_emoji = "🟢"
            elif success_rate >= 85:
                status_emoji = "🟡"
            else:
                status_emoji = "🔴"
                
            embed.add_field(
                name=f"{status_emoji} Commandes Exécutées",
                value=commands_text,
                inline=True
            )
        else:
            embed.add_field(
                name="📝 Commandes Exécutées",
                value="*Aucune commande enregistrée aujourd'hui*",
                inline=True
            )

        # === UTILISATEURS ===
        users_text = f"**👥 Utilisateurs uniques :** {stats['unique_users']}"
        embed.add_field(
            name="👤 Activité Utilisateurs",
            value=users_text,
            inline=True
        )

        # === TOP COMMANDES ===
        if stats['most_used_commands']:
            top_commands = sorted(
                stats['most_used_commands'].items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:8]  # Top 8
            
            commands_list = []
            for i, (cmd, count) in enumerate(top_commands, 1):
                emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "▫️"
                commands_list.append(f"{emoji} **{cmd}** : {count}")
            
            embed.add_field(
                name="🏆 Commandes Populaires",
                value="\n".join(commands_list),
                inline=False
            )

        # === SANTÉ SYSTÈME ===
        if stats['total_commands'] > 0:
            if stats['failed_commands'] == 0:
                health_status = "🟢 Excellent"
                health_desc = "Aucune erreur détectée"
            elif stats['failed_commands'] <= 2:
                health_status = "🟡 Bon"
                health_desc = f"{stats['failed_commands']} erreur(s) mineure(s)"
            else:
                health_status = "🔴 Attention"
                health_desc = f"{stats['failed_commands']} erreurs détectées"
        else:
            health_status = "⚪ Inactif"
            health_desc = "Aucune activité"

        embed.add_field(
            name="🏥 Santé du Système",
            value=f"{health_status}\n{health_desc}",
            inline=True
        )

        # === INFORMATIONS FICHIER ===
        log_file_info = self._get_log_file_info(daily_logger)
        embed.add_field(
            name="📁 Fichier de Logs",
            value=log_file_info,
            inline=True
        )

        embed.set_footer(
            text=f"Consulté par {interaction.user.display_name} • {Config.ADMIN_ROLE_NAME}"
        )

        await interaction.followup.send(embed=embed)

    def _analyze_today_logs(self, daily_logger) -> dict:
        """Analyse les logs du jour actuel."""
        today = datetime.now().strftime('%d%m%Y')
        command_file = os.path.join(daily_logger.logs_dir, f"logs-{today}.log")  # MODIFIÉ
        
        stats = {
            'total_commands': 0,
            'successful_commands': 0,
            'failed_commands': 0,
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
                                
                                # Extraire nom de commande
                                if command_part.startswith('/'):
                                    cmd_name = command_part.split()[0][1:]  # Enlever le /
                                    stats['most_used_commands'][cmd_name] = stats['most_used_commands'].get(cmd_name, 0) + 1
                                
                                # Extraire utilisateur (format approximatif)
                                if 'User:' in line:
                                    user_part = line.split('User:')[1].split('|')[0].strip()
                                    stats['unique_users'].add(user_part)
        
        except Exception as e:
            print(f"Erreur lecture stats : {e}")
        
        # Convertir set en nombre
        stats['unique_users'] = len(stats['unique_users'])
        
        return stats

    def _get_log_file_info(self, daily_logger) -> str:
        """Récupère les informations sur le fichier de logs du jour."""
        today = datetime.now().strftime('%d%m%Y')
        command_file = os.path.join(daily_logger.logs_dir, f"logs-{today}.log")  # MODIFIÉ
        
        try:
            if os.path.exists(command_file):
                size = os.path.getsize(command_file)
                if size < 1024:
                    size_str = f"{size} bytes"
                elif size < 1024*1024:
                    size_str = f"{size//1024} KB"
                else:
                    size_str = f"{size//(1024*1024)} MB"
                
                return f"**Fichier :** logs-{today}.log\n**Taille :** {size_str}"  # MODIFIÉ
            else:
                return f"**Fichier :** logs-{today}.log\n**Statut :** Non créé"  # MODIFIÉ
        except Exception as e:
            return f"**Erreur :** {str(e)}"