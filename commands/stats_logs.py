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

VERSION CORRIGÉE - Utilise les bonnes références de fichiers et améliore l'affichage.
"""

import discord
from discord import app_commands
from datetime import datetime
import os
from .base import BaseCommand
from utils.permissions import has_admin_role
from utils.file_logger import get_daily_logger
from utils.discord_logger import get_discord_logger
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
        discord_logger = get_discord_logger()
        
        if not daily_logger:
            await interaction.response.send_message(
                "❌ Système de logs quotidiens non initialisé.", 
                ephemeral=True)
            return

        # Defer car peut prendre un moment à analyser les logs
        await interaction.response.defer(ephemeral=True)
        
        # CORRECTION : Analyser les logs du jour avec la bonne méthode
        stats = daily_logger.get_today_stats()
        file_info = daily_logger.get_file_info()  # NOUVEAU : Utilise la méthode du logger
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
        
        # NOUVEAU : Actions admin séparées
        if stats['admin_actions'] > 0:
            users_text += f"\n**🔧 Actions admin :** {stats['admin_actions']}"
            
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
                
                # CORRECTION : Affichage différent pour les actions admin
                if cmd.startswith('ADMIN_'):
                    display_name = f"🔧 {cmd[6:]}"  # Enlever "ADMIN_"
                else:
                    display_name = f"/{cmd}"
                    
                commands_list.append(f"{emoji} **{display_name}** : {count}")
            
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
        # CORRECTION : Utilise les informations du logger corrigé
        file_text = f"**Fichier :** {file_info['filename']}\n**Taille :** {file_info['size_str']}"
        
        if not file_info['exists']:
            file_text += "\n⚠️ *Fichier non encore créé*"
            
        embed.add_field(
            name="📁 Fichier de Logs",
            value=file_text,
            inline=True
        )

        # === STATUT DISCORD LOGGER ===
        # NOUVEAU : Affiche le statut du Discord Logger
        if discord_logger:
            discord_status = discord_logger.get_status()
            
            if discord_status['in_cooldown']:
                discord_text = "⏸️ **En cooldown**\n"
                discord_text += f"Erreurs: {discord_status['error_count']}/{discord_status['max_errors']}"
            elif discord_status['ready']:
                discord_text = "✅ **Opérationnel**\n"
                discord_text += f"Cache: {discord_status['cache_size']} entrées"
            else:
                discord_text = "⚠️ **En attente**\n"
                discord_text += f"Cache: {discord_status['cache_size']} logs en attente"
                
            embed.add_field(
                name="📢 Discord Logger",
                value=discord_text,
                inline=True
            )

        # === ACTIONS RECOMMANDÉES ===
        recommendations = []
        
        if stats['total_commands'] == 0:
            recommendations.append("ℹ️ Aucune activité détectée aujourd'hui")
        elif stats['failed_commands'] > 5:
            recommendations.append("⚠️ Taux d'erreurs élevé - vérifier les logs")
        elif success_rate < 90:
            recommendations.append("🔍 Analyser les causes des échecs de commandes")
            
        if discord_logger and discord_logger.get_status()['in_cooldown']:
            recommendations.append("🔧 Discord Logger en cooldown - vérifier la configuration")
            
        if not file_info['exists']:
            recommendations.append("📝 Fichier de logs non créé - première utilisation")

        if recommendations:
            embed.add_field(
                name="💡 Recommandations",
                value="\n".join(recommendations),
                inline=False
            )

        # === COMMANDES UTILES ===
        embed.add_field(
            name="🛠️ Commandes Utiles",
            value=(
                "• `/test-logs` - Tester le système de logs\n"
                "• `/config-channels action:test` - Vérifier la config\n"
                "• `!debug_bot` - Informations de débogage"
            ),
            inline=False
        )

        embed.set_footer(
            text=f"Consulté par {interaction.user.display_name} • {Config.ADMIN_ROLE_NAME} • Fichier: {file_info['filename']}"
        )

        await interaction.followup.send(embed=embed)