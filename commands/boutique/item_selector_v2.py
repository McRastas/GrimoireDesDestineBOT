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
    
    def _is_item_valid(self, item: Dict[str, str]) -> bool:
        """
        Vérifie si un objet est valide (pas de valeurs NA importantes).
        
        Args:
            item: Objet à vérifier
            
        Returns:
            bool: True si l'objet est valide
        """
        if not item:
            return False
        
        # Colonnes critiques qui ne doivent pas être NA
        critical_columns = [
            'Name',           # Nom anglais
            'NameVF',         # Nom français
            'RARETER',        # Rareté
            'Type'            # Type
        ]
        
        # Vérifier les colonnes critiques
        for column in critical_columns:
            value = item.get(column, "")
            if not value or str(value).strip().upper() in ['NA', 'N/A', '']:
                logger.debug(f"Objet invalide - {column}: '{value}'")
                return False
        
        # Vérifier qu'au moins un nom existe (français ou anglais)
        name_fr = item.get('NameVF', '')
        name_en = item.get('Name', '')
        
        if (not name_fr or str(name_fr).strip().upper() in ['NA', 'N/A', '']) and \
           (not name_en or str(name_en).strip().upper() in ['NA', 'N/A', '']):
            logger.debug("Objet invalide - aucun nom valide")
            return False
        
        # Vérifier la rareté
        rarity = item.get('RARETER', '')
        if not rarity or str(rarity).strip().upper() in ['NA', 'N/A', '']:
            logger.debug("Objet invalide - rareté NA")
            return False
        
        return True
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
        Exclut également les objets avec des valeurs NA.
        
        Args:
            items: Liste des objets à filtrer
            rarity_column: Nom de la colonne contenant la rareté
            
        Returns:
            Tuple[List[Dict[str, str]], List[int]]: (Liste des objets filtrés, Liste des indices originaux)
        """
        filtered_items = []
        original_indices = []
        excluded_count = {'rarity': 0, 'na_values': 0, 'total': 0}
        
        for i, item in enumerate(items):
            # D'abord vérifier si l'objet est valide (pas de NA)
            if not self._is_item_valid(item):
                excluded_count['na_values'] += 1
                excluded_count['total'] += 1
                item_name = item.get("NameVF") or item.get("Name", "Inconnu")
                logger.debug(f"Objet exclu (NA): {item_name}")
                continue
            
            # Ensuite vérifier la rareté
            rarity = item.get(rarity_column, "")
            
            if not self._is_rarity_excluded(rarity):
                filtered_items.append(item)
                original_indices.append(i)
            else:
                excluded_count['rarity'] += 1
                excluded_count['total'] += 1
                item_name = item.get("NameVF") or item.get("Name", "Inconnu")
                logger.debug(f"Objet exclu (rareté): {item_name} (Rareté: {rarity})")
        
        logger.info(f"Filtrage terminé: {len(filtered_items)}/{len(items)} objets retenus")
        logger.info(f"Exclusions: {excluded_count['na_values']} NA, {excluded_count['rarity']} rareté, {excluded_count['total']} total")
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
        Remplace les valeurs NA par des valeurs par défaut.
        """
        validated_item = {}
        
        # Copier toutes les données existantes en nettoyant les NA
        for key, value in item.items():
            if value is None or str(value).strip().upper() in ['NA', 'N/A', '']:
                validated_item[key] = ""
            else:
                validated_item[key] = str(value).strip()
        
        # Utiliser le nom français en priorité, sinon anglais
        nom_francais = validated_item.get("NameVF", "")
        nom_anglais = validated_item.get("Name", "")
        
        if nom_francais and nom_francais.upper() not in ['NA', 'N/A']:
            validated_item["nom_display"] = nom_francais
        elif nom_anglais and nom_anglais.upper() not in ['NA', 'N/A']:
            validated_item["nom_display"] = nom_anglais
        else:
            validated_item["nom_display"] = "Objet mystérieux"
        
        # Normaliser la rareté pour l'affichage
        rarity_raw = validated_item.get("RARETER", "0-COMMUN")
        if rarity_raw and rarity_raw.upper() not in ['NA', 'N/A']:
            validated_item["rarity_display"] = normalize_rarity_name(rarity_raw)
        else:
            validated_item["rarity_display"] = "Commun"
        
        # Normaliser le lien magique
        lien_raw = validated_item.get("Lien", "N")
        if lien_raw and lien_raw.upper() not in ['NA', 'N/A']:
            validated_item["lien_display"] = normalize_lien_magique(lien_raw)
        else:
            validated_item["lien_display"] = "Non"
        
        # Gérer les prix (utiliser CostF en priorité, puis MEDIANNE)
        price_costf = validated_item.get("CostF", "")
        price_median = validated_item.get("MEDIANNE", "")
        
        # Nettoyer les prix NA
        if price_costf and price_costf.upper() not in ['NA', 'N/A', '0', '']:
            try:
                # Vérifier que c'est un nombre valide
                float(price_costf)
                validated_item["price_display"] = f"{price_costf} po"
            except ValueError:
                price_costf = ""
        else:
            price_costf = ""
        
        if not price_costf and price_median and price_median.upper() not in ['NA', 'N/A', '0', '']:
            try:
                # Vérifier que c'est un nombre valide
                float(price_median)
                validated_item["price_display"] = f"{price_median} po"
            except ValueError:
                validated_item["price_display"] = "Prix non spécifié"
        elif not price_costf:
            validated_item["price_display"] = "Prix non spécifié"
        
        # Nettoyer le type
        item_type = validated_item.get("Type", "")
        if item_type and item_type.upper() not in ['NA', 'N/A']:
            validated_item["Type"] = item_type
        else:
            validated_item["Type"] = "Objet magique"
        
        # Nettoyer la source
        source = validated_item.get("Source", "")
        if source and source.upper() not in ['NA', 'N/A']:
            validated_item["Source"] = source
        else:
            validated_item["Source"] = "Inconnue"
        
        return validated_item