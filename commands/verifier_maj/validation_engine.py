# commands/verifier_maj/validation_engine.py
"""Moteur de validation et correction des templates."""

import re
import logging
from typing import Dict, Any, List
from ..maj_fiche.validation_system import TemplateValidator

logger = logging.getLogger(__name__)


class ValidationEngine:
    """Moteur principal de validation des templates."""
    
    def __init__(self):
        # Réutiliser le validateur de maj_fiche
        self.base_validator = TemplateValidator()
    
    def validate_template(self, content: str, mode_correction: str = "auto") -> Dict[str, Any]:
        """Valide un template et génère les corrections si nécessaire."""
        
        try:
            # 1. Validation de base avec le système maj_fiche
            base_result = self.base_validator.verify_template(content)
            
            # 2. Enrichir avec des infos spécifiques à verifier_maj
            result = {
                **base_result,
                'mode_correction': mode_correction,
                'corrections_generated': False,
                'corrected_content': None,
                'original_length': len(content),
                'analysis_timestamp': None
            }
            
            # 3. Ajouter des analyses supplémentaires
            self._add_enhanced_analysis(content, result)
            
            # 4. Générer les corrections si demandé
            if mode_correction in ["auto", "advanced"]:
                corrected = self._generate_corrections(content, base_result, mode_correction)
                if corrected and corrected != content:
                    result['corrections_generated'] = True
                    result['corrected_content'] = corrected
                    result['corrected_length'] = len(corrected)
            
            logger.info(f"Validation terminée: {result['score']}/{result['total_checks']} sections")
            return result
            
        except Exception as e:
            logger.error(f"Erreur lors de la validation: {e}")
            # Retourner un résultat d'erreur minimal
            return {
                'score': 0,
                'total_checks': 7,  # Nombre approximatif de sections
                'sections_found': [],
                'sections_missing': ['erreur_validation'],
                'warnings': [f"Erreur lors de la validation: {str(e)}"],
                'suggestions': ['Réessayer la validation'],
                'details': {},
                'placeholders': [],
                'completion_percentage': 0.0,
                'mode_correction': mode_correction,
                'corrections_generated': False,
                'corrected_content': None
            }
    
    def _add_enhanced_analysis(self, content: str, result: Dict[str, Any]):
        """Ajoute des analyses supplémentaires spécifiques à verifier_maj."""
        
        # Analyser la longueur du contenu
        length = len(content)
        if length > 2000:
            result['warnings'].append(f"Template très long ({length} caractères)")
        elif length < 100:
            result['warnings'].append(f"Template très court ({length} caractères)")
        
        # Analyser la structure des séparateurs
        separators = re.findall(r'[-─═]+', content)
        if len(separators) < 2:
            result['suggestions'].append("Ajouter des séparateurs pour structurer le template")
        
        # Analyser les formules mathématiques
        math_patterns = re.findall(r'\d+\s*[+\-×*÷/]\s*\d+', content)
        if math_patterns:
            result['suggestions'].append(f"Vérifier les {len(math_patterns)} calculs détectés")
        
        # Analyser les mentions de niveau
        level_mentions = re.findall(r'niveau\s+(\d+)', content, re.IGNORECASE)
        if level_mentions:
            levels = [int(x) for x in level_mentions if x.isdigit()]
            if levels:
                min_level, max_level = min(levels), max(levels)
                if max_level - min_level > 3:
                    result['warnings'].append(f"Écart de niveau important détecté ({min_level}-{max_level})")
    
    def _generate_corrections(self, content: str, validation_result: Dict, mode: str) -> str:
        """Génère des corrections automatiques."""
        
        try:
            corrected = content
            
            # 1. Corrections de base via le validateur maj_fiche
            if hasattr(self.base_validator, 'generate_corrections'):
                try:
                    base_corrected = self.base_validator.generate_corrections(content, validation_result)
                    if base_corrected:
                        corrected = base_corrected
                except Exception as e:
                    logger.warning(f"Erreur lors des corrections de base: {e}")
            
            # 2. Corrections spécifiques à verifier_maj
            corrected = self._apply_basic_corrections(corrected)
            
            # 3. Corrections avancées pour mode "advanced"
            if mode == "advanced":
                corrected = self._apply_advanced_corrections(corrected)
            
            return corrected
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération des corrections: {e}")
            return content  # Retourner le contenu original en cas d'erreur
    
    def _apply_basic_corrections(self, content: str) -> str:
        """Applique des corrections de base."""
        
        # Nettoyer les espaces multiples
        content = re.sub(r' {2,}', ' ', content)
        
        # Nettoyer les retours à la ligne multiples
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        # Uniformiser les séparateurs basiques
        content = re.sub(r'-{3,}', '───────────────────', content)
        
        # Corriger les espaces autour des deux-points
        content = re.sub(r'\s*:\s*', ': ', content)
        
        # Corriger la capitalisation des mots-clés courants
        keywords = ['nom', 'classe', 'niveau', 'xp', 'pv', 'ca', 'quête']
        for keyword in keywords:
            pattern = rf'\b{keyword}\b'
            replacement = keyword.capitalize()
            content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
        
        return content
    
    def _apply_advanced_corrections(self, content: str) -> str:
        """Applique des corrections avancées."""
        
        # Uniformiser les séparateurs décoratifs
        content = re.sub(r'[─═]{2,}', '═══════════════════════════════════════', content)
        
        # Améliorer le formatage des sections
        content = re.sub(r'^([A-Z][^:\n]+):(.*)$', r'**\1:**\2', content, flags=re.MULTILINE)
        
        # Optimiser les listes
        content = re.sub(r'^\s*[-*•]\s*', '• ', content, flags=re.MULTILINE)
        
        # Améliorer les formules de calcul
        content = re.sub(r'(\d+)\s*\+\s*(\d+)\s*=\s*(\d+)', r'\1 + \2 = \3', content)
        content = re.sub(r'(\d+)\s*-\s*(\d+)\s*=\s*(\d+)', r'\1 - \2 = \3', content)
        
        # Optimiser la présentation des niveaux
        content = re.sub(r'niveau\s+(\d+)', r'Niveau \1', content, flags=re.IGNORECASE)
        
        # Améliorer les sections de capacités
        content = re.sub(r'capacité[s]?\s*:', 'Capacités acquises:', content, flags=re.IGNORECASE)
        
        return content
    
    def quick_validate(self, content: str) -> bool:
        """Validation rapide pour vérifier si le contenu est un template valide."""
        
        # Vérifications basiques
        if not content or len(content.strip()) < 50:
            return False
        
        # Chercher des mots-clés essentiels
        essential_keywords = ['nom', 'classe', 'niveau', 'xp']
        found_keywords = 0
        
        for keyword in essential_keywords:
            if re.search(rf'\b{keyword}\b', content, re.IGNORECASE):
                found_keywords += 1
        
        return found_keywords >= 2
    
    def get_validation_summary(self, result: Dict[str, Any]) -> str:
        """Génère un résumé textuel de la validation."""
        
        completion = result.get('completion_percentage', 0)
        score = result.get('score', 0)
        total = result.get('total_checks', 1)
        
        if completion >= 80:
            status = "✅ Excellent"
        elif completion >= 60:
            status = "⚠️ Correct"
        else:
            status = "❌ À améliorer"
        
        summary = f"{status} - {score}/{total} sections ({completion:.1f}%)"
        
        if result.get('corrections_generated'):
            summary += " - Corrections disponibles"
        
        return summary