"""
Commande Top Joueurs - Classe les joueurs les plus mentionnés
Compte les mentions dans le canal récompenses
"""

import discord
from discord import app_commands
from collections import defaultdict
from typing import Optional
from .base import BaseCommand


class TopJoueurs(BaseCommand):
    """Commande pour afficher le top des joueurs les plus mentionnés."""

    @property
    def name(self) -> str:
        return "topjoueurs"

    @property
    def description(self) -> str:
        return "Affiche le classement des joueurs les plus mentionnés dans le canal récompense"
    
    def register(self, tree: app_commands.CommandTree):
        """Enregistre la commande avec ses paramètres."""
        @app_commands.command(name=self.name, description=self.description)
        @app_commands.describe(
            limite="Nombre de joueurs à afficher (entre 5 et 25, défaut: 10)"
        )
        async def topjoueurs_cmd(interaction: discord.Interaction, limite: Optional[int] = 10):
            await self.callback(interaction, limite)
        
        tree.add_command(topjoueurs_cmd)

    async def callback(
        self, 
        interaction: discord.Interaction,
        limite: int = 10
    ):
        """Analyse les mentions dans le canal récompenses et affiche le classement des joueurs."""
        
        # Validation du nombre (entre 5 et 25)
        limite_original = limite
        if limite < 5:
            limite = 5
        elif limite > 25:
            limite = 25
        
        # Réponse discrète (ephemeral) - visible uniquement par l'utilisateur
        await interaction.response.defer(ephemeral=True)
        
        # Message d'avertissement si le nombre a été ajusté
        adjusted_warning = ""
        if limite_original != limite:
            adjusted_warning = f"⚠️ Nombre ajusté de {limite_original} à {limite} (limites: 5-25)\n\n"

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

            # Message de progression (ephemeral)
            await interaction.followup.send(
                f"{adjusted_warning}📊 Analyse des mentions en cours...\n"
                f"Canal : #{recompense_channel.name}",
                ephemeral=True
            )

            # Collecter tous les messages
            all_messages = []
            async for message in recompense_channel.history(limit=None):
                all_messages.append(message)
                
                # Limite de sécurité (10000 messages max)
                if len(all_messages) >= 10000:
                    break

            # Compter les mentions par utilisateur
            mention_counts = defaultdict(int)
            total_messages = 0
            messages_with_mentions = 0

            for message in all_messages:
                total_messages += 1
                
                # Ignorer les messages de bots
                if message.author.bot:
                    continue

                # Récupérer les mentions uniques dans ce message
                mentioned_users = set()
                for mention in message.mentions:
                    # Ignorer les auto-mentions
                    if mention.id != message.author.id:
                        mentioned_users.add(mention.id)

                # Compter les mentions
                if mentioned_users:
                    messages_with_mentions += 1
                    for user_id in mentioned_users:
                        mention_counts[user_id] += 1

            # Trier par nombre de mentions (décroissant)
            sorted_players = sorted(
                mention_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:limite]

            if not sorted_players:
                await interaction.edit_original_response(
                    content="📊 Aucune mention trouvée dans le canal récompense."
                )
                return

            # Créer l'embed (sera ephemeral automatiquement)
            embed = discord.Embed(
                title=f"🏆 Top {len(sorted_players)} des Joueurs",
                description=f"Classement basé sur les mentions dans #{recompense_channel.name}",
                color=discord.Color.gold(),
                timestamp=discord.utils.utcnow()
            )

            # Médailles pour le podium
            medals = ['🥇', '🥈', '🥉']
            
            # Construire le classement
            ranking_text = ""
            for i, (user_id, count) in enumerate(sorted_players):
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
                
                mention_text = "mention" if count == 1 else "mentions"
                ranking_text += f"{icon} {user_name} - **{count}** {mention_text}\n"

            embed.add_field(
                name="📊 Classement",
                value=ranking_text,
                inline=False
            )

            # Statistiques supplémentaires
            total_mentions = sum(count for _, count in mention_counts.items())
            total_players = len(mention_counts)
            
            stats_text = (
                f"**Mentions totales :** {total_mentions}\n"
                f"**Messages analysés :** {total_messages}\n"
                f"**Messages avec mentions :** {messages_with_mentions}\n"
                f"**Joueurs mentionnés (total) :** {total_players}"
            )
            
            embed.add_field(
                name="📈 Statistiques",
                value=stats_text,
                inline=False
            )

            embed.set_footer(
                text=f"Demandé par {interaction.user.display_name} • Visible uniquement par vous"
            )

            # Éditer le message initial (reste ephemeral)
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
            print(f"❌ Erreur dans topjoueurs: {e}")
            await interaction.followup.send(
                f"❌ Une erreur est survenue lors de l'analyse des messages.\n"
                f"Erreur : {str(e)}",
                ephemeral=True
            )