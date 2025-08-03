# commands/boutique/item_selector_v2.py
"""
Sélecteur d'objets adapté pour le fichier OM_PRICE.csv
"""

import random
import logging
from typing import List, Dict, Optional, Tuple
from .config_v2 import get_config, normalize_rarity_name, normalize_lien_magique

logger = logging.getLogger(__name__)

class ItemSelectorV2:
    """
    Classe pour sélectionner des objets aléatoires adaptée au format OM_PRICE.
    """
    
    def __init__(self, excluded_rarities: List[str] = None):
        """
        Initialise le sélecteur d'objets pour OM_PRICE.
        
        Args:
            excluded_rarities: Liste des raretés à exclure (format OM_PRICE)
        """
        self.excluded_rarities = excluded_rarities or ['3-VERY RARE', '4-LEGENDARY']
        # Normaliser les raretés pour la comparaison
        self.excluded_rarities_normalized = [
            self._normalize_rarity(rarity) for rarity in self.excluded_rarities
        ]
        
        # Log de debug
        logger.info(f"Raretés à exclure: {self.excluded_rarities}")
        logger.info(f"Raretés normalisées: {self.excluded_rarities_normalized}")
    
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
        
        # Convertir en majuscules et supprimer les espaces
        normalized = rarity.upper().strip()
        return normalized
    
    def _is_rarity_excluded(self, rarity: str) -> bool:
        """
        Vérifie si une rareté doit être exclue.
        
        Args:
            rarity: Rareté à vérifier (format OM_PRICE)
            
        Returns:
            bool: True si la rareté doit être exclue
        """
        if not rarity:
            return False
        
        normalized_rarity = self._normalize_rarity(rarity)
        
        # Vérification exacte uniquement
        if normalized_rarity in self.excluded_rarities_normalized:
            logger.debug(f"Rareté '{rarity}' -> '{normalized_rarity}' : EXCLUE")
            return True
        
        logger.debug(f"Rareté '{rarity}' -> '{normalized_rarity}' : AUTORISÉE")
        return False
    
    def filter_items_by_rarity(self, items: List[Dict[str, str]], rarity_column: str = "RARETER") -> Tuple[List[Dict[str, str]], List[int]]:
        """
        Filtre les objets selon leur rareté en gardant les indices originaux.
        
        Args:
            items: Liste des objets à filtrer
            rarity_column: Nom de la colonne contenant la rareté
            
        Returns:
            Tuple[List[Dict[str, str]], List[int]]: (Liste des objets filtrés, Liste des indices originaux)
        """
        filtered_items = []
        original_indices = []
        
        for i, item in enumerate(items):
            rarity = item.get(rarity_column, "")
            
            if not self._is_rarity_excluded(rarity):
                filtered_items.append(item)
                original_indices.append(i)
            else:
                item_name = item.get("NameVF") or item.get("Name", "Inconnu")
                logger.debug(f"Objet exclu: {item_name} (Rareté: {rarity})")
        
        logger.info(f"Filtrage terminé: {len(filtered_items)}/{len(items)} objets retenus")
        return filtered_items, original_indices
    
    def select_random_items(self, items_with_indices: Tuple[List[Dict[str, str]], List[int]], min_count: int = 3, max_count: int = 8) -> Tuple[List[Dict[str, str]], List[int]]:
        """
        Sélectionne un nombre aléatoire d'objets avec leurs indices originaux.
        
        Args:
            items_with_indices: Tuple (liste des objets, liste des indices originaux)
            min_count: Nombre minimum d'objets à sélectionner
            max_count: Nombre maximum d'objets à sélectionner
            
        Returns:
            Tuple: (Liste des objets sélectionnés, Liste des indices originaux correspondants)
        """
        items, original_indices = items_with_indices
        
        if not items:
            raise ValueError("Aucun objet disponible pour la sélection")
        
        # Déterminer le nombre d'objets à sélectionner
        available_count = len(items)
        target_count = random.randint(min_count, min(max_count, available_count))
        
        if target_count > available_count:
            logger.warning(f"Pas assez d'objets disponibles: {available_count} < {target_count}")
            target_count = available_count
        
        # Créer une liste de tuples (objet, index_original)
        items_with_original_indices = list(zip(items, original_indices))
        
        # Sélection aléatoire sans remise
        selected_items_with_indices = random.sample(items_with_original_indices, target_count)
        
        # Séparer les objets et les indices
        selected_items = [item for item, _ in selected_items_with_indices]
        selected_indices = [index for _, index in selected_items_with_indices]
        
        logger.info(f"Sélection aléatoire: {len(selected_items)} objets choisis")
        return selected_items, selected_indices
    
    def get_item_stats(self, items: List[Dict[str, str]], rarity_column: str = "RARETER") -> Dict[str, int]:
        """
        Retourne les statistiques sur les raretés des objets.
        """
        stats = {}
        
        for item in items:
            rarity = item.get(rarity_column, "0-COMMUN").strip()
            if not rarity:
                rarity = "0-COMMUN"
            
            # Convertir en format lisible
            readable_rarity = normalize_rarity_name(rarity)
            stats[readable_rarity] = stats.get(readable_rarity, 0) + 1
        
        return stats
    
    def validate_item_data(self, item: Dict[str, str]) -> Dict[str, str]:
        """
        Valide et nettoie les données d'un objet OM_PRICE.
        """
        validated_item = {}
        
        # Copier toutes les données existantes
        for key, value in item.items():
            validated_item[key] = str(value).strip() if value else ""
        
        # Utiliser le nom français en priorité, sinon anglais
        nom_francais = validated_item.get("NameVF", "")
        nom_anglais = validated_item.get("Name", "")
        
        if nom_francais:
            validated_item["nom_display"] = nom_francais
        elif nom_anglais:
            validated_item["nom_display"] = nom_anglais
        else:
            validated_item["nom_display"] = "Objet mystérieux"
        
        # Normaliser la rareté pour l'affichage
        rarity_raw = validated_item.get("RARETER", "0-COMMUN")
        validated_item["rarity_display"] = normalize_rarity_name(rarity_raw)
        
        # Normaliser le lien magique
        lien_raw = validated_item.get("Lien", "N")
        validated_item["lien_display"] = normalize_lien_magique(lien_raw)
        
        # Gérer les prix (utiliser CostF en priorité)
        price_costf = validated_item.get("CostF", "")
        price_median = validated_item.get("MEDIANNE", "")
        
        if price_costf and price_costf != "0":
            validated_item["price_display"] = f"{price_costf} po"
        elif price_median and price_median != "0":
            validated_item["price_display"] = f"{price_median} po"
        else:
            validated_item["price_display"] = "Prix non spécifié"
        
        return validated_item