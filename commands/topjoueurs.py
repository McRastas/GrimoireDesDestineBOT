import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime
from collections import defaultdict
import os

class TopJoueurs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.recompense_channel_id = int(os.getenv('RECOMPENSE_CHANNEL_ID'))

    @app_commands.command(name="topjoueurs", description="Affiche le classement des joueurs les plus mentionnés dans le canal récompense")
    @app_commands.describe(limite="Nombre de joueurs à afficher (défaut: 10, max: 25)")
    async def topjoueurs(self, interaction: discord.Interaction, limite: int = 10):
        """Affiche le top des joueurs les plus mentionnés dans le canal récompense"""
        
        # Validation de la limite
        if limite < 1:
            await interaction.response.send_message("❌ La limite doit être au moins 1.", ephemeral=True)
            return
        if limite > 25:
            await interaction.response.send_message("❌ La limite maximale est 25 joueurs.", ephemeral=True)
            return

        await interaction.response.defer()

        # Récupérer le canal récompense
        channel = self.bot.get_channel(self.recompense_channel_id)
        if not channel:
            await interaction.followup.send("❌ Canal récompense introuvable.")
            return

        # Dictionnaire pour compter les mentions par utilisateur
        mention_counts = defaultdict(int)
        total_messages = 0
        messages_with_mentions = 0

        try:
            # Parcourir TOUS les messages du canal
            async for message in channel.history(limit=None, oldest_first=False):
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
            sorted_players = sorted(mention_counts.items(), key=lambda x: x[1], reverse=True)
            
            # Limiter au top demandé
            top_players = sorted_players[:limite]

            # Créer l'embed
            embed = discord.Embed(
                title=f"🏆 Top {len(top_players)} des Joueurs",
                description=f"Classement basé sur les mentions dans <#{self.recompense_channel_id}>",
                color=discord.Color.gold(),
                timestamp=datetime.now()
            )

            # Emojis pour le podium
            medals = {0: "🥇", 1: "🥈", 2: "🥉"}

            # Ajouter les joueurs au classement
            if top_players:
                ranking_text = ""
                for index, (user_id, count) in enumerate(top_players):
                    user = self.bot.get_user(user_id)
                    username = user.mention if user else f"<@{user_id}>"
                    
                    # Ajouter médaille pour le top 3
                    medal = medals.get(index, f"**{index + 1}.**")
                    
                    ranking_text += f"{medal} {username} — **{count}** mention{'s' if count > 1 else ''}\n"

                embed.add_field(
                    name="Classement",
                    value=ranking_text,
                    inline=False
                )

                # Statistiques générales
                total_mentions = sum(count for _, count in mention_counts.items())
                embed.add_field(
                    name="📊 Statistiques",
                    value=f"**{total_mentions}** mentions totales\n"
                          f"**{len(mention_counts)}** joueurs mentionnés\n"
                          f"**{messages_with_mentions}** messages avec mentions\n"
                          f"**{total_messages}** messages analysés",
                    inline=False
                )

            else:
                embed.description = "Aucune mention trouvée dans le canal récompense."

            embed.set_footer(text=f"Demandé par {interaction.user.display_name}")

            await interaction.followup.send(embed=embed)

        except discord.Forbidden:
            await interaction.followup.send("❌ Je n'ai pas la permission de lire l'historique du canal récompense.")
        except Exception as e:
            await interaction.followup.send(f"❌ Une erreur s'est produite : {str(e)}")
            print(f"Erreur dans topjoueurs: {e}")

async def setup(bot):
    await bot.add_cog(TopJoueurs(bot))