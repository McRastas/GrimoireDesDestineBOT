"""
Commande Discord : /mesquetes [membre]

DESCRIPTION:
    Liste les quêtes où un joueur est mentionné dans le canal quêtes avec dates futures

FONCTIONNEMENT:
    - Paramètre optionnel : membre à rechercher (par défaut l'auteur)
    - Recherche dans le canal quêtes configuré les mentions sur 30 jours
    - Analyse avec MAXIMUM de formats de dates possibles (MJ ne sont pas des ordis !)
    - LOGIQUE D'ANNÉE INTELLIGENTE pour dates sans année
    - Classification en 3 catégories : futures, passées, sans date détectable

UTILISATION:
    /mesquetes
    /mesquetes membre:@Aventurier
"""

import discord
from discord import app_commands
from datetime import datetime, timezone, timedelta
import re
import logging
from .base import BaseCommand
from utils.channels import ChannelHelper

logger = logging.getLogger(__name__)


class MesQuetesCommand(BaseCommand):

    @property
    def name(self) -> str:
        return "mesquetes"

    @property
    def description(self) -> str:
        return "Liste les quêtes où tu es mentionné dans le canal quêtes (dates futures)"

    def register(self, tree: app_commands.CommandTree):
        """Enregistrement spécial pour cette commande avec paramètre optionnel."""

        @tree.command(name=self.name, description=self.description)
        @app_commands.describe(
            membre="Le membre à rechercher (par défaut toi-même)")
        async def mes_quetes_command(interaction: discord.Interaction,
                                     membre: discord.Member = None):
            await self.callback(interaction, membre)

    def _determine_best_year(self, jour: int, mois: int, now: datetime) -> int:
        """
        Détermine l'année la plus logique pour une date JJ/MM sans année.
        LOGIQUE SIMPLIFIÉE : privilégier les dates les plus proches.
        """
        current_year = now.year

        try:
            # Option 1: Année actuelle
            date_current_year = datetime(current_year,
                                         mois,
                                         jour,
                                         tzinfo=timezone.utc)
            days_diff_current = (date_current_year - now).days

            # Option 2: Année suivante
            date_next_year = datetime(current_year + 1,
                                      mois,
                                      jour,
                                      tzinfo=timezone.utc)
            days_diff_next = (date_next_year - now).days

            # Option 3: Année précédente (pour les dates très récemment passées)
            date_prev_year = datetime(current_year - 1,
                                      mois,
                                      jour,
                                      tzinfo=timezone.utc)
            days_diff_prev = (date_prev_year - now).days

            # Choisir l'année qui donne la date la plus proche (en valeur absolue)
            options = [(abs(days_diff_current), current_year,
                        days_diff_current),
                       (abs(days_diff_next), current_year + 1, days_diff_next),
                       (abs(days_diff_prev), current_year - 1, days_diff_prev)]

            # Trier par proximité (valeur absolue des jours)
            options.sort(key=lambda x: x[0])

            # Prendre la plus proche, mais éviter les dates trop anciennes (> 60 jours passés)
            for abs_days, year, real_days in options:
                if real_days >= -60:  # Pas plus de 60 jours dans le passé
                    return year

            # Si toutes sont trop anciennes, prendre l'année actuelle par défaut
            return current_year

        except ValueError:
            # Date invalide (ex: 29/02 année non bissextile)
            return current_year

    def _extract_date_from_text(self, text: str, now: datetime) -> tuple:
        """
        Extrait une date du texte avec MAXIMUM de formats possibles.
        Retourne (datetime_obj, date_string_found) ou (None, None)
        """

        # Nettoyer le texte pour éviter les faux positifs
        text_clean = text.replace('h', ':').replace('H',
                                                    ':')  # "14h30" -> "14:30"

        # MEGA liste de patterns pour tous les formats possibles
        date_patterns = [
            # === FORMATS AVEC ANNÉE COMPLÈTE ===
            r'(\d{1,2})[/\-\.](\d{1,2})[/\-\.](\d{4})',  # JJ/MM/AAAA, JJ-MM-AAAA, JJ.MM.AAAA
            r'(\d{1,2})\s+(\d{1,2})\s+(\d{4})',  # JJ MM AAAA
            r'(\d{4})[/\-\.](\d{1,2})[/\-\.](\d{1,2})',  # AAAA/MM/JJ (format ISO inversé)

            # === FORMATS AVEC ANNÉE COURTE ===
            r'(\d{1,2})[/\-\.](\d{1,2})[/\-\.](\d{2})',  # JJ/MM/AA, JJ-MM-AA, JJ.MM.AA
            r'(\d{1,2})\s+(\d{1,2})\s+(\d{2})',  # JJ MM AA

            # === FORMATS SANS ANNÉE (priorité aux plus spécifiques) ===
            r'(\d{1,2})[/\-\.](\d{1,2})(?:\s+[aà]\s+\d{1,2}[h:]?\d{0,2})',  # JJ/MM à 14h30
            r'(\d{1,2})[/\-\.](\d{1,2})(?=\s+[^\d/\-\.])',  # JJ/MM suivi d'un mot
            r'(\d{1,2})[/\-\.](\d{1,2})(?![/\-\.\d])',  # JJ/MM pas suivi de chiffres
            r'(\d{1,2})\s+(\d{1,2})(?!\s+\d{2,4})',  # JJ MM (pas suivi d'année)

            # === FORMATS TEXTUELS FRANÇAIS ===
            r'(\d{1,2})\s+(janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\s+(\d{4})',
            r'(\d{1,2})\s+(janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\s+(\d{2})',
            r'(\d{1,2})\s+(janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)(?!\s+\d)',
            r'(\d{1,2})\s+(jan|fév|mar|avr|mai|jun|jul|aoû|sep|oct|nov|déc)\.?\s+(\d{4})',
            r'(\d{1,2})\s+(jan|fév|mar|avr|mai|jun|jul|aoû|sep|oct|nov|déc)\.?(?!\s+\d)',

            # === FORMATS ANGLAIS ===
            r'(\d{1,2})\s+(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{4})',
            r'(\d{1,2})\s+(january|february|march|april|may|june|july|august|september|october|november|december)(?!\s+\d)',
            r'(\d{1,2})\s+(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\.?\s+(\d{4})',
            r'(\d{1,2})\s+(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\.?(?!\s+\d)',

            # === FORMATS AVEC MOTS-CLÉS ===
            r'le\s+(\d{1,2})[/\-\.](\d{1,2})(?:[/\-\.](\d{2,4}))?',  # "le 28/06" ou "le 28/06/2025"
            r'(\d{1,2})[/\-\.](\d{1,2})\s+prochain',  # "28/06 prochain"
            r'(\d{1,2})[/\-\.](\d{1,2})\s+à\s+',  # "28/06 à 14h30"
        ]

        # Dictionnaire pour convertir les mois textuels
        mois_mapping = {
            # Français
            'janvier': 1,
            'février': 2,
            'mars': 3,
            'avril': 4,
            'mai': 5,
            'juin': 6,
            'juillet': 7,
            'août': 8,
            'septembre': 9,
            'octobre': 10,
            'novembre': 11,
            'décembre': 12,
            'jan': 1,
            'fév': 2,
            'mar': 3,
            'avr': 4,
            'jun': 6,
            'jul': 7,
            'aoû': 8,
            'sep': 9,
            'oct': 10,
            'nov': 11,
            'déc': 12,
            # Anglais
            'january': 1,
            'february': 2,
            'march': 3,
            'april': 4,
            'may': 5,
            'june': 6,
            'july': 7,
            'august': 8,
            'september': 9,
            'october': 10,
            'november': 11,
            'december': 12,
            'jan': 1,
            'feb': 2,
            'mar': 3,
            'apr': 4,
            'jun': 6,
            'jul': 7,
            'aug': 8,
            'sep': 9,
            'oct': 10,
            'nov': 11,
            'dec': 12
        }

        for pattern in date_patterns:
            matches = re.finditer(pattern, text_clean, re.IGNORECASE)
            for match in matches:
                try:
                    groups = match.groups()
                    date_string_found = match.group(0)

                    # Identifier le type de format
                    if any(month in groups for month in mois_mapping.keys()):
                        # Format textuel avec nom de mois
                        jour = int(groups[0])
                        mois_text = groups[1].lower()
                        mois = mois_mapping.get(mois_text)
                        if not mois:
                            continue

                        if len(groups) >= 3 and groups[2]:
                            annee = int(groups[2])
                            if annee < 100:
                                annee = 2000 + annee if annee < 50 else 1900 + annee
                        else:
                            annee = self._determine_best_year(jour, mois, now)

                    elif pattern.startswith(r'(\d{4})'):
                        # Format AAAA/MM/JJ (ISO inversé)
                        annee = int(groups[0])
                        mois = int(groups[1])
                        jour = int(groups[2])

                    else:
                        # Format numérique standard JJ/MM[/AA[AA]]
                        jour = int(groups[0])
                        mois = int(groups[1])

                        if len(groups) >= 3 and groups[2]:
                            annee = int(groups[2])
                            if annee < 100:
                                annee = 2000 + annee if annee < 50 else 1900 + annee
                        else:
                            annee = self._determine_best_year(jour, mois, now)

                    # Validation des valeurs
                    if not (1 <= jour <= 31 and 1 <= mois <= 12):
                        continue

                    # Créer la date
                    quest_date = datetime(annee,
                                          mois,
                                          jour,
                                          tzinfo=timezone.utc)
                    return quest_date, date_string_found

                except (ValueError, IndexError) as e:
                    logger.debug(
                        f"Erreur parsing date '{match.group(0)}': {e}")
                    continue

        return None, None

    async def callback(self,
                       interaction: discord.Interaction,
                       membre: discord.Member = None):
        # Defer la réponse pour éviter le timeout
        await interaction.response.defer(ephemeral=True)

        cible = membre or interaction.user

        # Utiliser le système de canaux configurables
        channel = ChannelHelper.get_quetes_channel(interaction.guild)
        if not channel:
            error_msg = ChannelHelper.get_channel_error_message(
                ChannelHelper.QUETES)
            await interaction.followup.send(error_msg)
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
        resultats_passes = []
        resultats_sans_date = []

        for message in messages_avec_mention:
            premiere_ligne = message.content.split('\n', 1)[0].strip()
            message_url = f"https://discord.com/channels/{interaction.guild.id}/{channel.id}/{message.id}"

            # Extraire la date avec notre fonction ultra-complète
            quest_date, date_found = self._extract_date_from_text(
                message.content, now)

            if quest_date:
                jours_restants = (quest_date - now).days
                date_formatee = f"{quest_date.day:02d}/{quest_date.month:02d}/{quest_date.year}"

                if jours_restants >= 0 and jours_restants <= 90:
                    # Date future (0-90 jours)
                    if jours_restants == 0:
                        quand = "🔴 **AUJOURD'HUI**"
                    elif jours_restants == 1:
                        quand = "🟠 **Demain**"
                    elif jours_restants <= 3:
                        quand = f"🟡 Dans {jours_restants} jours"
                    elif jours_restants <= 7:
                        quand = f"🟢 Dans {jours_restants} jours"
                    elif jours_restants <= 14:
                        quand = f"🔵 Dans {jours_restants} jours"
                    else:
                        quand = f"⚪ Dans {jours_restants} jours"

                    resultats_futures.append({
                        'jours':
                        jours_restants,
                        'texte':
                        f"{quand} ({date_formatee})\n└─ [{premiere_ligne[:70]}{'...' if len(premiere_ligne) > 70 else ''}]({message_url})"
                    })

                elif jours_restants >= -60:  # Date passée récente (moins de 60 jours)
                    jours_passes = abs(jours_restants)
                    if jours_passes == 1:
                        quand = "🕰️ **Hier**"
                    elif jours_passes <= 7:
                        quand = f"🕰️ Il y a {jours_passes} jours"
                    elif jours_passes <= 30:
                        quand = f"🕰️ Il y a {jours_passes} jours"
                    else:
                        quand = f"🕰️ Il y a {jours_passes} jours"

                    resultats_passes.append({
                        'jours':
                        jours_restants,
                        'texte':
                        f"{quand} ({date_formatee})\n└─ [{premiere_ligne[:70]}{'...' if len(premiere_ligne) > 70 else ''}]({message_url})"
                    })

            else:
                # Aucune date détectable
                resultats_sans_date.append({
                    'texte': premiere_ligne[:100],
                    'url': message_url
                })

        # Trier les résultats
        resultats_futures.sort(key=lambda x: x['jours'])
        resultats_passes.sort(key=lambda x: x['jours'],
                              reverse=True)  # Plus récent en premier

        # Construire l'embed avec les 3 catégories
        embed = discord.Embed(title=f"📅 Quêtes - {cible.display_name}",
                              color=0x3498db)

        # 1. Quêtes futures
        if resultats_futures:
            desc_futures = "\n\n".join(
                [r['texte'] for r in resultats_futures[:6]])
            if len(resultats_futures) > 6:
                desc_futures += f"\n\n*... et {len(resultats_futures) - 6} autres*"

            embed.add_field(
                name=f"🎯 Quêtes à venir ({len(resultats_futures)})",
                value=desc_futures,
                inline=False)

        # 2. Quêtes passées récentes
        if resultats_passes:
            desc_passes = "\n\n".join(
                [r['texte'] for r in resultats_passes[:4]])
            if len(resultats_passes) > 4:
                desc_passes += f"\n\n*... et {len(resultats_passes) - 4} autres*"

            embed.add_field(
                name=f"🕰️ Quêtes récentes passées ({len(resultats_passes)})",
                value=desc_passes,
                inline=False)

        # 3. Mentions sans date détectable
        if resultats_sans_date:
            desc_sans_date = "\n".join([
                f"• [{item['texte'][:50]}{'...' if len(item['texte']) > 50 else ''}]({item['url']})"
                for item in resultats_sans_date[:5]
            ])
            if len(resultats_sans_date) > 5:
                desc_sans_date += f"\n*... et {len(resultats_sans_date) - 5} autres*"

            embed.add_field(
                name=
                f"📌 Mentions sans date détectable ({len(resultats_sans_date)})",
                value=desc_sans_date,
                inline=False)

        # Message si aucun résultat
        if not resultats_futures and not resultats_passes and not resultats_sans_date:
            embed.add_field(
                name="❌ Aucune mention trouvée",
                value=f"Aucune mention dans {channel.mention} sur 30 jours",
                inline=False)

        # Footer avec statistiques
        total_dates_detectees = len(resultats_futures) + len(resultats_passes)
        embed.set_footer(
            text=
            f"Analysé {messages_parcourus} messages | {len(messages_avec_mention)} mentions | {total_dates_detectees} dates détectées | Canal: #{channel.name}"
        )

        await interaction.followup.send(embed=embed)
