# commands/pnj_generator.py
import discord
from discord import app_commands
from typing import Optional
import random
import logging
from .base import BaseCommand

logger = logging.getLogger(__name__)


class PnjGeneratorCommand(BaseCommand):
    """Générateur de PNJ avec format optimisé Roll20"""

    def __init__(self, bot):
        super().__init__(bot)

    @property
    def name(self) -> str:
        return "pnj-generator"

    @property
    def description(self) -> str:
        return "Génère un PNJ complet pour D&D avec format Roll20"

    def register(self, tree: app_commands.CommandTree):
        """Enregistrement de la commande avec option format Roll20"""

        @tree.command(name=self.name, description=self.description)
        @app_commands.describe(
            type_pnj="Type de PNJ à générer",
            genre="Genre du PNJ",
            race="Race du PNJ",
            format_roll20="Format optimisé pour Roll20 (recommandé)"
        )
        @app_commands.choices(type_pnj=[
            app_commands.Choice(name="🛡️ Garde", value="garde"),
            app_commands.Choice(name="💰 Marchand", value="marchand"),
            app_commands.Choice(name="👑 Noble", value="noble"),
            app_commands.Choice(name="🍺 Aubergiste", value="aubergiste"),
            app_commands.Choice(name="⛪ Prêtre", value="pretre"),
            app_commands.Choice(name="🗡️ Aventurier", value="aventurier"),
            app_commands.Choice(name="🔨 Artisan", value="artisan"),
            app_commands.Choice(name="🌾 Paysan", value="paysan"),
            app_commands.Choice(name="🗝️ Voleur", value="voleur"),
            app_commands.Choice(name="🔮 Mage", value="mage")
        ])
        @app_commands.choices(genre=[
            app_commands.Choice(name="♂️ Masculin", value="masculin"),
            app_commands.Choice(name="♀️ Féminin", value="feminin"),
            app_commands.Choice(name="🎲 Aléatoire", value="aleatoire")
        ])
        @app_commands.choices(race=[
            app_commands.Choice(name="👤 Humain", value="humain"),
            app_commands.Choice(name="🧝 Elfe", value="elfe"),
            app_commands.Choice(name="⚒️ Nain", value="nain"),
            app_commands.Choice(name="🌿 Halfelin", value="halfelin"),
            app_commands.Choice(name="🌙 Demi-Elfe", value="demi-elfe"),
            app_commands.Choice(name="😈 Tieffelin", value="tieffelin"),
            app_commands.Choice(name="🎲 Aléatoire", value="aleatoire")
        ])
        @app_commands.choices(format_roll20=[
            app_commands.Choice(name="✅ Roll20 (Recommandé)", value=True),
            app_commands.Choice(name="💬 Discord", value=False)
        ])
        async def pnj_generator_command(
            interaction: discord.Interaction,
            type_pnj: str,
            genre: str = "aleatoire",
            race: str = "aleatoire",
            format_roll20: bool = True
        ):
            await self.callback(interaction, type_pnj, genre, race, format_roll20)

    async def callback(self,
                       interaction: discord.Interaction,
                       type_pnj: str,
                       genre: str = "aleatoire",
                       race: str = "aleatoire",
                       format_roll20: bool = True):
        """Callback principal avec gestion des deux formats"""
        try:
            # Générer le PNJ
            pnj = self._generate_pnj(type_pnj, genre, race)

            # Choisir le format de sortie
            if format_roll20:
                content = self._format_pnj_for_roll20(pnj, type_pnj)
                embed_title = "🎭 PNJ Généré (Format Roll20)"
                instructions = (
                    "1. **Copiez** le texte ci-dessous\n"
                    "2. **Collez** dans les notes de votre fiche Roll20\n"
                    "3. **Adaptez** selon vos besoins de campagne"
                )
            else:
                content = self._format_pnj_discord(pnj, type_pnj)
                embed_title = "🎭 PNJ Généré (Format Discord)"
                instructions = (
                    "1. **Copiez** le contenu formaté\n"
                    "2. **Utilisez** directement dans Discord\n"
                    "3. **Modifiez** selon vos besoins"
                )

            # Créer l'embed d'information
            embed = discord.Embed(
                title=embed_title,
                description=f"**{pnj['nom']}** - {pnj['race']} {type_pnj.title()}",
                color=0x3498db
            )

            embed.add_field(
                name="👤 Aperçu",
                value=f"**Genre:** {pnj['genre'].title()}\n**Âge:** {pnj['age']} ans",
                inline=True
            )

            embed.add_field(
                name="🎭 Trait Principal",
                value=f"{pnj['personnalite']['trait_positif'].title()}",
                inline=True
            )

            embed.add_field(
                name="📋 Instructions",
                value=instructions,
                inline=False
            )

            # Vérifier la longueur et envoyer
            if len(content) > 1900:
                await self._send_long_content(interaction, content, embed)
            else:
                await interaction.response.send_message(embed=embed)
                if format_roll20:
                    await interaction.followup.send(f"```\n{content}\n```")
                else:
                    await interaction.followup.send(content)

        except Exception as e:
            logger.error(f"Erreur génération PNJ: {e}")
            await interaction.response.send_message(
                "❌ Erreur lors de la génération du PNJ. Veuillez réessayer.",
                ephemeral=True
            )

    def _format_pnj_for_roll20(self, pnj: dict, type_pnj: str) -> str:
        """Formate le PNJ pour Roll20 (texte brut)"""
        
        template = f"""=== PNJ GENEREE ===

NOM: {pnj['nom']}
RACE: {pnj['race']}
CLASSE/TYPE: {type_pnj.title()}
GENRE: {pnj['genre'].title()}
AGE: {pnj['age']} ans

--- APPARENCE ---
{pnj['apparence']}

--- PERSONNALITE ---
Trait Positif: {pnj['personnalite']['trait_positif'].title()}
Trait Negatif: {pnj['personnalite']['trait_negatif'].title()}
Manie: {pnj['personnalite']['maniere']}
Motivation: {pnj['personnalite']['motivation'].title()}

--- BACKGROUND ---
{self._format_professional_details_roll20(pnj['details'], type_pnj)}

--- ACCROCHE RP ---
{pnj['secret']}

--- NOTES MJ ---
[Espace libre pour notes personnalisees]

=== FIN PNJ ==="""
        
        return template.strip()

    def _format_pnj_discord(self, pnj: dict, type_pnj: str) -> str:
        """Formate le PNJ pour Discord (avec formatage)"""
        
        template = f"""** / ======================= PNJ ========================= \\ **

**📛 Nom :** {pnj['nom']}
**🎭 Type :** {type_pnj.title()}
**⚧️ Genre :** {pnj['genre'].title()}
**🧝 Race :** {pnj['race']}
**🎂 Âge :** {pnj['age']} ans

**👤 APPARENCE**
{pnj['apparence']}

**🧠 PERSONNALITÉ**
• **Trait positif :** {pnj['personnalite']['trait_positif'].title()}
• **Trait négatif :** {pnj['personnalite']['trait_negatif'].title()}
• **Manie :** {pnj['personnalite']['maniere']}
• **Motivation :** {pnj['personnalite']['motivation'].title()}

**💼 BACKGROUND**
{self._format_professional_details_discord(pnj['details'], type_pnj)}

**🎲 ACCROCHE RP**
{pnj['secret']}

** \\ ======================= PNJ ========================= / **

*PNJ généré automatiquement - Prêt à utiliser*"""
        
        return template.strip()

    def _format_professional_details_roll20(self, details: dict, type_pnj: str) -> str:
        """Formate les détails professionnels pour Roll20"""
        
        if type_pnj == "marchand":
            return f"""Specialite: {details.get('specialite', 'Marchandises générales')}
Richesse: {details.get('richesse', 'Modeste')}
Reputation: {details.get('reputation', 'Honnête')}
Experience: {details.get('info_extra', 'Établi depuis quelques années')}"""
        
        elif type_pnj == "noble":
            return f"""Titre: {details.get('titre', 'Lord/Lady')}
Domaine: {details.get('domaine', 'Terres agricoles')}
Influence: {details.get('influence', 'Locale')}
Lignee: {details.get('info_extra', 'Famille ancienne')}"""
        
        elif type_pnj == "garde":
            return f"""Rang: {details.get('rang', 'Simple garde')}
Experience: {details.get('experience', '5 ans de service')}
Specialite: {details.get('specialite', 'Patrouilles')}
Background: {details.get('info_extra', 'Natif de la région')}"""

