# commands/parchemin/spell_selector_v2.py
"""
Sélecteur de sorts adapté pour les parchemins D&D 5e.
Structure inspirée de boutique/item_selector_v2.py
"""

import random
import logging
from typing import List, Dict, Optional, Tuple
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)

class SpellSelectorV2:
    """
    Classe pour sélectionner des sorts aléatoires - équivalent d'ItemSelectorV2 pour les sorts.
    """
    
    def __init__(self, excluded_levels: List[str] = None):
        """
        Initialise le sélecteur de sorts.
        Même structure que ItemSelectorV2.__init__ mais pour les niveaux exclus.
        
        Args:
            excluded_levels: Liste des niveaux à exclure (comme excluded_rarities)
        """
        self.excluded_levels = excluded_levels or []
        
        # Convertir les niveaux exclus en entiers (comme normalisation des raretés)
        self.excluded_levels_int = []
        for level in self.excluded_levels:
            try:
                self.excluded_levels_int.append(int(level))
            except ValueError:
                logger.warning(f"Niveau exclu invalide: {level}")
        
        # Log de debug (comme boutique)
        logger.info(f"Niveaux à exclure: {self.excluded_levels}")
        logger.info(f"Niveaux exclus normalisés: {self.excluded_levels_int}")
    
    def _is_level_excluded(self, level: int) -> bool:
        """
        Vérifie si un niveau doit être exclu.
        Équivalent de _is_rarity_excluded dans boutique.
        
        Args:
            level: Niveau du sort à vérifier
            
        Returns:
            bool: True si le niveau doit être exclu
        """
        if level in self.excluded_levels_int:
            logger.debug(f"Niveau {level} EXCLU")
            return True
        
        logger.debug(f"Niveau {level} AUTORISÉ")
        return False
    
    def filter_spells_by_level_range(self, spells: List[Dict], level_range: Tuple[int, int]) -> Tuple[List[Dict], List[int]]:
        """
        Filtre les sorts par plage de niveaux.
        Équivalent de filter_items_by_specific_rarity mais pour les niveaux.
        
        Args:
            spells: Liste des sorts à filtrer
            level_range: Tuple (niveau_min, niveau_max) inclusive
            
        Returns:
            Tuple[List[Dict], List[int]]: (Sorts filtrés, indices originaux)
        """
        filtered_spells = []
        original_indices = []
        
        min_level, max_level = level_range
        
        for i, spell in enumerate(spells):
            spell_level = spell.get('level', 0)
            
            if min_level <= spell_level <= max_level:
                filtered_spells.append(spell)
                original_indices.append(i)
                
                spell_name = spell.get('name', 'Sort inconnu')
                logger.debug(f"Sort inclus: {spell_name} (Niveau: {spell_level})")
        
        logger.info(f"Filtrage par niveau {min_level}-{max_level} terminé: {len(filtered_spells)}/{len(spells)} sorts retenus")
        return filtered_spells, original_indices
    
    def filter_spells_by_school(self, spells_with_indices: Tuple[List[Dict], List[int]], school: str) -> Tuple[List[Dict], List[int]]:
        """
        Filtre les sorts par école de magie.
        Équivalent de filter_items_by_price mais pour l'école.
        
        Args:
            spells_with_indices: Tuple (sorts, indices originaux)
            school: École de magie à filtrer
            
        Returns:
            Tuple[List[Dict], List[int]]: (Sorts filtrés, indices originaux préservés)
        """
        spells, original_indices = spells_with_indices
        filtered_spells = []
        preserved_original_indices = []
        excluded_count = 0
        
        school_lower = school.lower().strip()
        
        for spell, original_index in zip(spells, original_indices):
            spell_name = spell.get('name', 'Sort inconnu')
            spell_school = spell.get('school', '').lower().strip()
            
            if spell_school == school_lower:
                filtered_spells.append(spell)
                preserved_original_indices.append(original_index)  # PRÉSERVER l'index original
                logger.debug(f"Sort inclus: {spell_name} - école: {spell_school}")
            else:
                logger.debug(f"Sort exclu (école différente): {spell_name} - école: {spell_school}")
                excluded_count += 1
        
        logger.info(f"Filtrage école '{school}' terminé: {len(filtered_spells)} sorts gardés, {excluded_count} sorts exclus")
        return filtered_spells, preserved_original_indices
    
    def filter_spells_by_class(self, spells_with_indices: Tuple[List[Dict], List[int]], character_class: str) -> Tuple[List[Dict], List[int]]:
        """
        Filtre les sorts par classe de personnage.
        Adaptation du filtrage de boutique pour les classes.
        
        Args:
            spells_with_indices: Tuple (sorts, indices originaux)
            character_class: Classe de personnage à filtrer
            
        Returns:
            Tuple[List[Dict], List[int]]: (Sorts filtrés, indices originaux préservés)
        """
        spells, original_indices = spells_with_indices
        filtered_spells = []
        preserved_original_indices = []
        excluded_count = 0
        
        class_lower = character_class.lower().strip()
        
        for spell, original_index in zip(spells, original_indices):
            spell_name = spell.get('name', 'Sort inconnu')
            spell_classes = [cls.lower().strip() for cls in spell.get('classes', [])]
            
            if class_lower in spell_classes:
                filtered_spells.append(spell)
                preserved_original_indices.append(original_index)  # PRÉSERVER l'index original
                logger.debug(f"Sort inclus: {spell_name} - classes: {spell_classes}")
            else:
                logger.debug(f"Sort exclu (classe non trouvée): {spell_name} - classes: {spell_classes}")
                excluded_count += 1
        
        logger.info(f"Filtrage classe '{character_class}' terminé: {len(filtered_spells)} sorts gardés, {excluded_count} sorts exclus")
        return filtered_spells, preserved_original_indices
    
    def filter_spells_by_ritual(self, spells_with_indices: Tuple[List[Dict], List[int]], is_ritual: bool) -> Tuple[List[Dict], List[int]]:
        """
        Filtre les sorts par statut rituel.
        Nouveau filtre spécifique aux sorts.
        
        Args:
            spells_with_indices: Tuple (sorts, indices originaux)
            is_ritual: True pour rituels uniquement, False pour non-rituels
            
        Returns:
            Tuple[List[Dict], List[int]]: (Sorts filtrés, indices originaux préservés)
        """
        spells, original_indices = spells_with_indices
        filtered_spells = []
        preserved_original_indices = []
        excluded_count = 0
        
        for spell, original_index in zip(spells, original_indices):
            spell_name = spell.get('name', 'Sort inconnu')
            spell_ritual = spell.get('ritual', False)
            
            if spell_ritual == is_ritual:
                filtered_spells.append(spell)
                preserved_original_indices.append(original_index)  # PRÉSERVER l'index original
                logger.debug(f"Sort inclus: {spell_name} - rituel: {spell_ritual}")
            else:
                logger.debug(f"Sort exclu (rituel différent): {spell_name} - rituel: {spell_ritual}")
                excluded_count += 1
        
        ritual_text = "rituels" if is_ritual else "non-rituels"
        logger.info(f"Filtrage sorts {ritual_text} terminé: {len(filtered_spells)} sorts gardés, {excluded_count} sorts exclus")
        return filtered_spells, preserved_original_indices
    
    def filter_spells_by_excluded_levels(self, spells: List[Dict]) -> Tuple[List[Dict], List[int]]:
        """
        Filtre les sorts en excluant les niveaux configurés.
        Équivalent de filter_items_by_rarity dans boutique.
        
        Args:
            spells: Liste des sorts à filtrer
            
        Returns:
            Tuple[List[Dict], List[int]]: (Sorts filtrés, indices originaux)
        """
        filtered_spells = []
        original_indices = []
        
        for i, spell in enumerate(spells):
            spell_level = spell.get('level', 0)
            spell_name = spell.get('name', 'Sort inconnu')
            
            if not self._is_level_excluded(spell_level):
                filtered_spells.append(spell)
                original_indices.append(i)
                logger.debug(f"Sort inclus: {spell_name} (Niveau: {spell_level})")
            else:
                logger.debug(f"Sort exclu (niveau banni): {spell_name} (Niveau: {spell_level})")
        
        logger.info(f"Filtrage niveaux exclus terminé: {len(filtered_spells)}/{len(spells)} sorts retenus")
        return filtered_spells, original_indices
    
    def select_random_spells(self, spells_with_indices: Tuple[List[Dict], List[int]], min_count: int = 1, max_count: int = 15) -> Tuple[List[Dict], List[int]]:
        """
        Sélectionne un nombre aléatoire de sorts avec leurs indices originaux.
        Même structure que select_random_items dans boutique.
        
        Args:
            spells_with_indices: Tuple (liste des sorts, liste des indices originaux)
            min_count: Nombre minimum de sorts à sélectionner
            max_count: Nombre maximum de sorts à sélectionner
            
        Returns:
            Tuple: (Liste des sorts sélectionnés, Liste des indices originaux correspondants)
        """
        spells, original_indices = spells_with_indices
        
        if not spells:
            raise ValueError("Aucun sort disponible pour la sélection")
        
        # Déterminer le nombre de sorts à sélectionner (même logique que boutique)
        available_count = len(spells)
        target_count = random.randint(min_count, min(max_count, available_count))
        
        if target_count > available_count:
            logger.warning(f"Pas assez de sorts disponibles: {available_count} < {target_count}")
            target_count = available_count
        
        # Créer une liste de tuples (sort, index_original) (même logique que boutique)
        spells_with_original_indices = list(zip(spells, original_indices))
        
        # Sélection aléatoire sans remise (même logique que boutique)
        selected_spells_with_indices = random.sample(spells_with_original_indices, target_count)
        
        # Séparer les sorts et les indices (même logique que boutique)
        selected_spells = [spell for spell, _ in selected_spells_with_indices]
        selected_indices = [index for _, index in selected_spells_with_indices]
        
        logger.info(f"Sélection aléatoire: {len(selected_spells)} sorts choisis")
        logger.info(f"Indices sélectionnés: {selected_indices}")
        return selected_spells, selected_indices
    
    def get_spell_stats(self, spells: List[Dict]) -> Dict[str, int]:
        """
        Retourne les statistiques sur les niveaux des sorts.
        Équivalent de get_item_stats dans boutique.
        
        Args:
            spells: Liste des sorts
            
        Returns:
            Dict[str, int]: Statistiques par niveau
        """
        stats = {}
        
        for spell in spells:
            level = spell.get('level', 0)
            
            # Convertir en format lisible (comme normalize_rarity_name)
            if level == 0:
                readable_level = "Tours de magie"
            else:
                readable_level = f"Niveau {level}"
            
            stats[readable_level] = stats.get(readable_level, 0) + 1
        
        return stats
    
    def search_spells(self, spells: List[Dict], query: str, max_results: int = 10, min_similarity: float = 0.4) -> List[Dict]:
        """
        Recherche floue dans les sorts.
        Équivalent de la recherche dans boutique/search_command.py mais intégré.
        
        Args:
            spells: Liste des sorts
            query: Terme de recherche
            max_results: Nombre maximum de résultats
            min_similarity: Seuil de similarité minimum
            
        Returns:
            List[Dict]: Sorts correspondants triés par pertinence
        """
        if not query or not spells:
            return []
        
        results = []
        query_lower = query.lower().strip()
        
        for spell in spells:
            # Calcul de la similarité avec le nom
            spell_name = spell.get('name', '').lower()
            name_similarity = SequenceMatcher(None, query_lower, spell_name).ratio()
            
            # Calcul de la similarité avec l'école
            spell_school = spell.get('school', '').lower()
            school_similarity = SequenceMatcher(None, query_lower, spell_school).ratio()
            
            # Calcul de la similarité avec les classes
            max_class_similarity = 0
            for cls in spell.get('classes', []):
                cls_similarity = SequenceMatcher(None, query_lower, cls.lower()).ratio()
                max_class_similarity = max(max_class_similarity, cls_similarity)
            
            # Score global (pondération: nom 70%, école 20%, classe 10%)
            total_similarity = (name_similarity * 0.7 + 
                              school_similarity * 0.2 + 
                              max_class_similarity * 0.1)
            
            # Bonus si le terme est contenu dans le nom
            if query_lower in spell_name:
                total_similarity += 0.3
            
            # Ajouter si au-dessus du seuil
            if total_similarity >= min_similarity:
                results.append({
                    'spell': spell,
                    'similarity': total_similarity
                })
        
        # Trier par similarité décroissante
        results.sort(key=lambda x: x['similarity'], reverse=True)
        
        # Retourner les meilleurs résultats
        best_results = results[:max_results]
        return [result['spell'] for result in best_results]
    
    def validate_spell_data(self, spell: Dict) -> Dict:
        """
        Valide et nettoie les données d'un sort.
        Équivalent de validate_item_data dans boutique.
        
        Args:
            spell: Données du sort à valider
            
        Returns:
            Dict: Sort validé et nettoyé
        """
        validated_spell = spell.copy()
        
        # Validation du nom (essentiel)
        if not validated_spell.get('name'):
            validated_spell['name'] = 'Sort mystérieux'
        
        # Validation du niveau
        try:
            level = int(validated_spell.get('level', 0))
            validated_spell['level'] = max(0, min(9, level))  # Clamper entre 0 et 9
        except (ValueError, TypeError):
            validated_spell['level'] = 0
        
        # Validation de l'école
        if not validated_spell.get('school'):
            validated_spell['school'] = 'Inconnue'
        
        # Validation des classes
        if not isinstance(validated_spell.get('classes'), list):
            validated_spell['classes'] = []
        
        # Validation du rituel
        validated_spell['ritual'] = bool(validated_spell.get('ritual', False))
        
        return validated_spell




