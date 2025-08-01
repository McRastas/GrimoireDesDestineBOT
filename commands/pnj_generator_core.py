# commands/pnj_generator_core.py - Logique Principale de Génération
import random
from .pnj_generator_data import PNJData


class PNJGenerator:
    """Générateur principal de PNJ - Logique de création"""
    
    def __init__(self):
        self.data = PNJData()
    
    def generate_pnj(self, type_pnj: str, genre: str, race: str) -> dict:
        """Génère un PNJ complet"""
        
        # Déterminer le genre
        if genre == "aleatoire":
            genre = random.choice(["masculin", "feminin"])

        # Déterminer la race
        if race == "aleatoire":
            race = random.choice([
                "humain", "elfe", "nain", "halfelin", "demi-elfe", "tieffelin"
            ])

        # Générer tous les composants du PNJ
        nom = self._generate_name(race, genre)
        apparence = self._generate_appearance(race, genre)
        personnalite = self._generate_personality()
        details = self._generate_type_details(type_pnj)
        secret = self._generate_secret(type_pnj)
        age = self._generate_age(race)

        return {
            "nom": nom,
            "race": race.title(),
            "genre": genre,
            "apparence": apparence,
            "personnalite": personnalite,
            "details": details,
            "secret": secret,
            "age": age
        }
    
    def _generate_name(self, race: str, genre: str) -> str:
        """Génère un nom selon la race et le genre"""
        race_names = self.data.names_data.get(race, self.data.names_data["humain"])
        gender_names = race_names.get(genre, race_names["masculin"])
        return random.choice(gender_names)
    
    def _generate_appearance(self, race: str, genre: str) -> str:
        """Génère l'apparence selon la race et le genre"""
        
        taille = random.choice(self.data.tailles.get(race, self.data.tailles["humain"]))
        cheveux_desc = random.choice(self.data.cheveux)
        yeux_desc = random.choice(self.data.yeux)
        distinctif = random.choice(self.data.distinctifs)

        # Gérer les spécificités raciales
        if race == "nain" and genre == "masculin":
            barbe_desc = random.choice(self.data.barbes)
            return f"{taille.title()}, aux cheveux {cheveux_desc} et aux yeux {yeux_desc}. Porte une barbe {barbe_desc} et a {distinctif}."
        else:
            return f"{taille.title()}, aux cheveux {cheveux_desc} et aux yeux {yeux_desc}. A {distinctif}."
    
    def _generate_personality(self) -> dict:
        """Génère les traits de personnalité"""
        return {
            "trait_positif": random.choice(self.data.traits_positifs),
            "trait_negatif": random.choice(self.data.traits_negatifs),
            "maniere": random.choice(self.data.manieres),
            "motivation": random.choice(self.data.motivations)
        }
    
    def _generate_type_details(self, type_pnj: str) -> dict:
        """Génère les détails spécifiques au type de PNJ"""
        
        if type_pnj == "marchand":
            return {
                "specialite": random.choice(self.data.marchand_specialites),
                "richesse": random.choice(self.data.marchand_richesses),
                "reputation": random.choice(self.data.marchand_reputations),
                "info_extra": f"Tient boutique depuis {random.randint(5, 30)} ans"
            }
        
        elif type_pnj == "noble":
            return {
                "titre": random.choice(self.data.noble_titres),
                "domaine": random.choice(self.data.noble_domaines),
                "influence": random.choice(self.data.noble_influences),
                "info_extra": f"Famille noble depuis {random.randint(3, 12)} générations"
            }
        
        elif type_pnj == "garde":
            return {
                "rang": random.choice(self.data.garde_rangs),
                "experience": f"{random.randint(2, 20)} ans de service",
                "specialite": random.choice(self.data.garde_specialites),
                "info_extra": random.choice(self.data.garde_backgrounds)
            }
        
        elif type_pnj == "aubergiste":
            return {
                "etablissement": random.choice(self.data.aubergiste_etablissements),
                "reputation": random.choice(self.data.aubergiste_reputations),
                "specialite_culinaire": random.choice(self.data.aubergiste_specialites),
                "info_extra": f"Gérant depuis {random.randint(3, 25)} ans"
            }
        
        elif type_pnj == "pretre":
            return {
                "divinite": random.choice(self.data.pretre_divinites),
                "rang_clerical": random.choice(self.data.pretre_rangs),
                "temple": random.choice(self.data.pretre_temples),
                "info_extra": f"Servant fidèle depuis {random.randint(5, 30)} ans"
            }
        
        elif type_pnj == "aventurier":
            return {
                "classe": random.choice(self.data.aventurier_classes),
                "niveau_estime": random.choice(self.data.aventurier_niveaux),
                "specialite": random.choice(self.data.aventurier_specialites),
                "info_extra": f"Aventurier depuis {random.randint(1, 15)} ans"
            }
        
        elif type_pnj == "artisan":
            return {
                "metier": random.choice(self.data.artisan_metiers),
                "reputation": random.choice(self.data.artisan_reputations),
                "specialite": random.choice(self.data.artisan_specialites),
                "info_extra": f"Pratique son art depuis {random.randint(3, 25)} ans"
            }
        
        elif type_pnj == "paysan":
            return {
                "activite": random.choice(self.data.paysan_activites),
                "statut": random.choice(self.data.paysan_statuts),
                "specialite": random.choice(self.data.paysan_specialites),
                "info_extra": f"Travaille la terre depuis {random.randint(5, 40)} ans"
            }
        
        elif type_pnj == "voleur":
            return {
                "specialite": random.choice(self.data.voleur_specialites),
                "reputation": random.choice(self.data.voleur_reputations),
                "territoire": random.choice(self.data.voleur_territoires),
                "info_extra": f"Actif dans le milieu depuis {random.randint(2, 20)} ans"
            }
        
        elif type_pnj == "mage":
            return {
                "ecole_magie": random.choice(self.data.mage_ecoles),
                "niveau_estime": random.choice(self.data.mage_niveaux),
                "specialite": random.choice(self.data.mage_specialites),
                "info_extra": f"Étudie la magie depuis {random.randint(5, 35)} ans"
            }
        
        else:
            return {
                "profession": type_pnj.title(),
                "experience": "Quelques années",
                "reputation": "Correcte",
                "info_extra": "Détails à développer"
            }
    
    def _generate_secret(self, type_pnj: str) -> str:
        """Génère un secret ou une accroche RP"""
        
        # Secrets spécifiques au type
        type_secrets = self.data.secrets_by_type.get(type_pnj, [])
        
        # Tous les secrets disponibles
        all_secrets = self.data.secrets_generaux + type_secrets
        
        return random.choice(all_secrets)
    
    def _generate_age(self, race: str) -> int:
        """Génère un âge approprié selon la race"""
        min_age, max_age = self.data.age_ranges.get(race, (18, 70))
        return random.randint(min_age, max_age)