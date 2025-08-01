# commands/pnj_generator_data.py - Toutes les Données du Générateur PNJ

class PNJData:
    """Classe centralisant toutes les données pour la génération de PNJ"""
    
    def __init__(self):
        self._init_names_data()
        self._init_appearance_data()
        self._init_personality_data()
        self._init_profession_data()
        self._init_secrets_data()
        self._init_age_data()
    
    def _init_names_data(self):
        """Initialise les données de noms par race et genre"""
        self.names_data = {
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
    
    def _init_appearance_data(self):
        """Initialise les données d'apparence"""
        self.tailles = {
            "humain": ["grand", "moyen", "petit"],
            "elfe": ["élancé", "gracieux", "svelte"],
            "nain": ["trapu", "robuste", "costaud"],
            "halfelin": ["petit", "menu", "délicat"],
            "demi-elfe": ["grand", "élancé", "gracieux"],
            "tieffelin": ["imposant", "élancé", "mystérieux"]
        }
        
        self.cheveux = [
            "noirs", "bruns", "châtains", "blonds", "roux", "gris", "blancs",
            "argentés", "cuivrés"
        ]
        
        self.yeux = [
            "noirs", "bruns", "verts", "bleus", "gris", "noisette", "dorés",
            "violets", "rouges"
        ]
        
        self.distinctifs = [
            "une cicatrice sur la joue", "une dent en or", "un tatouage tribal",
            "une bague ornée", "une amulette", "une cape colorée",
            "des bijoux voyants", "un chapeau distinctif", "une canne sculptée",
            "une sacoche en cuir", "des gants élégants", "une épingle à cheveux"
        ]
        
        self.barbes = [
            "courte et soignée", "longue et tressée", "épaisse et grise", "rousse et fournie"
        ]
    
    def _init_personality_data(self):
        """Initialise les données de personnalité"""
        self.traits_positifs = [
            "généreux", "courageux", "loyal", "intelligent", "charismatique",
            "patient", "déterminé", "honnête", "compassionnel", "humble"
        ]
        
        self.traits_negatifs = [
            "cupide", "impatient", "têtu", "arrogant", "méfiant", "paresseux",
            "bavard", "pessimiste", "jaloux", "colérique"
        ]
        
        self.manieres = [
            "se gratte le nez quand il ment",
            "tapote des doigts quand il réfléchit", "cligne beaucoup des yeux",
            "se penche en avant pour écouter", "croise toujours les bras",
            "sourit trop souvent", "baisse la voix pour les secrets",
            "regarde toujours par-dessus l'épaule"
        ]
        
        self.motivations = [
            "protéger sa famille", "devenir riche", "se venger d'un ennemi",
            "découvrir la vérité sur son passé", "aider les plus démunis",
            "atteindre la reconnaissance", "préserver une tradition",
            "explorer de nouveaux horizons"
        ]
    
    def _init_profession_data(self):
        """Initialise les données professionnelles par type"""
        
        # Marchand
        self.marchand_specialites = [
            "armes et armures", "potions et herbes", "bijoux précieux",
            "équipement d'aventurier", "nourriture exotique", "livres rares"
        ]
        self.marchand_richesses = ["prospère", "modeste", "en difficulté", "très riche"]
        self.marchand_reputations = ["honnête", "de confiance", "un peu louche", "réputé pour ses prix"]
        
        # Noble
        self.noble_titres = ["Lord/Lady", "Baron/Baronne", "Comte/Comtesse", "Duc/Duchesse"]
        self.noble_domaines = ["terres agricoles", "mines d'or", "vignobles", "forêts", "ports commerciaux"]
        self.noble_influences = ["locale", "régionale", "courtisane", "militaire"]
        
        # Garde
        self.garde_rangs = ["simple garde", "sergent", "capitaine", "lieutenant"]
        self.garde_specialites = ["patrouilles", "enquêtes", "formation", "garde du corps"]
        self.garde_backgrounds = ["ancien soldat", "natif de la ville", "recruté récemment"]
        
        # Aubergiste
        self.aubergiste_etablissements = ["auberge de luxe", "taverne populaire", "relais de voyageurs", "gîte familial"]
        self.aubergiste_reputations = ["accueillant", "discret", "convivial", "respecté"]
        self.aubergiste_specialites = ["ragoûts copieux", "pâtisseries", "bières locales", "cuisine régionale"]
        
        # Prêtre
        self.pretre_divinites = ["Tyr", "Helm", "Lathander", "Selûne", "Tempus", "Mystra", "Oghma", "Torm"]
        self.pretre_rangs = ["acolyte", "prêtre", "grand prêtre", "chapelain"]
        self.pretre_temples = ["temple principal", "chapelle locale", "sanctuaire", "monastère"]
        
        # Aventurier
        self.aventurier_classes = ["guerrier", "rôdeur", "roublard", "mage", "clerc"]
        self.aventurier_niveaux = ["débutant", "expérimenté", "vétéran", "légendaire"]
        self.aventurier_specialites = ["exploration de donjons", "chasse aux monstres", "escorte de caravanes", "missions diplomatiques"]
        
        # Artisan
        self.artisan_metiers = ["forgeron", "menuisier", "tisserand", "potier", "bijoutier", "cordonnier", "tailleur", "boulanger"]
        self.artisan_reputations = ["maître artisan", "apprenti talentueux", "créateur renommé", "artisan respecté"]
        self.artisan_specialites = ["travail de précision", "créations uniques", "réparations rapides", "commandes spéciales"]
        
        # Paysan
        self.paysan_activites = ["agriculture", "élevage", "viticulture", "apiculture", "maraîchage", "sylviculture"]
        self.paysan_statuts = ["propriétaire", "fermier", "métayer", "ouvrier agricole"]
        self.paysan_specialites = ["cultures céréalières", "légumes", "fruits", "bétail", "produits laitiers", "miel et cire"]
        
        # Voleur
        self.voleur_specialites = ["pickpocket", "cambrioleur", "escroc", "contrebandier", "receleur", "assassin"]
        self.voleur_reputations = ["discret et efficace", "audacieux", "dangereux", "mystérieux", "recherché"]
        self.voleur_territoires = ["quartiers riches", "docks", "marché", "routes commerciales", "tavernes", "arrière-cours"]
        
        # Mage
        self.mage_ecoles = ["évocation", "illusion", "enchantement", "divination", "nécromancie", "transmutation", "abjuration", "invocation"]
        self.mage_niveaux = ["apprenti", "magicien confirmé", "maître", "archimage"]
        self.mage_specialites = ["recherche théorique", "création d'objets magiques", "sorts de combat", "sorts utilitaires", "rituels anciens"]
    
    def _init_secrets_data(self):
        """Initialise les données de secrets et accroches RP"""
        
        self.secrets_generaux = [
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
        
        self.secrets_by_type = {
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
    
    def _init_age_data(self):
        """Initialise les données d'âge par race"""
        self.age_ranges = {
            "humain": (18, 70),
            "elfe": (100, 500),
            "nain": (40, 250),
            "halfelin": (20, 100),
            "demi-elfe": (25, 150),
            "tieffelin": (18, 80)
        }