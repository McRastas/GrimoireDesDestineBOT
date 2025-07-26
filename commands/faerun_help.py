"""
Commande Discord : /help

DESCRIPTION:
    Guide complet d'utilisation de toutes les commandes du Bot Faerûn

FONCTIONNEMENT:
    - Affiche un embed avec toutes les catégories de commandes
    - Explique chaque commande avec sa syntaxe et ses exemples
    - Inclut les permissions requises pour les commandes admin
    - Guide d'utilisation pour les MJ et joueurs

UTILISATION:
    /help
"""

import discord
from .base import BaseCommand
from config import Config


class HelpCommand(BaseCommand):

    @property
    def name(self) -> str:
        return "help"

    @property
    def description(self) -> str:
        return "Guide complet de toutes les commandes du bot"

    async def callback(self, interaction: discord.Interaction):
        # Embed principal
        embed = discord.Embed(
            title="🤖 Guide Complet du Bot Faerûn",
            description=(
                "**Bot Discord spécialisé pour les campagnes D&D dans les Royaumes Oubliés**\n\n"
                "Ce bot vous aide à gérer le calendrier Faerûnien, suivre les mentions de joueurs, "
                "planifier vos quêtes et générer des PNJ pour vos sessions de jeu de rôle."
            ),
            color=0x8B4513
        )

        # ===== SECTION 1: CALENDRIER FAERÛN =====
        calendrier_text = (
            "📅 **`/faerun`** - Date Faerûnienne actuelle\n"
            "📊 **`/faeruncomplet`** - Infos détaillées (saison, semaine, année DR)\n"
            "🎊 **`/faerunfestival`** - Prochain festival de Faerûn\n"
            "🔄 **`/faerunjdr [date]`** - Convertit une date (format JJ-MM-AAAA)\n"
            "   *Exemple : `/faerunjdr 25-12-2024`*"
        )
        embed.add_field(
            name="📅 Calendrier de Faerûn", 
            value=calendrier_text, 
            inline=False
        )

        # ===== SECTION 2: GESTION DES QUÊTES =====
        quetes_text = (
            "🎯 **`/mesquetes [membre]`** - Liste les quêtes futures d'un joueur\n"
            "   • Détecte automatiquement les dates dans vos messages\n"
            "   • Supporte : `28/06`, `28-06-2025`, `28 juin`, `le 28/06 à 14h30`\n"
            "   • Classe par urgence : aujourd'hui, demain, cette semaine, plus tard\n"
            "   *Exemple : `/mesquetes @Aventurier`*"
        )
        embed.add_field(
            name="🎯 Gestion des Quêtes", 
            value=quetes_text, 
            inline=False
        )

        # ===== SECTION 3: MENTIONS ET RÉCOMPENSES =====
        mentions_text = (
            "📢 **`/mentionsomeone [membre]`** - Mentions d'un joueur dans #récompenses (30 jours)\n"
            "   • Affiche les liens vers les messages originaux\n"
            "   • Compte total et détails par message\n\n"
            "📊 **`/mentionlist`** - Classement des mentions pour tous les actifs du canal\n"
            "   • Statistiques globales de participation\n\n"
            "📋 **`/recapmj [membre]`** - Messages où un MJ mentionne 2+ personnes\n"
            "   • Parfait pour suivre les récompenses de groupe\n"
            "   *Exemples : `/mentionsomeone @Joueur`, `/mentionlist`*"
        )
        embed.add_field(
            name="📊 Mentions et Récompenses", 
            value=mentions_text, 
            inline=False
        )

        # ===== SECTION 4: GÉNÉRATEUR DE CONTENU =====
        generateur_text = (
            "🎭 **`/pnj-generator [type] [genre] [race]`** - Génère un PNJ aléatoire\n"
            "   • **Types :** Marchand, Noble, Garde, Aubergiste, Prêtre, Voleur, Artisan, Paysan, Aventurier, Mage\n"
            "   • **Genres :** Masculin, Féminin, Aléatoire\n"
            "   • **Races :** Humain, Elfe, Nain, Halfelin, Demi-Elfe, Tieffelin, Aléatoire\n"
            "   • Inclut : apparence, personnalité, profession, secret RP\n"
            "   *Exemple : `/pnj-generator type:marchand genre:féminin race:elfe`*"
        )
        embed.add_field(
            name="🎭 Générateur de Contenu", 
            value=generateur_text, 
            inline=False
        )

        # ===== SECTION 5: COMMANDES UTILITAIRES =====
        utilitaires_text = (
            "⚙️ **`/test`** - Test de fonctionnement du bot\n"
            "ℹ️ **`/info`** - Statistiques du bot (serveurs, utilisateurs, commandes)\n"
            "❓ **`/help`** - Ce guide d'utilisation"
        )
        embed.add_field(
            name="⚙️ Utilitaires", 
            value=utilitaires_text, 
            inline=False
        )

        # ===== SECTION 6: COMMANDES ADMIN =====
        admin_text = (
            f"🔧 **`/config-channels`** - Configuration des canaux du bot ({Config.ADMIN_ROLE_NAME} seulement)\n"
            "   • Voir, tester et configurer les canaux\n"
            "   • Suggestions automatiques basées sur les canaux existants\n\n"
            f"**Commandes textuelles admin** (rôle {Config.ADMIN_ROLE_NAME} requis) :\n"
            "• **`!sync_bot`** - Synchronise les commandes slash\n"
            "• **`!debug_bot`** - Informations de débogage\n"
            "• **`!reload_commands`** - Recharge les commandes à chaud"
        )
        embed.add_field(
            name="🔐 Administration", 
            value=admin_text, 
            inline=False
        )

        # ===== SECTION 7: CONFIGURATION DES CANAUX =====
        config_text = (
            "**Le bot fonctionne mieux avec des canaux spécialisés :**\n"
            "• **#récompenses** - Pour `/mentionsomeone` et `/mentionlist`\n"
            "• **#départ-à-l-aventure** - Pour `/mesquetes` (détection des quêtes)\n"
            "• **#bot-logs** - Logs système du bot\n"
            "• **#bot-admin** - Canal d'administration\n\n"
            f"Utilisez `/config-channels` (rôle {Config.ADMIN_ROLE_NAME}) pour configurer ces canaux."
        )
        embed.add_field(
            name="⚙️ Configuration Recommandée", 
            value=config_text, 
            inline=False
        )

        # ===== SECTION 8: CONSEILS D'UTILISATION =====
        conseils_text = (
            "🎲 **Pour les MJ :**\n"
            "• Utilisez le calendrier Faerûn pour l'immersion\n"
            "• Planifiez vos événements selon les festivals\n"
            "• Générez des PNJ rapidement avec `/pnj-generator`\n"
            "• Suivez les récompenses avec `/recapmj`\n\n"
            "👥 **Pour les Joueurs :**\n"
            "• Consultez vos quêtes avec `/mesquetes`\n"
            "• Vérifiez vos mentions avec `/mentionsomeone`\n"
            "• Convertissez les dates importantes avec `/faerunjdr`"
        )
        embed.add_field(
            name="💡 Conseils d'Utilisation", 
            value=conseils_text, 
            inline=False
        )

        # ===== SECTION 9: FORMATS DE DATES SUPPORTÉS =====
        dates_text = (
            "**Pour `/faerunjdr` :** JJ-MM-AAAA uniquement\n"
            "   *Exemple : `15-02-2023`*\n\n"
            "**Pour `/mesquetes` (détection automatique) :**\n"
            "• `28/06`, `28-06`, `28.06` (année automatique)\n"
            "• `28/06/2025`, `28-06-2025` (année explicite)\n"
            "• `28 juin`, `28 june 2025` (formats textuels)\n"
            "• `le 28/06`, `28/06 à 14h30` (formats naturels)"
        )
        embed.add_field(
            name="📅 Formats de Dates", 
            value=dates_text, 
            inline=False
        )

        # Footer et timestamp
        embed.set_footer(
            text=f"🏰 Bot Faerûn v1.0 • {len(self.bot.guilds)} serveurs • {len(self.bot.tree.get_commands())} commandes"
        )
        embed.timestamp = discord.utils.utcnow()

        await interaction.response.send_message(embed=embed, ephemeral=True)
