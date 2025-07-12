# commands/pnj_generator.py
import discord
from discord import app_commands
import random
from .base import BaseCommand


class PnjGeneratorCommand(BaseCommand):

    @property
    def name(self) -> str:
        return "pnj-generator"

    @property
    def description(self) -> str:
        return "Génère un PNJ aléatoire selon le type spécifié"

    def register(self, tree: app_commands.CommandTree):
        """Enregistrement avec choix prédéfinis"""

        @tree.command(name=self.name, description=self.description)
        @app_commands.describe(type_pnj="Type de PNJ à générer",
                               genre="Genre du PNJ (optionnel)",
                               race="Race du PNJ (optionnel)")
        @app_commands.choices(type_pnj=[
            app_commands.Choice(name="Marchand", value="marchand"),
            app_commands.Choice(name="Noble", value="noble"),
            app_commands.Choice(name="Garde", value="garde"),
            app_commands.Choice(name="Aubergiste", value="aubergiste"),
            app_commands.Choice(name="Prêtre", value="pretre"),
            app_commands.Choice(name="Voleur", value="voleur"),
            app_commands.Choice(name="Artisan", value="artisan"),
            app_commands.Choice(name="Paysan", value="paysan"),
            app_commands.Choice(name="Aventurier", value="aventurier"),
            app_commands.Choice(name="Mage", value="mage")
        ])
        @app_commands.choices(genre=[
            app_commands.Choice(name="Masculin", value="masculin"),
            app_commands.Choice(name="Féminin", value="feminin"),
            app_commands.Choice(name="Aléatoire", value="aleatoire")
        ])
        @app_commands.choices(race=[
            app_commands.Choice(name="Humain", value="humain"),
            app_commands.Choice(name="Elfe", value="elfe"),
            app_commands.Choice(name="Nain", value="nain"),
            app_commands.Choice(name="Halfelin", value="halfelin"),
            app_commands.Choice(name="Halfelin", value="halfelin"),
            app_commands.Choice(name="Demi-Elfe", value="demi-elfe"),
            app_commands.Choice(name="Tieffelin", value="tieffelin"),
            app_commands.Choice(name="Aléatoire", value="aleatoire")
        ])
        async def pnj_generator_command(interaction: discord.Interaction,
                                        type_pnj: str,
                                        genre: str = "aleatoire",
                                        race: str = "aleatoire"):
            await self.callback(interaction, type_pnj, genre, race)

    async def callback(self,
                       interaction: discord.Interaction,
                       type_pnj: str,
                       genre: str = "aleatoire",
                       race: str = "aleatoire"):
        # Générer le PNJ
        pnj = self._generate_pnj(type_pnj, genre, race)

        # Créer l'embed
        embed = self._create_pnj_embed(pnj, type_pnj)

        await interaction.response.send_message(embed=embed, ephemeral=True)

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
                    "Gareth", "Hugo", "Ivan", "Jasper"
                ],
                "feminin": [
                    "Aria", "Bella", "Clara", "Diana", "Elena", "Fiona",
                    "Grace", "Helena", "Iris", "Julia"
                ]
            },
            "elfe": {
                "masculin": [
                    "Aelar", "Berrian", "Dayereth", "Enna", "Galinndan",
                    "Heian", "Himo", "Immeral", "Ivellios", "Laucian"
                ],
                "feminin": [
                    "Adrie", "Althaea", "Anastrianna", "Andraste", "Antinua",
                    "Bethrynna", "Birel", "Caelynn", "Dara", "Enna"
                ]
            },
            "nain": {
                "masculin": [
                    "Adrik", "Baern", "Darrak", "Eberk", "Fargrim", "Gardain",
                    "Harbek", "Kildrak", "Morgran", "Orsik"
                ],
                "feminin": [
                    "Amber", "Bardryn", "Diesa", "Eldeth", "Gunnloda", "Helja",
                    "Hlin", "Kathra", "Kristryd", "Ilde"
                ]
            },
            "halfelin": {
                "masculin": [
                    "Alton", "Ander", "Bernie", "Bobbin", "Cade", "Callus",
                    "Corrin", "Dannad", "Danniel", "Eddie"
                ],
                "feminin": [
                    "Andry", "Bree", "Callie", "Chenna", "Dee", "Enna",
                    "Georgie", "Gynnie", "Harriet", "Jasmal"
                ]
            },
            "demi-elfe": {
                "masculin": [
                    "Abel", "Aramil", "Aranck", "Berrian", "Cithreth",
                    "Drannor", "Enna", "Galinndan", "Hadarai", "Halimath"
                ],
                "feminin": [
                    "Arara", "Beryl", "Caelynn", "Dara", "Enna", "Hadarai",
                    "Immeral", "Ivellios", "Korfel", "Lamlis"
                ]
            },
            "tieffelin": {
                "masculin": [
                    "Akmenos", "Amnon", "Barakas", "Damakos", "Ekemon",
                    "Iados", "Kairon", "Leucis", "Melech", "Mordai"
                ],
                "feminin": [
                    "Akta", "Anakir", "Bryseis", "Criella", "Damaia", "Ea",
                    "Kallista", "Lerissa", "Makaria", "Nemeia"
                ]
            }
        }

        if race in names_data and genre in names_data[race]:
            return random.choice(names_data[race][genre])
        else:
            return random.choice(names_data["humain"][genre])

    def _generate_appearance(self, race: str, genre: str) -> str:
        """Génère l'apparence physique"""

        # Traits généraux
        taille_traits = {
            "humain": ["de taille moyenne", "plutôt grand", "plutôt petit"],
            "elfe": ["élancé", "gracieux", "de grande taille"],
            "nain": ["trapu", "robuste", "de petite taille mais solide"],
            "halfelin": ["petit", "rond", "agile malgré sa petite taille"],
            "demi-elfe": ["de taille moyenne", "aux traits fins", "élégant"],
            "tieffelin": ["imposant", "aux traits marqués", "mystérieux"]
        }

        couleur_cheveux = [
            "blonds", "bruns", "noirs", "châtains", "roux", "gris", "blancs"
        ]
        couleur_yeux = ["bleus", "verts", "bruns", "noisette", "gris", "noirs"]

        if race == "elfe":
            couleur_yeux.extend(["dorés", "argentés"])
        elif race == "tieffelin":
            couleur_yeux.extend(["rouges", "dorés", "violets"])

        signes_distinctifs = [
            "une cicatrice sur le visage", "des tatouages tribaux",
            "un grain de beauté distinctif", "une barbe bien taillée",
            "des bijoux voyants", "une démarche particulière",
            "des vêtements colorés", "une voix grave", "des mains calleuses",
            "un sourire éclatant", "des rides de sourire", "une posture droite"
        ]

        taille = random.choice(taille_traits.get(race,
                                                 taille_traits["humain"]))
        cheveux = random.choice(couleur_cheveux)
        yeux = random.choice(couleur_yeux)
        distinctif = random.choice(signes_distinctifs)

        if race == "nain" and genre == "masculin":
            barbe_desc = random.choice([
                "une barbe fournie", "une barbe tressée",
                "une barbe grisonnante", "une barbe rousse"
            ])
            return f"{taille.title()}, aux cheveux {cheveux} et aux yeux {yeux}. Porte {barbe_desc} et a {distinctif}."
        else:
            return f"{taille.title()}, aux cheveux {cheveux} et aux yeux {yeux}. A {distinctif}."

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
                "specialite":
                random.choice([
                    "armes et armures", "potions et herbes", "bijoux précieux",
                    "équipement d'aventurier", "nourriture exotique",
                    "livres rares"
                ]),
                "richesse":
                random.choice(
                    ["prospère", "modeste", "en difficulté", "très riche"]),
                "reputation":
                random.choice([
                    "honnête", "de confiance", "un peu louche",
                    "réputé pour ses prix"
                ]),
                "info_extra":
                "Tient boutique depuis " + str(random.randint(5, 30)) + " ans"
            },
            "noble": {
                "titre":
                random.choice([
                    "Lord/Lady", "Baron/Baronne", "Comte/Comtesse",
                    "Duc/Duchesse"
                ]),
                "domaine":
                random.choice([
                    "terres agricoles", "mines d'or", "vignobles", "forêts",
                    "ports commerciaux"
                ]),
                "influence":
                random.choice(
                    ["locale", "régionale", "courtisane", "militaire"]),
                "info_extra":
                "Famille noble depuis " + str(random.randint(3, 12)) +
                " générations"
            },
            "garde": {
                "rang":
                random.choice(
                    ["simple garde", "sergent", "capitaine", "lieutenant"]),
                "experience":
                str(random.randint(2, 20)) + " ans de service",
                "specialite":
                random.choice(
                    ["patrouilles", "enquêtes", "formation",
                     "garde du corps"]),
                "info_extra":
                random.choice([
                    "ancien soldat", "natif de la ville", "recruté récemment"
                ])
            },
            "aubergiste": {
                "etablissement":
                random.choice([
                    "auberge de luxe", "taverne populaire", "gîte modeste",
                    "relais de poste"
                ]),
                "specialite_cuisine":
                random.choice([
                    "ragoûts copieux", "pain frais", "bières locales",
                    "mets exotiques"
                ]),
                "clientele":
                random.choice(
                    ["voyageurs", "locaux", "marchands", "aventuriers"]),
                "info_extra":
                "Tient l'établissement depuis " + str(random.randint(5, 25)) +
                " ans"
            },
            "pretre": {
                "divinite":
                random.choice(
                    ["Tyr", "Pelor", "Bahamut", "Sélûne", "Kelemvor",
                     "Oghma"]),
                "rang":
                random.choice(["acolyte", "prêtre", "grand prêtre", "abbé"]),
                "specialite":
                random.choice([
                    "guérison", "conseil spirituel", "rites funéraires",
                    "bénédictions"
                ]),
                "info_extra":
                "Voué à sa divinité depuis " + str(random.randint(5, 30)) +
                " ans"
            }
            # Ajouter les autres types...
        }

        return details_by_type.get(
            type_pnj, {
                "profession":
                type_pnj,
                "experience":
                str(random.randint(1, 20)) + " ans d'expérience",
                "reputation":
                random.choice(["bonne", "mitigée", "excellente", "douteuse"]),
                "info_extra":
                "Pratique son métier dans la région"
            })

    def _generate_secret(self, type_pnj: str) -> str:
        """Génère un secret ou une accroche pour le roleplay"""

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
                "A des accords avec des contrebandiers"
            ],
            "noble": [
                "Sa fortune familiale provient d'activités douteuses",
                "Entretient une liaison secrète avec un roturier",
                "Soutient en secret la rébellion contre le roi",
                "N'est pas le véritable héritier du titre"
            ],
            "garde": [
                "Ferme les yeux sur certaines activités illégales contre paiement",
                "Enquête secrètement sur la corruption dans ses rangs",
                "Protège quelqu'un en secret",
                "A laissé s'échapper un criminel volontairement"
            ]
        }

        type_secrets = secrets_by_type.get(type_pnj, secrets_generaux)
        all_secrets = secrets_generaux + type_secrets

        return random.choice(all_secrets)

    def _generate_age(self, race: str) -> int:
        """Génère un âge approprié selon la race"""

        age_ranges = {
            "humain": (20, 70),
            "elfe": (100, 600),
            "nain": (50, 300),
            "halfelin": (30, 120),
            "demi-elfe": (30, 150),
            "tieffelin": (25, 80)
        }

        min_age, max_age = age_ranges.get(race, (20, 70))
        return random.randint(min_age, max_age)

    def _create_pnj_embed(self, pnj: dict, type_pnj: str) -> discord.Embed:
        """Crée l'embed Discord pour afficher le PNJ"""

        embed = discord.Embed(
            title=f"🎭 {pnj['nom']} - {type_pnj.title()}",
            description=f"**{pnj['race']} {pnj['genre']}, {pnj['age']} ans**",
            color=0x9932CC)

        # Apparence
        embed.add_field(name="👤 Apparence",
                        value=pnj['apparence'],
                        inline=False)

        # Personnalité
        personnalite_text = (
            f"**Trait positif:** {pnj['personnalite']['trait_positif']}\n"
            f"**Trait négatif:** {pnj['personnalite']['trait_negatif']}\n"
            f"**Manière:** {pnj['personnalite']['maniere']}\n"
            f"**Motivation:** {pnj['personnalite']['motivation']}")
        embed.add_field(name="🧠 Personnalité",
                        value=personnalite_text,
                        inline=False)

        # Détails professionnels
        details_text = "\n".join(
            [f"**{k.title()}:** {v}" for k, v in pnj['details'].items()])
        embed.add_field(name=f"💼 Détails - {type_pnj.title()}",
                        value=details_text,
                        inline=False)

        # Secret/Accroche
        embed.add_field(name="🤫 Secret/Accroche RP",
                        value=pnj['secret'],
                        inline=False)

        embed.set_footer(
            text="💡 Utilisez ces informations pour donner vie à vos PNJ !")

        return embed
