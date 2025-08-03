# commands/boutique/item_selector.py
"""
Sélecteur d'objets aléatoires avec filtres de rareté.
"""

import random
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class ItemSelector:
    """
    Classe pour sélectionner des objets aléatoires avec filtres.
    """
    
    def __init__(self, excluded_rarities: List[str] = None):
        """
        Initialise le sélecteur d'objets.
        
        Args:
            excluded_rarities: Liste des raretés à exclure (par défaut: très rare, légendaire)
        """
        self.excluded_rarities = excluded_rarities or ['très rare', 'légendaire']
        # Normaliser les raretés pour la comparaison (minuscules, sans accents)
        self.excluded_rarities_normalized = [
            self._normalize_rarity(rarity) for rarity in self.excluded_rarities
        ]
    
    def _normalize_rarity(self, rarity: str) -> str:
        """
        Normalise une rareté pour la comparaison.
        
        Args:
            rarity: Rareté à normaliser
            
        Returns:
            str: Rareté normalisée
        """
        if not rarity:
            return ""
        
        # Convertir en minuscules et supprimer les espaces
        normalized = rarity.lower().strip()
        
        # Suppression des accents basique
        accent_map = {
            'è': 'e', 'é': 'e', 'ê': 'e', 'ë': 'e',
            'à': 'a', 'á': 'a', 'â': 'a', 'ä': 'a',
            'ù': 'u', 'ú': 'u', 'û': 'u', 'ü': 'u',
            'ò': 'o', 'ó': 'o', 'ô': 'o', 'ö': 'o',
            'ì': 'i', 'í': 'i', 'î': 'i', 'ï': 'i',
            'ç': 'c'
        }
        
        for accented, normal in accent_map.items():
            normalized = normalized.replace(accented, normal)
        
        return normalized
    
    def _is_rarity_excluded(self, rarity: str) -> bool:
        """
        Vérifie si une rareté doit être exclue.
        
        Args:
            rarity: Rareté à vérifier
            
        Returns:
            bool: True si la rareté doit être exclue
        """
        if not rarity:
            return False
        
        normalized_rarity = self._normalize_rarity(rarity)
        
        # Vérification exacte
        if normalized_rarity in self.excluded_rarities_normalized:
            return True
        
        # Vérification partielle (contient le mot clé)
        for excluded in self.excluded_rarities_normalized:
            if excluded in normalized_rarity or normalized_rarity in excluded:
                return True
        
        return False
    
    def filter_items_by_rarity(self, items: List[Dict[str, str]], rarity_column: str = 'Rareté') -> List[Dict[str, str]]:
        """
        Filtre les objets selon leur rareté.
        
        Args:
            items: Liste des objets à filtrer
            rarity_column: Nom de la colonne contenant la rareté
            
        Returns:
            List[Dict[str, str]]: Liste des objets filtrés
        """
        filtered_items = []
        
        for item in items:
            rarity = item.get(rarity_column, "")
            
            if not self._is_rarity_excluded(rarity):
                filtered_items.append(item)
            else:
                item_name = item.get("Nom de l'objet", "Inconnu")
                logger.debug(f"Objet exclu: {item_name} (Rareté: {rarity})")
        
        logger.info(f"Filtrage terminé: {len(filtered_items)}/{len(items)} objets retenus")
        return filtered_items
    
    def select_random_items(self, items: List[Dict[str, str]], min_count: int = 3, max_count: int = 8) -> List[Dict[str, str]]:
        """
        Sélectionne un nombre aléatoire d'objets.
        
        Args:
            items: Liste des objets disponibles
            min_count: Nombre minimum d'objets à sélectionner
            max_count: Nombre maximum d'objets à sélectionner
            
        Returns:
            List[Dict[str, str]]: Liste des objets sélectionnés
            
        Raises:
            ValueError: Si pas assez d'objets disponibles
        """
        if not items:
            raise ValueError("Aucun objet disponible pour la sélection")
        
        # Déterminer le nombre d'objets à sélectionner
        available_count = len(items)
        target_count = random.randint(min_count, min(max_count, available_count))
        
        if target_count > available_count:
            logger.warning(f"Pas assez d'objets disponibles: {available_count} < {target_count}")
            target_count = available_count
        
        # Sélection aléatoire sans remise
        selected_items = random.sample(items, target_count)
        
        logger.info(f"Sélection aléatoire: {len(selected_items)} objets choisis")
        return selected_items
    
    def get_item_stats(self, items: List[Dict[str, str]], rarity_column: str = 'Rareté') -> Dict[str, int]:
        """
        Retourne les statistiques sur les raretés des objets.
        
        Args:
            items: Liste des objets à analyser
            rarity_column: Nom de la colonne contenant la rareté
            
        Returns:
            Dict[str, int]: Statistiques par rareté
        """
        stats = {}
        
        for item in items:
            rarity = item.get(rarity_column, "Inconnue").strip()
            if not rarity:
                rarity = "Inconnue"
            
            stats[rarity] = stats.get(rarity, 0) + 1
        
        return stats
    
    def validate_item_data(self, item: Dict[str, str]) -> Dict[str, str]:
        """
        Valide et nettoie les données d'un objet.
        
        Args:
            item: Objet à valider
            
        Returns:
            Dict[str, str]: Objet validé
        """
        validated_item = {}
        
        # Copier toutes les données existantes
        for key, value in item.items():
            validated_item[key] = str(value).strip() if value else ""
        
        # Gérer le nom de l'objet (utiliser le nom alternatif en priorité s'il existe)
        nom_principal = validated_item.get("Nom de l'objet", "")
        nom_alternatif = validated_item.get("Nom de l'objet_1", "")
        
        # Utiliser le nom alternatif s'il existe et n'est pas vide, sinon le principal
        if nom_alternatif and nom_alternatif != nom_principal:
            validated_item["Nom de l'objet_display"] = nom_alternatif
        else:
            validated_item["Nom de l'objet_display"] = nom_principal or "Objet mystérieux"
        
        # Colonnes requises avec valeurs par défaut
        required_columns = {
            "Rareté": "Inconnue",
            "Prix achat": "Non spécifié",
            "Prix vente": "Non spécifié",
            "Effet": "Effet mystérieux",
            "Type": "Objet magique"
        }
        
        # Ajouter les valeurs par défaut pour les colonnes manquantes
        for column, default_value in required_columns.items():
            if column not in validated_item or not validated_item[column]:
                validated_item[column] = default_value
        
        return validated_item