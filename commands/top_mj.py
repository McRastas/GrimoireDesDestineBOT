"""
Commande Top MJ - Répertorie les 10 MJ les plus actifs
Compte les posts dans le canal récompenses avec au moins 2 mentions
"""

import discord
from discord import app_commands
from collections import defaultdict
from .base import BaseCommand


class TopMjCommand(BaseCommand):
    """Commande pour afficher le top 10 des MJ les plus actifs."""

    @property
    def name(self) -> str:
        return "top-mj"

    @property
    def description(self) -> str:
        return "Affiche le top 10 des MJ les plus actifs sur le serveur"

    async def callback(self, interaction: discord.Interaction):
        """Analyse les posts dans le canal récompenses et affiche le classement des MJ."""
        
        await interaction.response.defer()

        try:
            # Chercher le canal récompenses (plusieurs variantes possibles)
            recompense_channel = None
            for channel in interaction.guild.text_channels:
                if channel.name.lower() in ['recompenses', 'récompenses', 'recompense']:
                    recompense_channel = channel
                    break

            if not recompense_channel:
                await interaction.followup.send(
                    "❌ Le canal **récompenses** n'a pas été trouvé sur ce serveur.\n"
                    "Assurez-vous qu'un canal avec ce nom existe.",
                    ephemeral=True
                )
                return

            # Message de progression
            await interaction.followup.send(
                f"📊 Analyse des messages en cours...\n"
                f"Canal : #{recompense_channel.name}"
            )

            # Collecter tous les messages
            all_messages = []
            async for message in recompense_channel.history(limit=None):
                all_messages.append(message)
                
                # Limite de sécurité (10000 messages max)
                if len(all_messages) >= 10000:
                    break

            # Compter les posts valides par auteur
            mj_stats = defaultdict(int)

            for message in all_messages:
                # Vérifier si le message a au moins 2 mentions
                if len(message.mentions) >= 2:
                    mj_stats[message.author.id] += 1

            # Trier et prendre le top 10
            sorted_mj = sorted(
                mj_stats.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]

            if not sorted_mj:
                await interaction.edit_original_response(
                    content="📊 Aucun MJ trouvé avec des posts contenant au moins 2 mentions."
                )
                return

            # Créer l'embed
            embed = discord.Embed(
                title="🏆 Top 10 des MJ les plus actifs",
                description=f"Classement basé sur les posts dans #{recompense_channel.name} avec au moins 2 mentions",
                color=discord.Color.gold(),
                timestamp=discord.utils.utcnow()
            )

            # Médailles pour le podium
            medals = ['🥇', '🥈', '🥉']
            
            # Construire le classement
            ranking_text = ""
            for i, (user_id, count) in enumerate(sorted_mj):
                try:
                    user = await self.bot.fetch_user(user_id)
                    user_name = f"{user.display_name}"
                except:
                    user_name = f"Utilisateur inconnu"
                
                # Icône pour le classement
                if i < 3:
                    icon = medals[i]
                else:
                    icon = f"**{i + 1}.**"
                
                sessions_text = "session" if count == 1 else "sessions"
                ranking_text += f"{icon} {user_name} - **{count}** {sessions_text}\n"

            embed.add_field(
                name="📊 Classement",
                value=ranking_text,
                inline=False
            )

            # Statistiques supplémentaires
            total_sessions = sum(count for _, count in sorted_mj)
            total_mj = len(mj_stats)
            
            embed.add_field(
                name="📈 Statistiques",
                value=(
                    f"**Total sessions (top 10) :** {total_sessions}\n"
                    f"**Messages analysés :** {len(all_messages)}\n"
                    f"**MJ actifs (total) :** {total_mj}"
                ),
                inline=False
            )

            embed.set_footer(
                text=f"Demandé par {interaction.user.display_name}"
            )

            await interaction.edit_original_response(
                content=None,
                embed=embed
            )

        except discord.Forbidden:
            await interaction.followup.send(
                "❌ Je n'ai pas la permission de lire l'historique du canal récompenses.\n"
                "Vérifiez que le bot a bien la permission `Lire l'historique des messages`.",
                ephemeral=True
            )
        except Exception as e:
            print(f"❌ Erreur dans top-mj: {e}")
            await interaction.followup.send(
                f"❌ Une erreur est survenue lors de l'analyse des messages.\n"
                f"Erreur : {str(e)}",
                ephemeral=True
            )