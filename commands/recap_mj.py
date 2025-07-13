"""
Commande Discord : /recapmj [membre]

DESCRIPTION:
    Compte et liste les messages dans #recompenses où un MJ mentionne au moins 2 personnes différentes

FONCTIONNEMENT:
    - Paramètre optionnel : membre à analyser (par défaut l'auteur de la commande)
    - Parcourt #recompenses sur 30 jours pour les messages de ce membre
    - Pour chaque message, compte les mentions uniques (excluant l'auteur)
    - Liste tous les messages avec 2+ mentions différentes
    - Affiche avec liens cliquables et détails des mentions

UTILISATION:
    /recapmj
    /recapmj membre:@MaitreJeu
"""

import discord
from discord import app_commands
from datetime import datetime, timezone, timedelta
from .base import BaseCommand


class RecapMjCommand(BaseCommand):

    @property
    def name(self) -> str:
        return "recapmj"

    @property
    def description(self) -> str:
        return "Liste les messages dans #recompenses où le MJ mentionne 2+ personnes"

    def register(self, tree: app_commands.CommandTree):
        """Enregistrement spécial pour cette commande avec paramètre optionnel."""

        @tree.command(name=self.name, description=self.description)
        @app_commands.describe(
            membre="Le membre dont on veut analyser les posts (par défaut toi)"
        )
        async def recap_mj_command(interaction: discord.Interaction,
                                   membre: discord.Member = None):
            await self.callback(interaction, membre)

    async def callback(self,
                       interaction: discord.Interaction,
                       membre: discord.Member = None):
        # Defer pour éviter timeout
        await interaction.response.defer(ephemeral=True)

        cible = membre or interaction.user
        channel = discord.utils.get(interaction.guild.text_channels,
                                    name='recompenses')

        if not channel:
            await interaction.followup.send(
                "❌ Le canal #recompenses est introuvable.")
            return

        now = datetime.now(timezone.utc)
        thirty_days_ago = now - timedelta(days=30)

        # Collecter tous les messages multi-mentions du MJ
        posts_multi_mentions = []
        messages_parcourus = 0
        total_mentions_uniques = 0

        async for message in channel.history(limit=1000,
                                             after=thirty_days_ago):
            messages_parcourus += 1

            if message.author.id == cible.id:
                # Compter les mentions uniques (en excluant l'auteur)
                mentions_uniques = set(user.id for user in message.mentions
                                       if user.id != cible.id)

                if len(mentions_uniques) >= 2:
                    # Créer le lien vers le message
                    message_url = f"https://discord.com/channels/{interaction.guild.id}/{channel.id}/{message.id}"

                    # Prendre la première ligne du message pour l'aperçu
                    premiere_ligne = message.content.split('\n', 1)[0].strip()
                    if not premiere_ligne:
                        premiere_ligne = "*[Message vide ou embed]*"

                    # Tronquer si trop long
                    apercu = premiere_ligne[:50] + (
                        '...' if len(premiere_ligne) > 50 else '')

                    # Info sur la date relative
                    delta = now - message.created_at
                    if delta.days == 0:
                        when = "Aujourd'hui"
                    elif delta.days == 1:
                        when = "Hier"
                    elif delta.days <= 7:
                        when = f"Il y a {delta.days} jours"
                    else:
                        when = f"Il y a {delta.days} jours"

                    # Récupérer les noms des personnes mentionnées
                    mentions_noms = [
                        user.display_name for user in message.mentions
                        if user.id != cible.id
                    ]
                    mentions_str = ", ".join(
                        mentions_noms[:5])  # Max 5 noms affichés
                    if len(mentions_noms) > 5:
                        mentions_str += f" +{len(mentions_noms) - 5} autres"

                    posts_multi_mentions.append({
                        'apercu':
                        apercu,
                        'url':
                        message_url,
                        'when':
                        when,
                        'nb_mentions':
                        len(mentions_uniques),
                        'mentions_str':
                        mentions_str,
                        'date':
                        message.created_at
                    })

                    total_mentions_uniques += len(mentions_uniques)

        # Trier par date (plus récent en premier)
        posts_multi_mentions.sort(key=lambda x: x['date'], reverse=True)

        # Construire l'embed
        embed = discord.Embed(
            title=f"📋 Posts multi-mentions de {cible.display_name}",
            description=
            f"**{len(posts_multi_mentions)} posts de récompense** avec 2+ mentions sur 30 jours",
            color=0x7289DA)

        if posts_multi_mentions:
            # Afficher jusqu'à 6 posts récents avec gestion des limites
            desc_posts = []
            char_count = 0
            max_chars = 900  # Limite de sécurité

            for post in posts_multi_mentions[:
                                             12]:  # Max 12 pour avoir du choix
                # Raccourcir pour économiser l'espace
                apercu_court = post['apercu'][:40] + ('...' if len(
                    post['apercu']) > 40 else '')
                mentions_court = post['mentions_str'][:40] + ('...' if len(
                    post['mentions_str']) > 40 else '')

                line = (
                    f"• **{post['when']}** ({post['nb_mentions']} mentions)\n"
                    f"  └─ [{apercu_court}]({post['url']})\n"
                    f"  └─ 👥 {mentions_court}")

                # Vérifier si on peut ajouter cette ligne
                if char_count + len(line) + 3 > max_chars:  # +3 pour \n\n\n
                    break

                desc_posts.append(line)
                char_count += len(line) + 3

            embed.add_field(
                name=f"📋 Posts récents ({len(desc_posts)} affichés)",
                value="\n\n".join(desc_posts),
                inline=False)

            # Statistiques générales (compact)
            avg_mentions = total_mentions_uniques / len(
                posts_multi_mentions) if posts_multi_mentions else 0
            stats_text = f"**Total :** {total_mentions_uniques} mentions | **Moyenne :** {avg_mentions:.1f}/post"

            # Indicateur s'il y en a plus
            if len(posts_multi_mentions) > len(desc_posts):
                remaining = len(posts_multi_mentions) - len(desc_posts)
                stats_text += f" | **Non affichés :** {remaining} posts"

            embed.add_field(name="📊 Statistiques",
                            value=stats_text,
                            inline=False)
        else:
            embed.add_field(
                name="❌ Aucun post multi-mention trouvé",
                value=
                "Aucun message avec 2+ mentions dans #recompenses sur 30 jours",
                inline=False)

        # Footer avec infos de recherche
        embed.set_footer(
            text=f"Analysé {messages_parcourus} messages sur 30 jours")

        await interaction.followup.send(embed=embed)
