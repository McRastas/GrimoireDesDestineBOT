"""Commandes liées aux mentions et récompenses."""

import discord
from discord import app_commands
from datetime import datetime, timezone, timedelta
import logging
from .base import BaseCommand

logger = logging.getLogger(__name__)


class MentionSomeoneCommand(BaseCommand):

    @property
    def name(self) -> str:
        return "mentionsomeone"

    @property
    def description(self) -> str:
        return "Compte les mentions dans #recompenses sur 30j"

    def register(self, tree: app_commands.CommandTree):
        """Enregistrement spécial pour cette commande avec paramètre optionnel."""

        @tree.command(name=self.name, description=self.description)
        @app_commands.describe(
            membre="Le membre dont on veut le nombre de mentions")
        async def mentions_command(interaction: discord.Interaction,
                                   membre: discord.Member = None):
            await self.callback(interaction, membre)

    async def callback(self,
                       interaction: discord.Interaction,
                       membre: discord.Member = None):
        cible = membre or interaction.user
        channel = discord.utils.get(interaction.guild.text_channels,
                                    name='recompenses')

        if not channel:
            await interaction.response.send_message(
                "❌ Le canal #recompenses est introuvable.", ephemeral=True)
            return

        count = 0
        now = datetime.now(timezone.utc)
        thirty_days_ago = now - timedelta(days=30)

        async for message in channel.history(limit=1000,
                                             after=thirty_days_ago):
            if cible in message.mentions:
                count += 1

        embed = discord.Embed(
            title="📢 Statistiques de mentions",
            description=
            f"**{cible.display_name}** a été mentionné **{count} fois** dans #recompenses sur 30 jours.",
            color=0x7289DA)
        await interaction.response.send_message(embed=embed, ephemeral=True)


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


class RecapMjCommand(BaseCommand):

    @property
    def name(self) -> str:
        return "recapmj"

    @property
    def description(self) -> str:
        return "Compte le nombre de messages dans #recompenses sur 30j où le MJ mentionne au moins 2 personnes"

    def register(self, tree: app_commands.CommandTree):
        """Enregistrement spécial pour cette commande avec paramètre optionnel."""

        @tree.command(name=self.name, description=self.description)
        @app_commands.describe(
            membre="Le membre dont on veut la stat (par défaut toi)")
        async def recap_mj_command(interaction: discord.Interaction,
                                   membre: discord.Member = None):
            await self.callback(interaction, membre)

    async def callback(self,
                       interaction: discord.Interaction,
                       membre: discord.Member = None):
        cible = membre or interaction.user
        channel = discord.utils.get(interaction.guild.text_channels,
                                    name='recompenses')

        if not channel:
            await interaction.response.send_message(
                "❌ Le canal #recompenses est introuvable.", ephemeral=True)
            return

        now = datetime.now(timezone.utc)
        thirty_days_ago = now - timedelta(days=30)
        nb_messages = 0
        total_mentions = 0

        async for message in channel.history(limit=1000,
                                             after=thirty_days_ago):
            if message.author.id == cible.id:
                mentions_uniques = set(user.id for user in message.mentions
                                       if user.id != cible.id)
                if len(mentions_uniques) >= 2:
                    nb_messages += 1
                    total_mentions += len(mentions_uniques)

        embed = discord.Embed(
            title="📋 Messages multi-mentions dans #recompenses",
            description=
            (f"**{cible.display_name}** a posté **{nb_messages} poste de récompense** "
             f"dans #recompenses (sur 30j) où il/elle mentionne au moins deux personnes différentes."
             ),
            color=0x7289DA)
        await interaction.response.send_message(embed=embed, ephemeral=True)