elif type_pnj == "aubergiste":
            return f"""Etablissement: {details.get('etablissement', 'Auberge modeste')}
Reputation: {details.get('reputation', 'Accueillant')}
Specialite: {details.get('specialite_culinaire', 'Cuisine locale')}
Experience: {details.get('info_extra', 'Gérant depuis des années')}"""
        
        elif type_pnj == "pretre":
            return f"""Divinite: {details.get('divinite', 'Divinité majeure')}
Rang: {details.get('rang_clerical', 'Prêtre')}
Temple: {details.get('temple', 'Temple local')}
Devotion: {details.get('info_extra', 'Serviteur fidèle')}"""
        
        elif type_pnj == "aventurier":
            return f"""Classe: {details.get('classe', 'Guerrier')}
Niveau: {details.get('niveau_estime', 'Expérimenté')}
Specialite: {details.get('specialite', 'Exploration')}
Experience: {details.get('info_extra', 'Quelques années d\'aventure')}"""
        
        elif type_pnj == "artisan":
            return f"""Metier: {details.get('metier', 'Artisan')}
Reputation: {details.get('reputation', 'Respecté')}
Specialite: {details.get('specialite', 'Travail de qualité')}
Experience: {details.get('info_extra', 'Maîtrise son art')}"""
        
        elif type_pnj == "paysan":
            return f"""Activite: {details.get('activite', 'Agriculture')}
Statut: {details.get('statut', 'Propriétaire')}
Specialite: {details.get('specialite', 'Cultures variées')}
Experience: {details.get('info_extra', 'Travaille la terre')}"""
        
        elif type_pnj == "voleur":
            return f"""Specialite: {details.get('specialite', 'Vol à la tire')}
Reputation: {details.get('reputation', 'Discret')}
Territoire: {details.get('territoire', 'Quartiers populaires')}
Experience: {details.get('info_extra', 'Actif depuis peu')}"""
        
        elif type_pnj == "mage":
            return f"""Ecole: {details.get('ecole_magie', 'Évocation')}
Niveau: {details.get('niveau_estime', 'Apprenti')}
Specialite: {details.get('specialite', 'Sorts utilitaires')}
Experience: {details.get('info_extra', 'Étudie la magie')}"""
        
        else:
            return "Details a developper selon les besoins de la campagne"

    def _format_professional_details_discord(self, details: dict, type_pnj: str) -> str:
        """Formate les détails professionnels pour Discord"""
        
        if type_pnj == "marchand":
            return f"""• **Spécialité :** {details.get('specialite', 'Marchandises générales')}
• **Richesse :** {details.get('richesse', 'Modeste')}
• **Réputation :** {details.get('reputation', 'Honnête')}
• **Expérience :** {details.get('info_extra', 'Établi depuis quelques années')}"""
        
        elif type_pnj == "noble":
            return f"""• **Titre :** {details.get('titre', 'Lord/Lady')}
• **Domaine :** {details.get('domaine', 'Terres agricoles')}
• **Influence :** {details.get('influence', 'Locale')}
• **Lignée :** {details.get('info_extra', 'Famille ancienne')}"""
        
        elif type_pnj == "garde":
            return f"""• **Rang :** {details.get('rang', 'Simple garde')}
• **Expérience :** {details.get('experience', '5 ans de service')}
• **Spécialité :** {details.get('specialite', 'Patrouilles')}
• **Background :** {details.get('info_extra', 'Natif de la région')}"""
        
        elif type_pnj == "aubergiste":
            return f"""• **Établissement :** {details.get('etablissement', 'Auberge modeste')}
• **Réputation :** {details.get('reputation', 'Accueillant')}
• **Spécialité :** {details.get('specialite_culinaire', 'Cuisine locale')}
• **Expérience :** {details.get('info_extra', 'Gérant depuis des années')}"""
        
        elif type_pnj == "pretre":
            return f"""• **Divinité :** {details.get('divinite', 'Divinité majeure')}
• **Rang :** {details.get('rang_clerical', 'Prêtre')}
• **Temple :** {details.get('temple', 'Temple local')}
• **Dévotion :** {details.get('info_extra', 'Serviteur fidèle')}"""
        
        elif type_pnj == "aventurier":
            return f"""• **Classe :** {details.get('classe', 'Guerrier')}
• **Niveau :** {details.get('niveau_estime', 'Expérimenté')}
• **Spécialité :** {details.get('specialite', 'Exploration')}
• **Expérience :** {details.get('info_extra', 'Quelques années d\'aventure')}"""
        
        elif type_pnj == "artisan":
            return f"""• **Métier :** {details.get('metier', 'Artisan')}
• **Réputation :** {details.get('reputation', 'Respecté')}
• **Spécialité :** {details.get('specialite', 'Travail de qualité')}
• **Expérience :** {details.get('info_extra', 'Maîtrise son art')}"""
        
        elif type_pnj == "paysan":
            return f"""• **Activité :** {details.get('activite', 'Agriculture')}
• **Statut :** {details.get('statut', 'Propriétaire')}
• **Spécialité :** {details.get('specialite', 'Cultures variées')}
• **Expérience :** {details.get('info_extra', 'Travaille la terre')}"""
        
        elif type_pnj == "voleur":
            return f"""• **Spécialité :** {details.get('specialite', 'Vol à la tire')}
• **Réputation :** {details.get('reputation', 'Discret')}
• **Territoire :** {details.get('territoire', 'Quartiers populaires')}
• **Expérience :** {details.get('info_extra', 'Actif depuis peu')}"""
        
        elif type_pnj == "mage":
            return f"""• **École :** {details.get('ecole_magie', 'Évocation')}
• **Niveau :** {details.get('niveau_estime', 'Apprenti')}
• **Spécialité :** {details.get('specialite', 'Sorts utilitaires')}
• **Expérience :** {details.get('info_extra', 'Étudie la magie')}"""
        
        else:
            return "• **Détails :** À développer selon les besoins de la campagne"

            async def _send_long_content(self, interaction: discord.Interaction, content: str, embed: discord.Embed):
        """Envoie du contenu long en le divisant si nécessaire"""
        
        await interaction.response.send_message(embed=embed)
        
        # Diviser le contenu si trop long
        if len(content) > 1900:
            parts = []
            lines = content.split('\n')
            current_part = ""
            
            for line in lines:
                if len(current_part) + len(line) + 1 > 1900:
                    if current_part:
                        parts.append(current_part)
                    current_part = line
                else:
                    current_part += ("\n" if current_part else "") + line
            
            if current_part:
                parts.append(current_part)
            
            for i, part in enumerate(parts):
                await interaction.followup.send(f"```\n{part}\n```")
        else:
            await interaction.followup.send(f"```\n{content}\n```")

    def _generate_pnj(self, type_pnj: str, genre: str, race: str) -> dict:
        """Génère un PNJ complet"""

        # Déterminer le genre
        if genre == "aleatoire":
            genre = random.choice(["masculin", "feminin"])

        # Déterminer la race
        if race == "aleatoire":
            race = random.choice([
                "humain", "elfe", "nain", "halfelin", "demi-elfe", "tieffelin"
            ])

        # Générer le nom
        nom = self._generate_name(race, genre)

        # Générer l'apparence
        apparence = self._generate_appearance(race, genre)

        # Générer la personnalité
        personnalite = self._generate_personality()

        # Générer les détails selon le type
        details = self._generate_type_details(type_pnj)

        # Générer un secret/accroche
        secret = self._generate_secret(type_pnj)

        return {
            "nom": nom,
            "race": race.title(),
            "genre": genre,
            "apparence": apparence,
            "personnalite": personnalite,
            "details": details,
            "secret": secret,
            "age": self._generate_age(race)
        }

    def _generate_name(self, race: str, genre: str) -> str:
        """Génère un nom selon la race et le genre"""

        names_data = {
            "humain": {
                "masculin": [
                    "Aldric", "Bran", "Cedric", "Dorian", "Elias", "Finn",
                    "Gareth", "Henri", "Ivan", "Jasper", "Klaus", "Leon",
                    "Magnus", "Nolan", "Oscar", "Pavel", "Quinn", "Roland",
                    "Stefan", "Tristan", "Ulric", "Victor", "Willem", "Xavier"
                ],
                "feminin": [
                    "Aria", "Beatrice", "Celeste", "Diana", "Elena", "Fiona",
                    "Gwen", "Helena", "Iris", "Juliet", "Kira", "Luna",
                    "Mira", "Nora", "Olivia", "Petra", "Quinn", "Rosa",
                    "Stella", "Tara", "Uma", "Vera", "Willa", "Xara"
                ]
            },
            "elfe": {
                "masculin": [
                    "Aelar", "Berrian", "Dayereth", "Enna", "Galinndan",
                    "Hadarai", "Lamlis", "Mindartis", "Naal", "Nutae",
                    "Paelynn", "Peren", "Quarion", "Riardon", "Rolen",
                    "Silvyr", "Suhnaal", "Thamior", "Theren", "Theriatis"
                ],
                "feminin": [
                    "Adrie", "Birel", "Caelynn", "Dara", "Enna", "Galinndan",
                    "Hadarai", "Immeral", "Ivellios", "Korfel", "Lamlis",
                    "Mindartis", "Naal", "Nutae", "Paelynn", "Peren",
                    "Quarion", "Riardon", "Rolen", "Silvyr"
                ]
            },
            "nain": {
                "masculin": [
                    "Adrik", "Baern", "Darrak", "Eberk", "Fargrim", "Gardain",
                    "Harbek", "Kildrak", "Morgran", "Orsik", "Rangrim",
                    "Taklinn", "Thorek", "Travok", "Ulfgar", "Vondal",
                    "Balin", "Dwalin", "Oin", "Gloin"
                ]

                "feminin": [
                    "Amber", "Bardryn", "Diesa", "Eldeth", "Gunnloda",
                    "Gwyn", "Helja", "Hlin", "Kathra", "Kristryd",
                    "Ilde", "Liftrasa", "Mardred", "Riswynn", "Sannl",
                    "Torbera", "Torgga", "Vistra"
                ]
            },
            "halfelin": {
                "masculin": [
                    "Alton", "Ander", "Bernie", "Bobbin", "Cade", "Callus",
                    "Corrin", "Dannad", "Dinodas", "Eberk", "Finnan",
                    "Garret", "Lindal", "Lyle", "Merric", "Milo",
                    "Osborn", "Perrin", "Reed", "Roscoe", "Wellby"
                ],
                "feminin": [
                    "Andry", "Bree", "Callie", "Cora", "Euphemia", "Jillian",
                    "Kithri", "Lavinia", "Lidda", "Merla", "Nedda",
                    "Paela", "Portia", "Seraphina", "Shaena", "Trym",
                    "Vani", "Verna", "Celandine", "Amaryllis"
                ]
            },
            "demi-elfe": {
                "masculin": [
                    "Abel", "Aramil", "Arannis", "Berrian", "Cithreth",
                    "Dayereth", "Drannor", "Enna", "Galinndan", "Hadarai",
                    "Heian", "Himo", "Immeral", "Ivellios", "Korfel",
                    "Lamlis", "Laucian", "Mindartis", "Naal", "Nutae"
                ],
                "feminin": [
                    "Adrie", "Althaea", "Anastrianna", "Andraste", "Antinua",
                    "Bethrynna", "Birel", "Caelynn", "Dara", "Enna",
                    "Galinndan", "Hadarai", "Halimath", "Heian", "Himo",
                    "Immeral", "Ivellios", "Korfel", "Lamlis", "Laucian"
                ]
            },
            "tieffelin": {
                "masculin": [
                    "Akmenos", "Amnon", "Barakas", "Damakos", "Ekemon",
                    "Iados", "Kairon", "Leucis", "Melech", "Mordai",
                    "Morthos", "Pelaios", "Skamos", "Therai", "Valeth",
                    "Verin", "Zeth", "Amon", "Andram", "Astaroth"
                ],
                "feminin": [
                    "Akta", "Anakir", "Bryseis", "Criella", "Damaia",
                    "Ea", "Kallista", "Lerissa", "Makaria", "Nemeia",
                    "Orianna", "Phelaia", "Rieta", "Ronassah", "Seraphina",
                    "Valeria", "Vellynne", "Xara", "Yalda", "Zariel"
                ]
            }
        }

        race_names = names_data.get(race, names_data["humain"])
        gender_names = race_names.get(genre, race_names["masculin"])
        
        return random.choice(gender_names)

    def _generate_appearance(self, race: str, genre: str) -> str:
        """Génère l'apparence selon la race et le genre"""

        tailles = {
            "humain": ["grand", "moyen", "petit"],
            "elfe": ["élancé", "gracieux", "svelte"],
            "nain": ["trapu", "robuste", "costaud"],
            "halfelin": ["petit", "menu", "délicat"],
            "demi-elfe": ["grand", "élancé", "gracieux"],
            "tieffelin": ["imposant", "élancé", "mystérieux"]
        }

        cheveux = [
            "noirs", "bruns", "châtains", "blonds", "roux", "gris", "blancs",
            "argentés", "cuivrés"
        ]

        yeux = [
            "noirs", "bruns", "verts", "bleus", "gris", "noisette", "dorés",
            "violets", "rouges"
        ]

        distinctifs = [
            "une cicatrice sur la joue