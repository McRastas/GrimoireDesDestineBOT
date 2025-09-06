"""
Commande Discord : /mentionlist

DESCRIPTION:
    Compte et liste les mentions et posts de récompenses des utilisateurs du canal

FONCTIONNEMENT:
    - Récupère les auteurs actifs du canal actuel (1000 derniers messages)
    - Parcourt le canal #recompenses sur 30 jours
    - Compte les mentions reçues par chaque utilisateur
    - Compte les posts avec 2+ mentions (posts MJ)
    - Affiche un classement par mentions reçues

UTILISATION:
    /mentionlist
    /mentionlist public:True
"""

import discord
from discord import app_commands
from datetime import datetime, timezone, timedelta
import logging
from typing import Optional
from .base import BaseCommand
from utils.channels import ChannelHelper

logger = logging.getLogger(__name__)


class MentionListCommand(BaseCommand):
    """Commande pour lister les mentions et posts de récompenses des utilisateurs du canal."""

    @property
    def name(self) -> str:
        return "mentionlist"

    @property
    def description(self) -> str:
        return "Compte les mentions et posts de récompenses des posteurs du canal (30 derniers jours)"

    def register(self, tree: app_commands.CommandTree):
        """Enregistre la commande dans l'arbre des commandes Discord."""
        
        @tree.command(name=self.name, description=self.description)
        @app_commands.describe(
            public="Afficher les statistiques publiquement (visible par tous) - défaut: non"
        )
        async def mentionlist_command(
            interaction: discord.Interaction,
            public: Optional[bool] = False
        ):
            await self.callback(interaction, public)

    async def callback(self, interaction: discord.Interaction, public: Optional[bool] = False):
        """
        Exécute la commande mentionlist.
        
        Args:
            interaction: Interaction Discord
            public: Si True, le message sera visible par tous, sinon temporaire (défaut: False)
        """
        try:
            # Déterminer si le message doit être temporaire ou public
            is_ephemeral = not public  # Si public=True, ephemeral=False, et vice versa
            
            # Defer car ça peut prendre du temps
            await interaction.response.defer(ephemeral=is_ephemeral)
            
            # Utiliser le système de canaux configurables
            recompenses_channel = ChannelHelper.get_recompenses_channel(interaction.guild)
            if not recompenses_channel:
                error_msg = ChannelHelper.get_channel_error_message(
                    ChannelHelper.RECOMPENSES)
                await interaction.followup.send(error_msg)
                return
                
            now = datetime.now(timezone.utc)
            thirty_days_ago = now - timedelta(days=30)
            
            # Récupérer les auteurs du canal actuel
            auteurs = {}
            async for msg in interaction.channel.history(limit=1000, oldest_first=True):
                if msg.author.bot:
                    continue
                auteurs[msg.author.id] = msg.author
                
            # Exclure le créateur du thread si c'est un thread
            if isinstance(interaction.channel, discord.Thread) and interaction.channel.owner_id:
                auteurs.pop(interaction.channel.owner_id, None)
                
            if not auteurs:
                await interaction.followup.send(
                    "Aucun utilisateur actif trouvé dans ce canal.")
                return

            # Compter mentions et posts MJ
            mentions_count = {user_id: 0 for user_id in auteurs.keys()}
            posts_mj_count = {user_id: 0 for user_id in auteurs.keys()}
            messages_parcourus = 0

            async for msg in recompenses_channel.history(limit=1000, after=thirty_days_ago):
                messages_parcourus += 1
                
                # Compter mentions
                for mentioned in msg.mentions:
                    if mentioned.id in mentions_count:
                        mentions_count[mentioned.id] += 1
                
                # Compter posts MJ (posts avec 2+ mentions)
                if len(msg.mentions) >= 2 and msg.author.id in posts_mj_count:
                    posts_mj_count[msg.author.id] += 1

            # Trier par mentions décroissantes
            sorted_users = sorted(mentions_count.items(), 
                                key=lambda x: x[1], reverse=True)

            # Construction du message
            if not any(count > 0 for count in mentions_count.values()):
                description = "Aucune mention trouvée pour les posteurs de ce canal."
            else:
                lines = []
                for i, (user_id, mention_count) in enumerate(sorted_users[:15]):
                    if mention_count == 0:
                        continue
                        
                    user = auteurs.get(user_id)
                    if not user:
                        continue
                        
                    posts_mj = posts_mj_count.get(user_id, 0)
                    emoji = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else "📍"
                    
                    line = f"{emoji} **{user.display_name}**"
                    if mention_count > 0:
                        line += f" - {mention_count} mention{'s' if mention_count > 1 else ''}"
                    if posts_mj > 0:
                        line += f" - {posts_mj} post{'s' if posts_mj > 1 else ''} MJ"
                    
                    lines.append(line)

                if lines:
                    description = "\n".join(lines)
                else:
                    description = "Aucune mention trouvée pour les posteurs de ce canal."

            # Créer l'embed
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
            
            # Footer avec légende et info sur la visibilité
            footer_text = "Mentions = fois mentionné | Posts MJ = messages avec 2+ mentions"
            if public:
                footer_text += f" • Message public partagé par {interaction.user.display_name}"
            
            embed.set_footer(text=footer_text)
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Erreur dans la commande /mentionlist : {e}", exc_info=True)
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