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
        """
        if not rarity:
            return False
        
        cleaned_rarity = rarity.strip()
        
        for excluded in self.excluded_rarities:
            if cleaned_rarity.lower() == excluded.strip().lower():
                logger.debug(f"Rareté '{rarity}' EXCLUE")
                return True
        
        logger.debug(f"Rareté '{rarity}' AUTORISÉE")
        return False
    
    def filter_items_by_specific_rarity(self, items: List[Dict[str, str]], rarity_column: str, target_rarity: str) -> Tuple[List[Dict[str, str]], List[int]]:
        """
        Filtre les objets pour ne garder que ceux d'une rareté spécifique.
        
        Args:
            items: Liste des objets à filtrer
            rarity_column: Nom de la colonne contenant la rareté
            target_rarity: Rareté cible à conserver
            
        Returns:
            Tuple[List[Dict[str, str]], List[int]]: (Liste des objets filtrés, Liste des indices originaux)
        """
        filtered_items = []
        original_indices = []
        
        target_rarity_lower = target_rarity.lower().strip()
        
        for i, item in enumerate(items):
            rarity = item.get(rarity_column, "").lower().strip()
            
            # Comparaison flexible pour différents formats de rareté
            if (rarity == target_rarity_lower or 
                rarity.replace(' ', '') == target_rarity_lower.replace(' ', '') or
                rarity in target_rarity_lower or 
                target_rarity_lower in rarity):
                
                filtered_items.append(item)
                original_indices.append(i)
                
                item_name = item.get("Nom de l'objet") or item.get("Nom en VO", "Inconnu")
                logger.debug(f"Objet inclus: {item_name} (Rareté: {rarity})")
        
        logger.info(f"Filtrage par rareté '{target_rarity}' terminé: {len(filtered_items)}/{len(items)} objets retenus")
        return filtered_items, original_indices

    def filter_items_by_price(self, items_with_indices: Tuple[List[Dict[str, str]], List[int]], price_column: str = "OM_PRICE") -> Tuple[List[Dict[str, str]], List[int]]:
        """
        Filtre les objets qui ont un prix valide et non nul.
        PRÉSERVE les indices originaux de la base de données complète.
        
        Args:
            items_with_indices: Tuple (liste des objets filtrés, liste des indices originaux)
            price_column: Nom de la colonne contenant le prix
            
        Returns:
            Tuple: (Liste des objets avec prix valide, Liste des indices originaux PRÉSERVÉS)
        """
        items, original_indices = items_with_indices
        
        filtered_items = []
        preserved_original_indices = []
        
        config = get_config()
        na_values = config['filtering']['na_values'] + ['0', '0.0', '-', 'null', 'None']
        
        logger.info(f"Filtrage par prix sur la colonne '{price_column}' avec préservation des indices")
        excluded_count = 0
        
        for i, item in enumerate(items):
            price_raw = item.get(price_column, "").strip()
            nom_objet = item.get('Nom de l\'objet', 'inconnu')
            original_index = original_indices[i]  # Récupérer l'index original correspondant
            
            # Vérifier si le prix est vide ou NA
            if not price_raw or price_raw in na_values:
                logger.debug(f"Objet exclu (pas de prix): {nom_objet} - prix: '{price_raw}' (ligne {original_index + 2})")
                excluded_count += 1
                continue
            
            # Essayer de convertir en nombre pour vérifier que c'est > 0
            try:
                # Nettoyer le prix (enlever 'po', espaces, etc.)
                clean_price = price_raw.replace(' po', '').replace('po', '').replace(',', '').strip()
                price_num = float(clean_price)
                
                if price_num > 0:
                    filtered_items.append(item)
                    preserved_original_indices.append(original_index)  # PRÉSERVER l'index original
                    logger.debug(f"Objet inclus: {nom_objet} - prix: {price_num} (ligne {original_index + 2})")
                else:
                    logger.debug(f"Objet exclu (prix = 0): {nom_objet} - prix: {price_num} (ligne {original_index + 2})")
                    excluded_count += 1
            except (ValueError, TypeError):
                # Si on ne peut pas convertir en nombre, on considère que c'est invalide
                logger.debug(f"Objet exclu (prix invalide): {nom_objet} - prix: '{price_raw}' (ligne {original_index + 2})")
                excluded_count += 1
                continue
        
        logger.info(f"Filtrage prix terminé: {len(filtered_items)} objets gardés, {excluded_count} objets exclus")
        logger.info(f"Indices originaux préservés: {preserved_original_indices[:5]}..." if len(preserved_original_indices) > 5 else f"Indices originaux préservés: {preserved_original_indices}")
        
        return filtered_items, preserved_original_indices
    
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
        logger.info(f"Indices sélectionnés: {selected_indices}")
        return selected_items, selected_indices
    
    def get_item_stats(self, items: List[Dict[str, str]], rarity_column: str = "RARETER") -> Dict[str, int]:
        """
        Retourne les statistiques sur les raretés des objets.
        
        Args:
            items: Liste des objets
            rarity_column: Nom de la colonne de rareté
            
        Returns:
            Dict[str, int]: Statistiques par rareté
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
        Valide et nettoie les données d'un objet selon tes colonnes.
        
        Args:
            item: Données brutes de l'objet
            
        Returns:
            Dict[str, str]: Données nettoyées et validées
        """
        validated_item = {}
        
        # Copier toutes les données existantes
        for key, value in item.items():
            validated_item[key] = str(value).strip() if value else ""
        
        # Noms d'objets
        nom_francais = validated_item.get("Nom de l'objet", "")
        nom_anglais = validated_item.get("Nom en VO", "")
        
        if nom_francais:
            validated_item["nom_display"] = nom_francais
        elif nom_anglais:
            validated_item["nom_display"] = nom_anglais
        else:
            validated_item["nom_display"] = "Objet mystérieux"
        
        # Rareté
        rarity_raw = validated_item.get("Rareté", "Commun")
        validated_item["rarity_display"] = normalize_rarity_name(rarity_raw)
        
        # Lien magique
        lien_raw = validated_item.get("Lien", "Non")
        if lien_raw.lower() in ['oui', 'yes', 'y']:
            validated_item["lien_display"] = "Oui"
        elif lien_raw.lower() in ['non', 'no', 'n']:
            validated_item["lien_display"] = "Non"
        else:
            validated_item["lien_display"] = lien_raw
        
        # PRIX - Utiliser la bonne colonne OM_PRICE
        price_om = validated_item.get("OM_PRICE", "").strip()
        
        if price_om and price_om not in ['0', '0.0', '', 'NA', 'N/A', 'null', '-']:
            try:
                price_num = float(price_om.replace(' po', '').replace('po', '').replace(',', '').strip())
                if price_num > 0:
                    validated_item["price_display"] = f"{price_num:.0f} po"
                else:
                    validated_item["price_display"] = "Prix non spécifié"
            except ValueError:
                # Si ce n'est pas un nombre, on garde tel quel
                validated_item["price_display"] = f"{price_om}"
        else:
            validated_item["price_display"] = "Prix non spécifié"
                
        return validated_item