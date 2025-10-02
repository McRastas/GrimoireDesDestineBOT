# commands/postulation/character_selector.py
"""
Sélection et filtrage des personnages pour la postulation.
"""

import logging
from typing import List, Dict, Optional
from .config import get_config, format_class_info, clean_value

logger = logging.getLogger(__name__)


class CharacterSelector:
    """Gère la sélection et le filtrage des personnages."""
    
    def __init__(self):
        """Initialise le sélecteur de personnages."""
        self.config = get_config()
        self.columns = self.config['columns']
        self.filtering = self.config['filtering']
        logger.info("CharacterSelector initialisé")
    
    def filter_active_characters(self, characters: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Filtre les personnages pour ne garder que les actifs.
        
        Args:
            characters: Liste de tous les personnages
            
        Returns:
            List[Dict[str, str]]: Liste des personnages actifs
        """
        statut_column = self.columns['statut']
        statut_valide = self.filtering['statut_valide']
        statut_pnj = self.filtering['statut_pnj']
        exclude_pnj = self.filtering['exclude_pnj']
        
        active_characters = []
        
        for char in characters:
            statut = clean_value(char.get(statut_column, ''))
            
            # Vérifier si le statut est valide
            if statut.upper() != statut_valide.upper():
                logger.debug(f"Personnage '{char.get(self.columns['nom_pj'], 'Inconnu')}' ignoré: statut '{statut}'")
                continue
            
            # Vérifier si c'est un PNJ (si exclusion activée)
            if exclude_pnj and statut.upper() == statut_pnj.upper():
                logger.debug(f"PNJ '{char.get(self.columns['nom_pj'], 'Inconnu')}' ignoré")
                continue
            
            active_characters.append(char)
        
        logger.info(f"✅ {len(active_characters)} personnages actifs sur {len(characters)} total")
        return active_characters
    
    def format_character_for_display(self, character: Dict[str, str]) -> Dict[str, str]:
        """
        Formate un personnage pour l'affichage.
        
        Args:
            character: Données brutes du personnage
            
        Returns:
            Dict[str, str]: Personnage formaté avec toutes les infos
        """
        # Récupérer les valeurs
        nom_pj = clean_value(character.get(self.columns['nom_pj'], ''), 'Personnage inconnu')
        joueur = clean_value(character.get(self.columns['joueur'], ''), 'Joueur inconnu')
        race = clean_value(character.get(self.columns['race'], ''), 'Race inconnue')
        token_url = clean_value(character.get(self.columns['token_url'], ''))
        niveau_total = clean_value(character.get(self.columns['niveau_total'], ''), '1')
        
        # Récupérer les classes
        classe1 = clean_value(character.get(self.columns['classe1'], ''))
        niveau1 = clean_value(character.get(self.columns['niveau1'], ''))
        classe2 = clean_value(character.get(self.columns['classe2'], ''))
        niveau2 = clean_value(character.get(self.columns['niveau2'], ''))
        classe3 = clean_value(character.get(self.columns['classe3'], ''))
        niveau3 = clean_value(character.get(self.columns['niveau3'], ''))
        
        # Formater les classes
        classes_formatted = format_class_info(
            classe1, niveau1,
            classe2, niveau2,
            classe3, niveau3
        )
        
        formatted = {
            'nom_pj': nom_pj,
            'joueur': joueur,
            'race': race,
            'token_url': token_url,
            'niveau_total': niveau_total,
            'classes': classes_formatted,
            'classe1': classe1,
            'niveau1': niveau1,
            'classe2': classe2,
            'niveau2': niveau2,
            'classe3': classe3,
            'niveau3': niveau3
        }
        
        logger.debug(f"Personnage formaté: {nom_pj} - {race} - {classes_formatted}")
        return formatted
    
    def create_select_option_label(self, character: Dict[str, str]) -> str:
        """
        Crée le label pour une option de sélection Discord.
        
        Args:
            character: Personnage formaté
            
        Returns:
            str: Label pour le menu déroulant (max 100 caractères)
        """
        nom = character['nom_pj']
        race = character['race']
        classes = character['classes']
        
        # Format: "Nom - Race - Classes"
        label = f"{nom} - {race} - {classes}"
        
        # Limiter à 100 caractères (limite Discord)
        if len(label) > 100:
            label = label[:97] + "..."
        
        return label
    
    def create_select_option_description(self, character: Dict[str, str]) -> str:
        """
        Crée la description pour une option de sélection Discord.
        
        Args:
            character: Personnage formaté
            
        Returns:
            str: Description pour le menu déroulant (max 100 caractères)
        """
        niveau = character['niveau_total']
        joueur = character['joueur']
        
        # Format: "Niveau X - Joueur"
        description = f"Niveau {niveau} - {joueur}"
        
        # Limiter à 100 caractères (limite Discord)
        if len(description) > 100:
            description = description[:97] + "..."
        
        return description
    
    def prepare_characters_for_select_menu(
        self, 
        characters: List[Dict[str, str]]
    ) -> List[Dict[str, str]]:
        """
        Prépare les personnages pour un menu de sélection Discord.
        
        Args:
            characters: Liste des personnages bruts
            
        Returns:
            List[Dict[str, str]]: Liste des personnages formatés pour Discord
        """
        # Filtrer les personnages actifs
        active_characters = self.filter_active_characters(characters)
        
        if not active_characters:
            logger.warning("Aucun personnage actif trouvé")
            return []
        
        # Formater chaque personnage
        formatted_characters = []
        for char in active_characters:
            formatted = self.format_character_for_display(char)
            formatted_characters.append(formatted)
        
        # Limiter à 25 personnages (limite Discord pour les select menus)
        if len(formatted_characters) > 25:
            logger.warning(f"Trop de personnages ({len(formatted_characters)}), limitation à 25")
            formatted_characters = formatted_characters[:25]
        
        logger.info(f"✅ {len(formatted_characters)} personnages préparés pour le menu de sélection")
        return formatted_characters
    
    def find_character_by_name(
        self, 
        characters: List[Dict[str, str]], 
        character_name: str
    ) -> Optional[Dict[str, str]]:
        """
        Trouve un personnage par son nom.
        
        Args:
            characters: Liste des personnages formatés
            character_name: Nom du personnage à trouver
            
        Returns:
            Optional[Dict[str, str]]: Personnage trouvé ou None
        """
        for char in characters:
            if char['nom_pj'] == character_name:
                logger.debug(f"Personnage trouvé: {character_name}")
                return char
        
        logger.warning(f"Personnage non trouvé: {character_name}")
        return None
    
    def validate_character(self, character: Dict[str, str]) -> bool:
        """
        Valide qu'un personnage a toutes les informations nécessaires.
        
        Args:
            character: Personnage formaté
            
        Returns:
            bool: True si le personnage est valide
        """
        required_fields = ['nom_pj', 'race', 'classes', 'niveau_total']
        
        for field in required_fields:
            value = character.get(field, '')
            if not value or value in ['Inconnu', 'Race inconnue', 'Classe inconnue']:
                logger.warning(f"Personnage invalide: champ '{field}' manquant ou invalide")
                return False
        
        logger.debug(f"Personnage valide: {character['nom_pj']}")
        return True
    
    def get_character_summary(self, character: Dict[str, str]) -> str:
        """
        Génère un résumé textuel d'un personnage.
        
        Args:
            character: Personnage formaté
            
        Returns:
            str: Résumé du personnage
        """
        summary = (
            f"**{character['nom_pj']}**\n"
            f"🧝 Race : {character['race']}\n"
            f"⚔️ Classe : {character['classes']}\n"
            f"📊 Niveau total : {character['niveau_total']}"
        )
        
        return summary


if __name__ == "__main__":
    # Test du sélecteur
    print("🧪 Test du CharacterSelector")
    print("=" * 60)
    
    selector = CharacterSelector()
    
    # Données de test
    test_characters = [
        {
            'ID Discord': '123456789',
            'Nom du PJ': 'Aerin Marteau-Sombre',
            'Joueurs': 'TestPlayer',
            'Url de token': 'https://example.com/token.png',
            'Races': 'Nain (Colline)',
            'Classe 1': 'Paladin',
            'Niv.': '1',
            'Classe 2': '',
            'Niv._1': '',
            'Classe 3': '',
            'Niv._2': '',
            'Niv. PJ': '1',
            'Statut': 'ACTIF'
        },
        {
            'ID Discord': '123456789',
            'Nom du PJ': 'Ezekiel',
            'Joueurs': 'TestPlayer',
            'Url de token': 'https://example.com/token2.png',
            'Races': 'Humain (Variant)',
            'Classe 1': 'Magicien',
            'Niv.': '7',
            'Classe 2': '',
            'Niv._1': '',
            'Classe 3': '',
            'Niv._2': '',
            'Niv. PJ': '7',
            'Statut': 'ACTIF'
        },
        {
            'ID Discord': '123456789',
            'Nom du PJ': 'Personnage Inactif',
            'Joueurs': 'TestPlayer',
            'Url de token': '',
            'Races': 'Elfe',
            'Classe 1': 'Guerrier',
            'Niv.': '5',
            'Classe 2': '',
            'Niv._1': '',
            'Classe 3': '',
            'Niv._2': '',
            'Niv. PJ': '5',
            'Statut': 'INACTIF'
        }
    ]
    
    # Test 1: Filtrage des personnages actifs
    print("\n📋 Test 1: Filtrage des personnages actifs")
    active = selector.filter_active_characters(test_characters)
    print(f"   Personnages actifs: {len(active)}/{len(test_characters)}")
    
    # Test 2: Formatage pour affichage
    print("\n✨ Test 2: Formatage des personnages")
    formatted = selector.prepare_characters_for_select_menu(test_characters)
    for char in formatted:
        print(f"\n   {char['nom_pj']}:")
        print(f"   • Label: {selector.create_select_option_label(char)}")
        print(f"   • Description: {selector.create_select_option_description(char)}")
        print(f"   • Résumé:\n{selector.get_character_summary(char)}")
    
    # Test 3: Validation
    print("\n✅ Test 3: Validation des personnages")
    for char in formatted:
        is_valid = selector.validate_character(char)
        print(f"   {char['nom_pj']}: {'✅ Valide' if is_valid else '❌ Invalide'}")
    
    print("\n" + "=" * 60)
    print("✅ Tests terminés")