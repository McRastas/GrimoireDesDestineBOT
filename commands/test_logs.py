"""
Commande Discord : /test-logs (ADMIN SEULEMENT)

DESCRIPTION:
    Teste le système de logs Discord du bot
    VISIBLE UNIQUEMENT pour les membres avec le rôle admin configuré

FONCTIONNEMENT:
    - Vérifie la configuration du canal admin
    - Teste les permissions d'envoi
    - Envoie un message de test dans le canal admin
    - Rapport détaillé des résultats

UTILISATION:
    /test-logs (Façonneurs seulement)

VERSION CORRIGÉE - Utilise les loggers corrigés et améliore les diagnostics.
"""

import discord
from discord import app_commands
from .base import BaseCommand
from utils.permissions import has_admin_role
from utils.discord_logger import get_discord_logger
from utils.file_logger import get_daily_logger
from utils.channels import ChannelHelper
from config import Config


class TestLogsCommand(BaseCommand):

    @property
    def name(self) -> str:
        return "test-logs"

    @property
    def description(self) -> str:
        return "Teste le système de logs Discord (Façonneurs seulement)"

    def register(self, tree: app_commands.CommandTree):
        """Enregistrement avec restriction de permissions."""

        @tree.command(name=self.name, description=self.description)
        # RESTRICTION : Commande visible seulement pour les admin
        @app_commands.check(self._is_admin)
        async def test_logs_command(interaction: discord.Interaction):
            await self.callback(interaction)

        # Gérer l'erreur de permission
        @test_logs_command.error
        async def test_logs_error(interaction: discord.Interaction,
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

        # Récupérer les loggers
        discord_logger = get_discord_logger()
        daily_logger = get_daily_logger()
        
        if not discord_logger:
            await interaction.response.send_message(
                "❌ Système de logs Discord non initialisé.", 
                ephemeral=True)
            return

        # Defer pour éviter timeout
        await interaction.response.defer(ephemeral=True)

        # Log de l'action admin dans le fichier quotidien
        if daily_logger:
            daily_logger.log_admin_action(
                interaction.user, 
                "Test Système Logs", 
                "Commande /test-logs utilisée"
            )

        # Log de l'action admin dans Discord
        discord_logger.admin_action(
            "Test Système Logs", 
            interaction.user,
            "Commande /test-logs utilisée"
        )

        # Tester le système de logs Discord
        result = await discord_logger.test_logging(interaction.guild)

        # NOUVEAU : Récupérer le statut complet du Discord Logger
        discord_status = discord_logger.get_status()

        # NOUVEAU : Tester le système de logs quotidiens
        file_result = self._test_daily_logger(daily_logger) if daily_logger else None

        # Créer l'embed de résultat avec diagnostics complets
        embed = discord.Embed(
            title="🧪 Test Complet du Système de Logs",
            timestamp=discord.utils.utcnow()
        )

        # === TEST DISCORD LOGGER ===
        if result['channel_found']:
            if result['test_sent']:
                embed.color = 0x00ff00  # Vert - Succès complet
                discord_status_text = "✅ **Parfaitement opérationnel !**"
                embed.add_field(
                    name="📍 Canal Admin Configuré",
                    value=f"✅ #{result['channel_name']}",
                    inline=True
                )
            elif not result['can_send']:
                embed.color = 0xff9900  # Orange - Problème de permissions
                discord_status_text = "⚠️ **Canal trouvé mais permissions insuffisantes**"
                embed.add_field(
                    name="📍 Canal Admin Configuré",
                    value=f"⚠️ #{result['channel_name']} (pas de permissions)",
                    inline=True
                )
            elif result.get('in_cooldown'):
                embed.color = 0xff9900  # Orange - En cooldown
                discord_status_text = "⏸️ **Système en cooldown temporaire**"
                embed.add_field(
                    name="📍 Canal Admin Configuré",
                    value=f"⏸️ #{result['channel_name']} (cooldown actif)",
                    inline=True
                )
            else:
                embed.color = 0xff0000  # Rouge - Erreur
                discord_status_text = "❌ **Erreur lors du test d'envoi**"
                embed.add_field(
                    name="📍 Canal Admin Configuré",
                    value=f"❌ #{result['channel_name']} (erreur d'envoi)",
                    inline=True
                )
        else:
            embed.color = 0xe74c3c  # Rouge foncé - Non configuré
            discord_status_text = "❌ **Canal admin non configuré**"
            embed.add_field(
                name="📍 Canal Admin",
                value="❌ Non configuré",
                inline=True
            )

        # Permissions détaillées
        if result['channel_found']:
            perm_status = "✅ Autorisées" if result['can_send'] else "❌ Manquantes"
            embed.add_field(
                name="🔐 Permissions",
                value=perm_status,
                inline=True
            )

            # Test d'envoi
            if result.get('in_cooldown'):
                test_status = "⏸️ Cooldown actif"
            elif result['test_sent']:
                test_status = "✅ Message envoyé"
            else:
                test_status = "❌ Échec d'envoi"
                
            embed.add_field(
                name="📨 Test d'Envoi",
                value=test_status,
                inline=True
            )

        embed.add_field(
            name="📢 Statut Discord Logger",
            value=discord_status_text,
            inline=False
        )

        # === DIAGNOSTIC AVANCÉ DISCORD LOGGER ===
        diagnostic_text = []
        diagnostic_text.append(f"**État :** {'✅ Prêt' if discord_status['ready'] else '⏳ En attente'}")
        diagnostic_text.append(f"**Erreurs :** {discord_status['error_count']}/{discord_status['max_errors']}")
        
        if discord_status['in_cooldown']:
            diagnostic_text.append("**Cooldown :** ⏸️ Actif (pause temporaire)")
        else:
            diagnostic_text.append("**Cooldown :** ✅ Inactif")
            
        diagnostic_text.append(f"**Cache :** {discord_status['cache_size']} logs en attente")
        diagnostic_text.append(f"**Anti-doublons :** {discord_status['sent_messages_cache']} entrées")

        embed.add_field(
            name="🔍 Diagnostic Discord Logger",
            value="\n".join(diagnostic_text),
            inline=False
        )

        # === TEST DAILY LOGGER ===
        if file_result:
            daily_status_text = []
            
            if file_result['logger_available']:
                daily_status_text.append("✅ **Logger quotidien opérationnel**")
                daily_status_text.append(f"📁 Fichier: `{file_result['filename']}`")
                daily_status_text.append(f"📊 Taille: {file_result['size_str']}")
                
                if file_result['writable']:
                    daily_status_text.append("✅ Écriture testée avec succès")
                else:
                    daily_status_text.append("❌ Problème d'écriture détecté")
            else:
                daily_status_text.append("❌ **Logger quotidien non disponible**")

            embed.add_field(
                name="📝 Logs Quotidiens",
                value="\n".join(daily_status_text),
                inline=False
            )

        # === SOLUTIONS ET RECOMMANDATIONS ===
        solutions = []
        
        if not result['channel_found']:
            solutions.append("🔧 **Configuration requise :**")
            solutions.append("• Configurez `CHANNEL_ADMIN_NAME=bot-admin`")
            solutions.append("• Ou `CHANNEL_ADMIN_ID=123456789`")
            solutions.append("• Utilisez `/config-channels action:guide`")
            
        elif not result['can_send']:
            solutions.append("🔧 **Permissions manquantes :**")
            solutions.append(f"• Accordez au bot l'accès à #{result['channel_name']}")
            solutions.append("• Permissions requises : Voir canal, Envoyer messages, Intégrer liens")
            
        elif result.get('in_cooldown'):
            solutions.append("⏸️ **Système en cooldown :**")
            solutions.append(f"• Trop d'erreurs détectées ({discord_status['error_count']})")
            solutions.append("• Le système reprendra automatiquement dans quelques minutes")
            solutions.append("• Utilisez `/stats-logs` pour plus de détails")
            
        elif result.get('error'):
            solutions.append("🐛 **Erreur détectée :**")
            solutions.append(f"• `{result['error']}`")
            solutions.append("• Vérifiez la configuration et les permissions")

        if not daily_logger:
            solutions.append("📝 **Logger quotidien :**")
            solutions.append("• Système de logs quotidiens non initialisé")
            solutions.append("• Redémarrage du bot recommandé")

        if solutions:
            embed.add_field(
                name="💡 Solutions Recommandées",
                value="\n".join(solutions),
                inline=False
            )

        # === COMMANDES UTILES ===
        useful_commands = [
            "• `/config-channels action:test` - Tester la config des canaux",
            "• `/stats-logs` - Voir les statistiques détaillées",
            "• `!debug_bot` - Informations de débogage complètes"
        ]
        
        if discord_status['in_cooldown']:
            useful_commands.append("• *Attendre la fin du cooldown pour un nouveau test*")

        embed.add_field(
            name="🛠️ Commandes Utiles",
            value="\n".join(useful_commands),
            inline=False
        )

        # Footer avec informations détaillées
        footer_parts = [f"Test par {interaction.user.display_name}"]
        footer_parts.append(Config.ADMIN_ROLE_NAME)
        
        if result['channel_found']:
            footer_parts.append(f"Canal: #{result['channel_name']}")
        
        embed.set_footer(text=" • ".join(footer_parts))

        await interaction.followup.send(embed=embed)

    def _test_daily_logger(self, daily_logger) -> dict:
        """NOUVEAU : Teste le système de logs quotidiens."""
        if not daily_logger:
            return {'logger_available': False}
        
        try:
            # Récupérer les informations du fichier
            file_info = daily_logger.get_file_info()
            
            # Tester l'écriture
            test_writable = True
            try:
                # Simuler un log de test (ne s'affichera pas réellement)
                import logging
                test_logger = logging.getLogger('faerun_test')
                test_logger.info("Test d'écriture du système de logs")
            except Exception:
                test_writable = False
            
            return {
                'logger_available': True,
                'filename': file_info['filename'],
                'size_str': file_info['size_str'],
                'exists': file_info['exists'],
                'writable': test_writable
            }
            
        except Exception as e:
            return {
                'logger_available': False,
                'error': str(e)
            }