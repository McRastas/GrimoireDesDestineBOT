"""Commandes liées aux quêtes."""

import discord
from discord import app_commands
from datetime import datetime, timezone, timedelta
import re
import logging
from .base import BaseCommand

logger = logging.getLogger(__name__)


class MesQuetesCommand(BaseCommand):

    @property
    def name(self) -> str:
        return "mesquetes"

    @property
    def description(self) -> str:
        return "Liste les quêtes où tu es mentionné dans #départ-à-l-aventure (dates futures)"

    def register(self, tree: app_commands.CommandTree):
        """Enregistrement spécial pour cette commande avec paramètre optionnel."""

        @tree.command(name=self.name, description=self.description)
        @app_commands.describe(
            membre="Le membre à rechercher (par défaut toi-même)")
        async def mes_quetes_command(interaction: discord.Interaction,
                                     membre: discord.Member = None):
            await self.callback(interaction, membre)

    async def callback(self,
                       interaction: discord.Interaction,
                       membre: discord.Member = None):
        # Defer la réponse pour éviter le timeout
        await interaction.response.defer(ephemeral=True)

        cible = membre or interaction.user
        channel = discord.utils.get(interaction.guild.text_channels,
                                    name='départ-à-l-aventure')

        if not channel:
            await interaction.followup.send(
                "❌ Le canal #départ-à-l-aventure est introuvable.")
            return

        now = datetime.now(timezone.utc)
        thirty_days_ago = now - timedelta(days=30)

        # Récupérer tous les messages des 30 derniers jours où le joueur est mentionné
        messages_avec_mention = []
        messages_parcourus = 0

        async for message in channel.history(limit=1000,
                                             after=thirty_days_ago):
            messages_parcourus += 1
            if message.author.bot:
                continue
            if cible in message.mentions:
                messages_avec_mention.append(message)

        # Analyser ces messages pour trouver des dates
        resultats_futures = []
        resultats_sans_date = []

        for message in messages_avec_mention:
            premiere_ligne = message.content.split('\n', 1)[0].strip()

            # Chercher une date dans le message avec plusieurs formats
            date_patterns = [
                r'(\d{1,2})[/\-](\d{1,2})[/\-](\d{4})',  # JJ/MM/AAAA ou JJ-MM-AAAA
                r'(\d{1,2})[/\-](\d{1,2})[/\-](\d{2})',  # JJ/MM/AA ou JJ-MM-AA
                r'(\d{1,2})[/\-](\d{1,2})(?![/\-\d])',  # JJ/MM ou JJ-MM (sans année)
                r'(\d{1,2})\.(\d{1,2})(?:\.(\d{2,4}))?',  # JJ.MM.AAAA ou JJ.MM
                r'(\d{1,2})\s+(\d{1,2})\s+(\d{4})',  # JJ MM AAAA (avec espaces)
            ]

            date_trouvee = False
            for pattern in date_patterns:
                date_match = re.search(pattern, message.content)
                if date_match:
                    try:
                        jour = int(date_match.group(1))
                        mois = int(date_match.group(2))

                        # Validation basique
                        if not (1 <= jour <= 31 and 1 <= mois <= 12):
                            continue

                        # Gestion de l'année selon le nombre de groupes capturés
                        if len(date_match.groups()) >= 3 and date_match.group(
                                3):
                            annee = int(date_match.group(3))
                            if annee < 100:  # Année sur 2 chiffres
                                annee = 2000 + annee
                        else:
                            # Pas d'année spécifiée - logique améliorée pour gérer la fin d'année
                            annee = now.year
                            if now.month >= 11 and mois <= 2:
                                annee = now.year + 1
                            elif now.month <= 2 and mois >= 11:
                                continue
                            else:
                                try:
                                    test_date = datetime(annee,
                                                         mois,
                                                         jour,
                                                         tzinfo=timezone.utc)
                                    if test_date < now:
                                        annee = now.year + 1
                                except ValueError:
                                    annee = now.year + 1

                        # Créer la date de la quête
                        quest_date = datetime(annee,
                                              mois,
                                              jour,
                                              tzinfo=timezone.utc)
                        jours_restants = (quest_date - now).days

                        # Ne garder que les quêtes futures ou d'aujourd'hui (max 60 jours)
                        if 0 <= jours_restants <= 60:
                            date_formatee = f"{jour:02d}/{mois:02d}/{annee}"

                            if jours_restants == 0:
                                quand = "🔴 **AUJOURD'HUI**"
                            elif jours_restants == 1:
                                quand = "🟠 **Demain**"
                            elif jours_restants <= 7:
                                quand = f"🟡 Dans {jours_restants} jours"
                            else:
                                quand = f"🟢 Dans {jours_restants} jours"

                            resultats_futures.append({
                                'jours':
                                jours_restants,
                                'texte':
                                f"{quand} ({date_formatee})\n└─ {premiere_ligne[:80]}{'...' if len(premiere_ligne) > 80 else ''}"
                            })
                            date_trouvee = True
                            break

                    except ValueError:
                        continue

            if not date_trouvee:
                resultats_sans_date.append(premiere_ligne)

        # Trier les quêtes futures par date
        resultats_futures.sort(key=lambda x: x['jours'])

        # Construire l'embed
        embed = discord.Embed(title=f"📅 Quêtes à venir - {cible.display_name}",
                              color=0x3498db)

        if resultats_futures:
            desc_futures = "\n\n".join(
                [r['texte'] for r in resultats_futures[:10]])
            embed.add_field(
                name=f"🎯 Quêtes planifiées ({len(resultats_futures)})",
                value=desc_futures,
                inline=False)
        else:
            embed.add_field(name="🎯 Quêtes planifiées",
                            value="*Aucune quête avec date future trouvée*",
                            inline=False)

        # Ajouter les mentions sans date si peu de quêtes futures
        if resultats_sans_date and len(resultats_futures) < 5:
            desc_sans_date = "\n".join([
                f"• {q[:60]}..." if len(q) > 60 else f"• {q}"
                for q in resultats_sans_date[:5]
            ])
            embed.add_field(
                name=
                f"📌 Mentions récentes sans date ({len(resultats_sans_date)})",
                value=desc_sans_date,
                inline=False)

        embed.set_footer(
            text=
            f"Analysé {messages_parcourus} messages des 30 derniers jours | {len(messages_avec_mention)} mentions trouvées"
        )

        await interaction.followup.send(embed=embed)
