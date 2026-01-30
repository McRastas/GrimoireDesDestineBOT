"""
Commande Discord : /mesquetes [membre]

DESCRIPTION:
    Liste les quêtes futures où un joueur est mentionné dans le canal quêtes

FONCTIONNEMENT:
    - Paramètre optionnel : membre à rechercher (par défaut l'auteur)
    - Recherche dans le canal quêtes les messages des 30 derniers jours
    - Filtre uniquement les quêtes avec une date FUTURE
    - Supporte de nombreux formats de dates (flexibilité pour les MJ)

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

        LOGIQUE INTELLIGENTE :
        - Date future cette année → année actuelle
        - Date passée de moins de 30 jours → année actuelle (vraiment passée)
        - Date passée de plus de 30 jours → année prochaine (probablement futur)

        Exemple (si on est le 30/01/2026) :
        - "15/02" → 15/02/2026 (futur proche)
        - "15/01" → 15/01/2026 (passé de 15j, on garde cette année)
        - "15/12" → 15/12/2026 (passé de 46j, donc c'est l'année prochaine... non en fait futur)

        En fait : si passé de plus de 30j, c'est probablement l'année suivante
        """
        current_year = now.year
        seuil_jours_passes = 30  # Seuil pour considérer que c'est l'année suivante

        try:
            date_current_year = datetime(current_year, mois, jour, tzinfo=timezone.utc)
            days_diff = (date_current_year - now).days

            # Date future ou aujourd'hui → année actuelle
            if days_diff >= 0:
                return current_year

            # Date passée récemment (< 30 jours) → vraiment passée, année actuelle
            if days_diff >= -seuil_jours_passes:
                return current_year

            # Date passée de longtemps (> 30 jours) → probablement année prochaine
            return current_year + 1

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

        # Dictionnaire pour convertir les mois textuels (FR + EN)
        mois_mapping = {
            # Français complet
            'janvier': 1, 'février': 2, 'mars': 3, 'avril': 4,
            'mai': 5, 'juin': 6, 'juillet': 7, 'août': 8,
            'septembre': 9, 'octobre': 10, 'novembre': 11, 'décembre': 12,
            # Français abrégé
            'jan': 1, 'fév': 2, 'mar': 3, 'avr': 4,
            'jun': 6, 'jul': 7, 'aoû': 8,
            'sep': 9, 'oct': 10, 'nov': 11, 'déc': 12,
            # Anglais complet
            'january': 1, 'february': 2, 'march': 3, 'april': 4,
            'may': 5, 'june': 6, 'july': 7, 'august': 8,
            'september': 9, 'october': 10, 'november': 11, 'december': 12,
            # Anglais abrégé (uniquement ceux différents du français)
            'feb': 2, 'apr': 4, 'aug': 8, 'dec': 12
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

        # Analyser ces messages pour trouver des dates FUTURES uniquement
        quetes_futures = []

        for message in messages_avec_mention:
            premiere_ligne = message.content.split('\n', 1)[0].strip()
            message_url = f"https://discord.com/channels/{interaction.guild.id}/{channel.id}/{message.id}"

            # Extraire la date
            quest_date, date_found = self._extract_date_from_text(message.content, now)

            if quest_date:
                jours_restants = (quest_date - now).days
                date_formatee = f"{quest_date.day:02d}/{quest_date.month:02d}/{quest_date.year}"

                # Garder uniquement les dates futures (aujourd'hui inclus)
                if jours_restants >= 0:
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

                    quetes_futures.append({
                        'jours': jours_restants,
                        'date': date_formatee,
                        'quand': quand,
                        'titre': premiere_ligne[:70] + ('...' if len(premiere_ligne) > 70 else ''),
                        'url': message_url
                    })

        # Trier par date (plus proche en premier)
        quetes_futures.sort(key=lambda x: x['jours'])

        # Construire l'embed
        embed = discord.Embed(
            title=f"📅 Quêtes à venir - {cible.display_name}",
            color=0x3498db
        )

        if quetes_futures:
            # Afficher jusqu'à 10 quêtes futures
            for q in quetes_futures[:10]:
                embed.add_field(
                    name=f"{q['quand']} ({q['date']})",
                    value=f"[{q['titre']}]({q['url']})",
                    inline=False
                )

            if len(quetes_futures) > 10:
                embed.add_field(
                    name="",
                    value=f"*... et {len(quetes_futures) - 10} autres quêtes*",
                    inline=False
                )
        else:
            embed.add_field(
                name="Aucune quête future trouvée",
                value=f"Tu n'as pas de quête planifiée dans {channel.mention}",
                inline=False
            )

        # Footer avec statistiques
        embed.set_footer(
            text=f"📊 {messages_parcourus} messages analysés | {len(messages_avec_mention)} mentions | {len(quetes_futures)} quêtes futures"
        )

        await interaction.followup.send(embed=embed)
