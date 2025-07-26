"""
Commande Discord : /faerun_help

DESCRIPTION:
    Guide complet d'utilisation des commandes du calendrier Faerûn

FONCTIONNEMENT:
    - Affiche un embed détaillé avec toutes les commandes Faerûn disponibles
    - Explique le fonctionnement du calendrier de Harptos
    - Donne des exemples d'utilisation pratiques
    - Présente les festivals et saisons de Faerûn

UTILISATION:
    /faerun_help
"""

import discord
from .base import BaseCommand


class FaerunHelpCommand(BaseCommand):

    @property
    def name(self) -> str:
        return "faerun_help"

    @property
    def description(self) -> str:
        return "Guide complet des commandes du calendrier Faerûn"

    async def callback(self, interaction: discord.Interaction):
        # Embed principal avec introduction
        embed = discord.Embed(
            title="🏰 Guide du Calendrier Faerûn",
            description=(
                "**Bienvenue dans l'univers temporel des Royaumes Oubliés !**\n\n"
                "Le calendrier de Harptos est le système de datation officiel de Faerûn. "
                "Ce guide vous explique comment utiliser toutes les commandes liées au temps dans votre campagne D&D."
            ),
            color=0x8B4513
        )

        # Section 1: Commandes disponibles
        commandes_text = (
            "📅 **`/faerun`** - Affiche la date Faerûnienne actuelle\n"
            "📊 **`/faeruncomplet`** - Toutes les infos détaillées (saison, semaine, année DR)\n"
            "🎊 **`/faerunfestival`** - Prochain festival de Faerûn\n"
            "🔄 **`/faerunjdr [date]`** - Convertit une date réelle en Faerûnienne\n"
            "❓ **`/faerun_help`** - Ce guide d'utilisation"
        )
        embed.add_field(
            name="⚡ Commandes Disponibles", 
            value=commandes_text, 
            inline=False
        )

        # Section 2: Le calendrier de Harptos
        calendrier_text = (
            "**12 mois de 30 jours chacun :**\n"
            "• **Hammer** (Hiver) - *Le Marteau*\n"
            "• **Alturiak** (Hiver) - *La Griffe de l'Hiver*\n"
            "• **Ches** (Hiver) - *Les Couchers du Soleil*\n"
            "• **Tarsakh** (Printemps) - *Les Tempêtes*\n"
            "• **Mirtul** (Printemps) - *Le Dégel*\n"
            "• **Kythorn** (Printemps) - *L'Heure des Fleurs*\n"
            "• **Flamerule** (Été) - *Le Temps des Flammes*\n"
            "• **Eleasis** (Été) - *Les Hautes Chaleurs*\n"
            "• **Eleint** (Été) - *Les Précipitations*\n"
            "• **Marpenoth** (Automne) - *Le Fanage des Feuilles*\n"
            "• **Uktar** (Automne) - *Le Pourrissement*\n"
            "• **Nightal** (Automne) - *Le Soleil Descendant*"
        )
        embed.add_field(
            name="📆 Calendrier de Harptos", 
            value=calendrier_text, 
            inline=False
        )

        # Section 3: Festivals spéciaux
        festivals_text = (
            "🎭 **Midwinter** - Plein Hiver (après Hammer)\n"
            "🌱 **Greengrass** - Herbe Verte (après Tarsakh)\n"
            "☀️ **Midsummer** - Solstice d'Été (après Flamerule)\n"
            "🌾 **Highharvestide** - Hautes Moissons (après Eleint)\n"
            "🌙 **Feast of the Moon** - Fête de la Lune (après Marpenoth)\n"
            "🛡️ **Shieldmeet** - Rencontre des Boucliers (années bissextiles)"
        )
        embed.add_field(
            name="🎊 Festivals de Faerûn", 
            value=festivals_text, 
            inline=False
        )

        # Section 4: Exemples d'utilisation
        exemples_text = (
            "• `/faerun` → *Affiche : \"Tar, 15 Mirtul 1492 DR – Season: Spring – Week 21\"*\n"
            "• `/faerunfestival` → *\"Midsummer, le 30 Flamerule 1492 DR (21/07/2024)\"*\n"
            "• `/faerunjdr 25-12-2024` → *Convertit Noël 2024 en date Faerûnienne*\n"
            "• `/faeruncomplet` → *Vue détaillée avec tous les éléments*"
        )
        embed.add_field(
            name="💡 Exemples d'Utilisation", 
            value=exemples_text, 
            inline=False
        )

        # Section 5: Informations utiles
        infos_text = (
            "**📏 Structure temporelle :**\n"
            "• 1 année = 365 jours (366 en année bissextile)\n"
            "• 1 semaine = 10 jours (décade)\n"
            "• Années DR (Dalereckoning) = Années réelles - 628\n\n"
            "**🎲 Pour vos campagnes :**\n"
            "• Planifiez vos événements selon les festivals\n"
            "• Utilisez les saisons pour l'ambiance\n"
            "• Convertissez les dates importantes de votre histoire"
        )
        embed.add_field(
            name="ℹ️ Informations Utiles", 
            value=infos_text, 
            inline=False
        )

        # Section 6: Conseils de MJ
        conseils_text = (
            "🎯 **Immersion maximale :**\n"
            "• Annoncez les dates en Faerûnien dans vos sessions\n"
            "• Utilisez les festivals comme événements de campagne\n"
            "• Adaptez les quêtes aux saisons (hiver = difficultés, été = voyages)\n\n"
            "🗓️ **Astuce :** Utilisez `/faerunfestival` pour planifier vos prochains événements majeurs !"
        )
        embed.add_field(
            name="🎭 Conseils pour les MJ", 
            value=conseils_text, 
            inline=False
        )

        # Footer
        embed.set_footer(
            text="🏰 Royaumes Oubliés • Calendrier de Harptos • Bot Faerûn",
            icon_url=None
        )

        # Timestamp
        embed.timestamp = discord.utils.utcnow()

        await interaction.response.send_message(embed=embed, ephemeral=True)
