"""
Commande Discord : /help

DESCRIPTION:
    Guide complet d'utilisation adaptatif selon les permissions de l'utilisateur

FONCTIONNEMENT:
    - Affiche toutes les commandes disponibles pour l'utilisateur
    - Version complète pour les admins (Façonneurs)
    - Version utilisateur standard pour les autres
    - Détecte automatiquement les permissions

UTILISATION:
    /help
"""

import discord
from .base import BaseCommand
from config import Config
from utils.permissions import has_admin_role


class HelpCommand(BaseCommand):

    @property
    def name(self) -> str:
        return "help"

    @property
    def description(self) -> str:
        return "Guide d'utilisation du bot (adapté à vos permissions)"

    async def callback(self, interaction: discord.Interaction):
        # Détecter si l'utilisateur est admin
        is_admin = has_admin_role(interaction.user)
        
        if is_admin:
            await self._send_admin_help(interaction)
        else:
            await self._send_user_help(interaction)

    async def _send_user_help(self, interaction: discord.Interaction):
        """Version d'aide pour les utilisateurs normaux."""
        
        embed = discord.Embed(
            title="🤖 Guide du Bot Faerûn",
            description=(
                "**Bot Discord pour les campagnes D&D dans les Royaumes Oubliés**\n\n"
                "Découvrez toutes les commandes disponibles pour enrichir vos sessions de jeu de rôle !"
            ),
            color=0x3498db
        )

        # ===== CALENDRIER FAERÛN =====
        calendrier_text = (
            "📅 **`/faerun`** - Date Faerûnienne actuelle\n"
            "📊 **`/faeruncomplet`** - Infos détaillées (saison, semaine, année DR)\n"
            "🎊 **`/faerunfestival`** - Prochain festival de Faerûn\n"
            "🔄 **`/faerunjdr [date]`** - Convertit une date réelle en Faerûnienne\n"
            "   *Exemple : `/faerunjdr 25-12-2024`*"
        )
        embed.add_field(
            name="📅 Calendrier de Faerûn", 
            value=calendrier_text, 
            inline=False
        )

        # ===== GESTION DES QUÊTES =====
        quetes_text = (
            "🎯 **`/mesquetes [membre]`** - Vos quêtes futures avec dates détectées\n"
            "   • Détecte automatiquement les dates dans vos messages\n"
            "   • Formats supportés : `28/06`, `28-06-2025`, `28 juin`, `le 28/06 à 14h30`\n"
            "   • Classe par urgence : aujourd'hui, demain, cette semaine, plus tard\n"
            "   *Utilisez `/mesquetes` pour voir vos quêtes ou `/mesquetes @Joueur` pour celles d'un autre*"
        )
        embed.add_field(
            name="🎯 Vos Quêtes", 
            value=quetes_text, 
            inline=False
        )

        # ===== MENTIONS ET RÉCOMPENSES =====
        mentions_text = (
            "📢 **`/mentionsomeone [membre]`** - Vos mentions dans #récompenses (30 jours)\n"
            "   • Liens vers les messages de récompenses\n"
            "   • Compte total avec détails\n\n"
            "📊 **`/mentionlist`** - Classement des mentions dans ce canal\n"
            "   • Statistiques de participation globales\n\n"
            "*Parfait pour suivre vos récompenses et reconnaissances !*"
        )
        embed.add_field(
            name="📊 Vos Récompenses", 
            value=mentions_text, 
            inline=False
        )

        # ===== GÉNÉRATEUR DE CONTENU =====
        generateur_text = (
            "🎭 **`/pnj-generator [type] [genre] [race]`** - Créez des PNJ instantanément\n"
            "   • **Types :** Marchand, Noble, Garde, Aubergiste, Prêtre, Voleur, Artisan, Paysan, Aventurier, Mage\n"
            "   • **Genres :** Masculin, Féminin, Aléatoire\n"
            "   • **Races :** Humain, Elfe, Nain, Halfelin, Demi-Elfe, Tieffelin, Aléatoire\n"
            "   • Génère : apparence, personnalité, background, secrets RP\n"
            "   *Exemple : `/pnj-generator type:marchand genre:féminin race:elfe`*"
        )
        embed.add_field(
            name="🎭 Création de PNJ", 
            value=generateur_text, 
            inline=False
        )

        # ===== UTILITAIRES =====
        utilitaires_text = (
            "⚙️ **`/test`** - Vérifier que le bot fonctionne\n"
            "ℹ️ **`/info`** - Statistiques du bot\n"
            "❓ **`/help`** - Ce guide d'utilisation"
        )
        embed.add_field(
            name="⚙️ Utilitaires", 
            value=utilitaires_text, 
            inline=False
        )

        # ===== CONSEILS D'UTILISATION =====
        conseils_text = (
            "🎲 **Immersion maximale :**\n"
            "• Utilisez `/faerun` pour connaître la date dans votre campagne\n"
            "• Consultez vos quêtes avec `/mesquetes` avant chaque session\n"
            "• Vérifiez vos récompenses avec `/mentionsomeone`\n"
            "• Générez des PNJ pour enrichir vos interactions\n\n"
            "📅 **Formats de dates pour `/mesquetes` :**\n"
            "Le bot détecte : `28/06`, `28-06-2025`, `28 juin`, `le 28/06 à 14h30`"
        )
        embed.add_field(
            name="💡 Conseils d'Utilisation", 
            value=conseils_text, 
            inline=False
        )

        # Footer utilisateur
        embed.set_footer(
            text=f"🏰 Bot Faerûn • {len(self.bot.guilds)} serveurs • Mode Joueur"
        )
        embed.timestamp = discord.utils.utcnow()

        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def _send_admin_help(self, interaction: discord.Interaction):
        """Version d'aide complète pour les administrateurs."""
        
        embed = discord.Embed(
            title="🔐 Guide Complet du Bot Faerûn (Administration)",
            description=(
                f"**Version administrative pour les {Config.ADMIN_ROLE_NAME}**\n\n"
                "Vous avez accès à toutes les commandes du bot, y compris la configuration "
                "et les outils d'administration. Ce guide couvre l'ensemble des fonctionnalités."
            ),
            color=0xe74c3c  # Rouge pour indiquer les permissions admin
        )

        # ===== CALENDRIER FAERÛN =====
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

        # ===== GESTION DES QUÊTES =====
        quetes_text = (
            "🎯 **`/mesquetes [membre]`** - Quêtes futures avec détection intelligente des dates\n"
            "   • Analyse les messages dans le canal quêtes configuré\n"
            "   • Détecte : `28/06`, `28-06-2025`, `28 juin`, `le 28/06 à 14h30`\n"
            "   • Logique d'année automatique pour les dates sans année\n"
            "   • Classification par urgence avec liens vers les messages\n"
            "   *Utilisez pour suivre les quêtes de vos joueurs*"
        )
        embed.add_field(
            name="🎯 Gestion des Quêtes", 
            value=quetes_text, 
            inline=False
        )

        # ===== MENTIONS ET RÉCOMPENSES =====
        mentions_text = (
            "📢 **`/mentionsomeone [membre]`** - Mentions d'un joueur dans #récompenses (30 jours)\n"
            "   • Liens vers les messages originaux avec aperçu\n"
            "   • Statistiques détaillées de participation\n\n"
            "📊 **`/mentionlist`** - Classement global des mentions dans le canal actuel\n"
            "   • Vue d'ensemble de la participation des joueurs\n\n"
            "📋 **`/recapmj [membre]`** - Messages multi-mentions d'un MJ\n"
            "   • Parfait pour analyser les sessions de récompenses de groupe\n"
            "   • Affiche les messages où 2+ joueurs sont mentionnés"
        )
        embed.add_field(
            name="📊 Système de Mentions", 
            value=mentions_text, 
            inline=False
        )

        # ===== GÉNÉRATEUR DE CONTENU =====
        generateur_text = (
            "🎭 **`/pnj-generator [type] [genre] [race]`** - Générateur avancé de PNJ\n"
            "   • **Types :** Marchand, Noble, Garde, Aubergiste, Prêtre, Voleur, Artisan, Paysan, Aventurier, Mage\n"
            "   • **Genres :** Masculin, Féminin, Aléatoire\n"
            "   • **Races :** Humain, Elfe, Nain, Halfelin, Demi-Elfe, Tieffelin, Aléatoire\n"
            "   • Génère : apparence détaillée, traits de personnalité, background professionnel, secrets RP\n"
            "   *Outil puissant pour créer rapidement des PNJ mémorables*"
        )
        embed.add_field(
            name="🎭 Générateur de Contenu", 
            value=generateur_text, 
            inline=False
        )

        # ===== COMMANDES ADMIN SLASH =====
        admin_slash_text = (
            f"🔧 **`/config-channels [action]`** - Configuration des canaux ({Config.ADMIN_ROLE_NAME} seulement)\n"
            "   • **Actions :** show, list, test, suggest, guide\n"
            "   • Voir, tester et configurer les canaux du bot\n"
            "   • Suggestions automatiques basées sur les canaux existants\n"
            "   • Guide complet de configuration\n"
            "   *Commande invisible pour les utilisateurs normaux*"
        )
        embed.add_field(
            name="🔐 Administration (Slash)", 
            value=admin_slash_text, 
            inline=False
        )

        # ===== COMMANDES ADMIN TEXTUELLES =====
        admin_text_commands = (
            f"**Commandes textuelles réservées aux {Config.ADMIN_ROLE_NAME} :**\n\n"
            "🔄 **`!sync_bot`** - Synchronise les commandes slash\n"
            "   • Force la mise à jour des commandes Discord\n"
            "   • Utilise l'ID de guild pour une sync rapide si configuré\n\n"
            "🔍 **`!debug_bot`** - Informations de débogage détaillées\n"
            "   • Statistiques techniques du bot\n"
            "   • Liste des commandes chargées\n"
            "   • Informations sur les permissions et rôles\n\n"
            "♻️ **`!reload_commands`** - Recharge les commandes à chaud\n"
            "   • Recharge le code sans redémarrer le bot\n"
            "   • Utile pour le développement et les mises à jour"
        )
        embed.add_field(
            name="🔨 Commandes Textuelles Admin", 
            value=admin_text_commands, 
            inline=False
        )

        # ===== CONFIGURATION SYSTÈME =====
        config_text = (
            "**Configuration recommandée des canaux :**\n"
            "• **#récompenses** - Pour les commandes de mentions\n"
            "• **#départ-à-l-aventure** - Pour la détection des quêtes\n"
            "• **#bot-logs** - Logs système du bot\n"
            "• **#bot-admin** - Canal d'administration\n\n"
            "**Variables d'environnement importantes :**\n"
            f"• `ADMIN_ROLE_NAME` - Actuellement : `{Config.ADMIN_ROLE_NAME}`\n"
            "• `CHANNELS_CONFIG` - Configuration JSON des canaux\n"
            "• `GUILD_ID` - Pour la synchronisation rapide des commandes\n\n"
            "Utilisez `/config-channels action:guide` pour le guide complet."
        )
        embed.add_field(
            name="⚙️ Configuration Système", 
            value=config_text, 
            inline=False
        )

        # ===== UTILITAIRES =====
        utilitaires_text = (
            "⚙️ **`/test`** - Test de fonctionnement du bot\n"
            "ℹ️ **`/info`** - Statistiques complètes du bot\n"
            "❓ **`/help`** - Ce guide d'utilisation adaptatif"
        )
        embed.add_field(
            name="⚙️ Utilitaires", 
            value=utilitaires_text, 
            inline=False
        )

        # ===== CONSEILS ADMIN =====
        conseils_admin_text = (
            "🎲 **Gestion de campagne :**\n"
            "• Configurez les canaux avec `/config-channels` pour optimiser le bot\n"
            "• Utilisez `/recapmj` pour analyser vos sessions de récompenses\n"
            "• Surveillez l'activité avec `/mentionlist` dans différents canaux\n\n"
            "🔧 **Maintenance :**\n"
            "• `!sync_bot` après modifications importantes\n"
            "• `!debug_bot` pour diagnostiquer les problèmes\n"
            "• `!reload_commands` pour les mises à jour sans interruption\n\n"
            "📊 **Suivi des joueurs :**\n"
            "• Analysez l'engagement avec les commandes de mentions\n"
            "• Suivez la planification des quêtes avec `/mesquetes`"
        )
        embed.add_field(
            name="💡 Conseils d'Administration", 
            value=conseils_admin_text, 
            inline=False
        )

        # Footer admin avec plus d'infos
        embed.set_footer(
            text=f"🔐 Bot Faerûn • {len(self.bot.guilds)} serveurs • {len(self.bot.tree.get_commands())} commandes • Mode {Config.ADMIN_ROLE_NAME}"
        )
        embed.timestamp = discord.utils.utcnow()

        await interaction.response.send_message(embed=embed, ephemeral=True)
