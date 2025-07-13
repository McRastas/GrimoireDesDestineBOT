"""
Commande Discord : /mentionlist

DESCRIPTION:
    Compte les mentions de tous les utilisateurs actifs du canal actuel dans #recompenses

FONCTIONNEMENT:
    - Récupère tous les auteurs ayant posté dans le canal actuel (historique complet)
    - Exclut les bots et le créateur du thread (si c'est un thread)
    - Pour chaque auteur, compte ses mentions dans #recompenses sur 30 jours
    - Affiche un classement trié par nombre de mentions décroissant
    - Gestion d'erreur robuste avec logging

UTILISATION:
    /mentionlist (dans n'importe quel canal)
"""

import discord
from datetime import datetime, timezone, timedelta
import logging
from .base import BaseCommand

logger = logging.getLogger(__name__)


class MentionListCommand(BaseCommand):

    @property
    def name(self) -> str:
        return "mentionlist"

    @property
    def description(self) -> str:
        return "Compte les mentions de tous les posteurs de ce salon dans #recompenses (30 derniers jours)"

    async def callback(self, interaction: discord.Interaction):
        try:
            recompenses_channel = discord.utils.get(
                interaction.guild.text_channels, name='recompenses')
            if not recompenses_channel:
                await interaction.response.send_message(
                    "❌ Le canal #recompenses est introuvable.", ephemeral=True)
                return

            now = datetime.now(timezone.utc)
            thirty_days_ago = now - timedelta(days=30)
            auteurs = {}

            async for msg in interaction.channel.history(limit=1000,
                                                         oldest_first=True):
                if msg.author.bot:
                    continue
                auteurs[msg.author.id] = msg.author

            if isinstance(interaction.channel,
                          discord.Thread) and interaction.channel.owner_id:
                auteurs.pop(interaction.channel.owner_id, None)

            if not auteurs:
                await interaction.response.send_message(
                    "Aucun utilisateur actif trouvé dans ce canal.",
                    ephemeral=True)
                return

            mention_counts = {user_id: 0 for user_id in auteurs}

            async for msg in recompenses_channel.history(
                    limit=1000, after=thirty_days_ago):
                for user_id, user in auteurs.items():
                    if user in msg.mentions:
                        mention_counts[user_id] += 1

            lignes = [
                f"• **{auteurs[user_id].display_name}** : {count} mention(s)"
                for user_id, count in sorted(mention_counts.items(),
                                             key=lambda item: item[1],
                                             reverse=True)
            ]

            description = "\n".join(
                lignes) if lignes else "Aucune donnée trouvée."
            embed = discord.Embed(
                title="📊 Mentions dans #recompenses (30 derniers jours)",
                description=description,
                color=0x00b0f4)
            await interaction.response.send_message(embed=embed,
                                                    ephemeral=True)

        except Exception as e:
            logger.error(f"Erreur dans la commande /mention_list : {e}",
                         exc_info=True)
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    "❌ Une erreur inattendue est survenue.", ephemeral=True)