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
        
        else:
            return "Détails à développer selon les besoins de la campagne"

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
                if i == 0:
                    await interaction.followup.send(f"```\n{part}\n```")
                else:
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
                ],
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
            "une cicatrice sur la joue", "une dent en or", "un tatouage tribal",
            "une bague ornée", "une amulette", "une cape colorée",
            "des bijoux voyants", "un chapeau distinctif", "une canne sculptée",
            "une sacoche en cuir", "des gants élégants", "une épingle à cheveux"
        ]

        taille = random.choice(tailles.get(race, tailles["humain"]))
        cheveux_desc = random.choice(cheveux)
        yeux_desc = random.choice(yeux)
        distinctif = random.choice(distinctifs)

        # Gérer les spécificités raciales
        if race == "nain" and genre == "masculin":
            barbes = ["courte et soignée", "longue et tressée", "épaisse et grise", "rousse et fournie"]
            barbe_desc = random.choice(barbes)
            return f"{taille.title()}, aux cheveux {cheveux_desc} et aux yeux {yeux_desc}. Porte {barbe_desc} et a {distinctif}."
        else:
            return f"{taille.title()}, aux cheveux {cheveux_desc} et aux yeux {yeux_desc}. A {distinctif}."

    def _generate_personality(self) -> dict:
        """Génère les traits de personnalité"""

        traits_positifs = [
            "généreux", "courageux", "loyal", "intelligent", "charismatique",
            "patient", "déterminé", "honnête", "compassionnel", "humble"
        ]

        traits_negatifs = [
            "cupide", "impatient", "têtu", "arrogant", "méfiant", "paresseux",
            "bavard", "pessimiste", "jaloux", "colérique"
        ]

        manieres = [
            "se gratte le nez quand il ment",
            "tapote des doigts quand il réfléchit", "cligne beaucoup des yeux",
            "se penche en avant pour écouter", "croise toujours les bras",
            "sourit trop souvent", "baisse la voix pour les secrets",
            "regarde toujours par-dessus l'épaule"
        ]

        motivations = [
            "protéger sa famille", "devenir riche", "se venger d'un ennemi",
            "découvrir la vérité sur son passé", "aider les plus démunis",
            "atteindre la reconnaissance", "préserver une tradition",
            "explorer de nouveaux horizons"
        ]

        return {
            "trait_positif": random.choice(traits_positifs),
            "trait_negatif": random.choice(traits_negatifs),
            "maniere": random.choice(manieres),
            "motivation": random.choice(motivations)
        }

    def _generate_type_details(self, type_pnj: str) -> dict:
        """Génère les détails spécifiques au type de PNJ"""

        details_by_type = {
            "marchand": {
                "specialite": random.choice([
                    "armes et armures", "potions et herbes", "bijoux précieux",
                    "équipement d'aventurier", "nourriture exotique",
                    "livres rares"
                ]),
                "richesse": random.choice(
                    ["prospère", "modeste", "en difficulté", "très riche"]),
                "reputation": random.choice([
                    "honnête", "de confiance", "un peu louche",
                    "réputé pour ses prix"
                ]),
                "info_extra": "Tient boutique depuis " + str(random.randint(5, 30)) + " ans"
            },
            "noble": {
                "titre": random.choice([
                    "Lord/Lady", "Baron/Baronne", "Comte/Comtesse",
                    "Duc/Duchesse"
                ]),
                "domaine": random.choice([
                    "terres agricoles", "mines d'or", "vignobles", "forêts",
                    "ports commerciaux"
                ]),
                "influence": random.choice(
                    ["locale", "régionale", "courtisane", "militaire"]),
                "info_extra": "Famille noble depuis " + str(random.randint(3, 12)) + " générations"
            },
            "garde": {
                "rang": random.choice(
                    ["simple garde", "sergent", "capitaine", "lieutenant"]),
                "experience": str(random.randint(2, 20)) + " ans de service",
                "specialite": random.choice(
                    ["patrouilles", "enquêtes", "formation", "garde du corps"]),
                "info_extra": random.choice([
                    "ancien soldat", "natif de la ville", "recruté récemment"
                ])
            },
            "aubergiste": {
                "etablissement": random.choice([
                    "auberge de luxe", "taverne populaire", "relais de voyageurs",
                    "gîte familial"
                ]),
                "reputation": random.choice([
                    "accueillant", "discret", "convivial", "respecté"
                ]),
                "specialite_culinaire": random.choice([
                    "ragoûts copieux", "pâtisseries", "bières locales",
                    "cuisine régionale"
                ]),
                "info_extra": "Gérant depuis " + str(random.randint(3, 25)) + " ans"
            },
            "pretre": {
                "divinite": random.choice([
                    "Tyr", "Helm", "Lathander", "Selûne", "Tempus",
                    "Mystra", "Oghma", "Torm"
                ]),
                "rang_clerical": random.choice([
                    "acolyte", "prêtre", "grand prêtre", "chapelain"
                ]),
                "temple": random.choice([
                    "temple principal", "chapelle locale", "sanctuaire",
                    "monastère"
                ]),
                "info_extra": "Servant fidèle depuis " + str(random.randint(5, 30)) + " ans"
            },
            "aventurier": {
                "classe": random.choice([
                    "guerrier", "rôdeur", "roublard", "mage", "clerc"
                ]),
                "niveau_estime": random.choice([
                    "débutant", "expérimenté", "vétéran", "légendaire"
                ]),
                "specialite": random.choice([
                    "exploration de donjons", "chasse aux monstres",
                    "escorte de caravanes", "missions diplomatiques"
                ]),
                "info_extra": "Aventurier depuis " + str(random.randint(1, 15)) + " ans"
            },
            "artisan": {
                "metier": random.choice([
                    "forgeron", "menuisier", "tisserand", "potier",
                    "bijoutier", "cordonnier", "tailleur", "boulanger"
                ]),
                "reputation": random.choice([
                    "maître artisan", "apprenti talentueux", "créateur renommé",
                    "artisan respecté"
                ]),
                "specialite": random.choice([
                    "travail de précision", "créations uniques",
                    "réparations rapides", "commandes spéciales"
                ]),
                "info_extra": "Pratique son art depuis " + str(random.randint(3, 25)) + " ans"
            },
            "paysan": {
                "activite": random.choice([
                    "agriculture", "élevage", "viticulture", "apiculture",
                    "maraîchage", "sylviculture"
                ]),
                "statut": random.choice([
                    "propriétaire", "fermier", "métayer", "ouvrier agricole"
                ]),
                "specialite": random.choice([
                    "cultures céréalières", "légumes", "fruits", "bétail",
                    "produits laitiers", "miel et cire"
                ]),
                "info_extra": "Travaille la terre depuis " + str(random.randint(5, 40)) + " ans"
            },
            "voleur": {
                "specialite": random.choice([
                    "pickpocket", "cambrioleur", "escroc", "contrebandier",
                    "receleur", "assassin"
                ]),
                "reputation": random.choice([
                    "discret et efficace", "audacieux", "dangereux",
                    "mystérieux", "recherché"
                ]),
                "territoire": random.choice([
                    "quartiers riches", "docks", "marché", "routes commerciales",
                    "tavernes", "arrière-cours"
                ]),
                "info_extra": "Actif dans le milieu depuis " + str(random.randint(2, 20)) + " ans"
            },
            "mage": {
                "ecole_magie": random.choice([
                    "évocation", "illusion", "enchantement", "divination",
                    "nécromancie", "transmutation", "abjuration", "invocation"
                ]),
                "niveau_estime": random.choice([
                    "apprenti", "magicien confirmé", "maître", "archimage"
                ]),
                "specialite": random.choice([
                    "recherche théorique", "création d'objets magiques",
                    "sorts de combat", "sorts utilitaires", "rituels anciens"
                ]),
                "info_extra": "Étudie la magie depuis " + str(random.randint(5, 35)) + " ans"
            }
        }

        return details_by_type.get(type_pnj, {
            "profession": type_pnj.title(),
            "experience": "Quelques années",
            "reputation": "Correcte",
            "info_extra": "Détails à développer"
        })

    def _generate_secret(self, type_pnj: str) -> str:
        """Génère un secret ou une accroche RP"""

        secrets_generaux = [
            "Cache une dette importante envers la guilde des voleurs",
            "Recherche secrètement des informations sur un parent disparu",
            "Possède un objet magique dont il ignore la nature",
            "Est en réalité d'origine noble mais a fui sa famille",
            "Connaît l'emplacement d'un trésor caché",
            "A été témoin d'un crime important",
            "Entretient une correspondance secrète avec quelqu'un",
            "Cache une peur profonde des créatures magiques",
            "Possède des talents cachés en magie",
            "Est membre secret d'une organisation"
        ]

        secrets_by_type = {
            "marchand": [
                "Vend parfois des objets volés sans le savoir",
                "Finance secrètement un groupe d'aventuriers",
                "Cache une fortune dans un endroit secret",
                "A des accords avec des contrebandiers",
                "Collectionne des objets magiques rares",
                "Cherche à racheter les dettes de sa famille"
            ],
            "noble": [
                "Sa fortune familiale provient d'activités douteuses",
                "Entretient une liaison secrète avec un roturier",
                "Soutient en secret la rébellion contre le roi",
                "N'est pas le véritable héritier du titre",
                "Finance une organisation caritative secrète",
                "Cherche à venger un membre de sa famille"
            ],
            "garde": [
                "Ferme les yeux sur certaines activités illégales contre paiement",
                "Enquête secrètement sur la corruption dans ses rangs",
                "Protège quelqu'un en secret",
                "A laissé s'échapper un criminel volontairement",
                "Collecte des preuves contre son supérieur",
                "Ancien criminel reconverti"
            ],
            "aubergiste": [
                "Son établissement sert de planque à des contrebandiers",
                "Cache des messages secrets pour une organisation",
                "Connaît tous les ragots de la ville",
                "Protège un fugitif dans ses caves",
                "Ancien aventurier qui a raccroché",
                "Sa cuisine contient un ingrédient magique secret"
            ],
            "pretre": [
                "Doute secrètement de sa foi",
                "Utilise la magie divine à des fins personnelles",
                "Cache un passé de pécheur repenti",
                "Possède des textes religieux interdits",
                "Mène une double vie la nuit",
                "Cherche à exposer la corruption dans son temple"
            ],
            "aventurier": [
                "Fuit une malédiction qui le poursuit",
                "Recherche un artefact légendaire",
                "A trahi ses anciens compagnons",
                "Cache sa véritable identité",
                "Possède une carte de donjon secret",
                "Est le dernier survivant de son groupe"
            ],
            "artisan": [
                "Ses créations cachent des messages secrets",
                "Utilise des matériaux d'origine douteuse",
                "Fabrique des objets pour la pègre",
                "Cache un talent pour la magie des objets",
                "Cherche à recréer une technique perdue",
                "Ses outils sont en réalité magiques"
            ],
            "paysan": [
                "Ses terres cachent un ancien tombeau",
                "Cultive des plantes magiques en secret",
                "Fait de la contrebande avec ses récoltes",
                "A découvert un filon de métal précieux",
                "Protège une créature magique blessée",
                "Ancien soldat qui a déserté"
            ],
            "voleur": [
                "Prépare un coup majeur depuis des mois",
                "Travaille pour deux organisations rivales",
                "Cherche à venger un proche assassiné",
                "Possède des informations compromettantes sur un noble",
                "Cache son butin dans un endroit secret",
                "Ancien garde tombé dans la criminalité"
            ],
            "mage": [
                "Expérimente avec de la magie interdite",
                "Cherche un moyen de prolonger sa vie",
                "Ses recherches ont attiré l'attention d'entités dangereuses",
                "Cache un familier inhabituel",
                "Possède un grimoire volé",
                "Mène des expériences sur les morts-vivants"
            ]
        }

        type_secrets = secrets_by_type.get(type_pnj, secrets_generaux)
        all_secrets = secrets_generaux + type_secrets

        return random.choice(all_secrets)

    def _generate_age(self, race: str) -> int:
        """Génère un âge approprié selon la race"""

        age_ranges = {
            "humain": (18, 70),
            "elfe": (100, 500),
            "nain": (40, 250),
            "halfelin": (20, 100),
            "demi-elfe": (25, 150),
            "tieffelin": (18, 80)
        }

        min_age, max_age = age_ranges.get(race, (18, 70))
        return random.randint(min_age, max_age)

    def _create_pnj_embed(self, pnj: dict, type_pnj: str) -> discord.Embed:
        """Crée un embed Discord pour afficher le PNJ (ancienne version - gardée pour compatibilité)"""
        
        embed = discord.Embed(
            title=f"🎭 {pnj['nom']}",
            description=f"**{pnj['race']} {type_pnj.title()}** ({pnj['genre']})",
            color=0x3498db
        )

        # Apparence
        embed.add_field(
            name="👤 Apparence",
            value=pnj['apparence'],
            inline=False
        )

        # Personnalité
        personnalite_text = (
            f"**Positif:** {pnj['personnalite']['trait_positif'].title()}\n"
            f"**Négatif:** {pnj['personnalite']['trait_negatif'].title()}\n"
            f"**Manie:** {pnj['personnalite']['maniere']}\n"
            f"**Motivation:** {pnj['personnalite']['motivation'].title()}"
        )
        embed.add_field(
            name="🧠 Personnalité",
            value=personnalite_text,
            inline=True
        )

        # Détails professionnels
        details = pnj['details']
        if type_pnj == "marchand":
            details_text = (
                f"**Spécialité:** {details.get('specialite', 'N/A')}\n"
                f"**Richesse:** {details.get('richesse', 'N/A')}\n"
                f"**Réputation:** {details.get('reputation', 'N/A')}"
            )
        elif type_pnj == "noble":
            details_text = (
                f"**Titre:** {details.get('titre', 'N/A')}\n"
                f"**Domaine:** {details.get('domaine', 'N/A')}\n"
                f"**Influence:** {details.get('influence', 'N/A')}"
            )
        else:
            details_text = "Détails spécifiques au type"

        embed.add_field(
            name="💼 Détails",
            value=details_text,
            inline=True
        )

        # Secret/Accroche
        embed.add_field(
            name="🎲 Accroche RP",
            value=pnj['secret'],
            inline=False
        )

        embed.set_footer(text=f"Âge: {pnj['age']} ans")
        embed.timestamp = discord.utils.utcnow()

        return embed
            "