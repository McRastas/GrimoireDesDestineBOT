import discord
from discord import app_commands
from datetime import datetime, timezone, timedelta
import logging

from commands.base import BaseCommand

logger = logging.getLogger(__name__)


class MentionListCommand(BaseCommand):
    """Commande pour lister les mentions et posts de récompenses des utilisateurs du canal."""

    def __init__(self):
        super().__init__(
            name="mentionlist",
            description="Compte les mentions et posts de récompenses des posteurs du canal (30 derniers jours)"
        )

    async def callback(self, interaction: discord.Interaction):
        """Exécute la commande mentionlist."""
        try:
            # Defer car ça peut prendre du temps
            await interaction.response.defer(ephemeral=True)
            
            recompenses_channel = discord.utils.get(
                interaction.guild.text_channels, name='recompenses')
            if not recompenses_channel:
                await interaction.followup.send(
                    "❌ Le canal #recompenses est introuvable.")
                return
                
            now = datetime.now(timezone.utc)
            thirty_days_ago = now - timedelta(days=30)
            
            # Récupérer les auteurs du canal actuel
            auteurs = {}
            async for msg in interaction.channel.history(
                    limit=1000, oldest_first=True):
                if msg.author.bot:
                    continue
                auteurs[msg.author.id] = msg.author
                
            if isinstance(interaction.channel,
                          discord.Thread) and interaction.channel.owner_id:
                auteurs.pop(interaction.channel.owner_id, None)
                
            if not auteurs:
                await interaction.followup.send(
                    "Aucun utilisateur actif trouvé dans ce canal.")
                return
            
            # Initialiser les compteurs
            stats = {}
            for user_id in auteurs:
                stats[user_id] = {
                    'mentions_reçues': 0,
                    'posts_recompenses': 0
                }
            
            # Parcourir les messages de #recompenses
            async for msg in recompenses_channel.history(
                    limit=1000, after=thirty_days_ago):
                # Compter les mentions reçues
                for user_id, user in auteurs.items():
                    if user in msg.mentions:
                        stats[user_id]['mentions_reçues'] += 1
                
                # Compter les posts de récompenses (2+ mentions)
                if msg.author.id in auteurs:
                    mentions_uniques = set(user.id for user in msg.mentions
                                         if user.id != msg.author.id)
                    if len(mentions_uniques) >= 2:
                        stats[msg.author.id]['posts_recompenses'] += 1
            
            # Trier par mentions reçues (décroissant)
            sorted_stats = sorted(stats.items(),
                                key=lambda x: x[1]['mentions_reçues'],
                                reverse=True)
            
            # Construire l'affichage
            lignes = []
            for user_id, data in sorted_stats:
                user = auteurs[user_id]
                mentions = data['mentions_reçues']
                posts = data['posts_recompenses']
                
                # Format : "• Nom : X mentions | Y posts"
                ligne = f"• **{user.display_name}** : {mentions} mention{'s' if mentions != 1 else ''}"
                if posts > 0:
                    ligne += f" | {posts} post{'s' if posts != 1 else ''} MJ"
                lignes.append(ligne)
            
            description = "\n".join(lignes) if lignes else "Aucune donnée trouvée."
            
            embed = discord.Embed(
                title="📊 Statistiques #recompenses (30 derniers jours)",
                description=description,
                color=0x00b0f4)
            
            # Ajouter des infos sur le canal source
            embed.add_field(
                name="Canal source",
                value=f"{interaction.channel.mention}",
                inline=True
            )
            embed.add_field(
                name="Période",
                value="30 derniers jours",
                inline=True
            )
            
            # Footer avec légende
            embed.set_footer(
                text="Mentions = fois mentionné | Posts MJ = messages avec 2+ mentions"
            )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Erreur dans la commande /mentionlist : {e}",
                         exc_info=True)
            try:
                if interaction.response.is_done():
                    await interaction.followup.send(
                        "❌ Une erreur inattendue est survenue.")
                else:
                    await interaction.response.send_message(
                        "❌ Une erreur inattendue est survenue.",
                        ephemeral=True)
            except Exception:
                pass
