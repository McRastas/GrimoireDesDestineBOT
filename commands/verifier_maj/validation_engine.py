"""Moteur de validation et correction des templates."""

import re
from typing import Dict, Any, List
from ..maj_fiche.validation_system import TemplateValidator

class ValidationEngine:
    """Moteur principal de validation des templates."""
    
    def __init__(self):
        # Réutiliser le validateur de maj_fiche
        self.base_validator = TemplateValidator()
    
    def validate_template(self, content: str, mode_correction: str = "auto") -> Dict[str, Any]:
        """Valide un template et génère les corrections si nécessaire."""
        
        # 1. Validation de base avec le système maj_fiche
        base_result = self.base_validator.verify_template(content)
        
        # 2. Enrichir avec des infos spécifiques à verifier_maj
        result = {
            **base_result,
            'mode_correction': mode_correction,
            'corrections_generated': False,
            'corrected_content': None
        }
        
        # 3. Générer les corrections si demandé
        if mode_correction in ["auto", "advanced"]:
            corrected = self._generate_corrections(content, base_result, mode_correction)
            if corrected != content:
                result['corrections_generated'] = True
                result['corrected_content'] = corrected
        
        return result
    
    def _generate_corrections(self, content: str, validation_result: Dict, mode: str) -> str:
        """Génère des corrections automatiques."""
        corrected = content
        
        # Réutiliser la logique du validateur existant
        if hasattr(self.base_validator, 'generate_corrections'):
            corrected = self.base_validator.generate_corrections(content, validation_result)
        
        # Corrections supplémentaires pour mode "advanced"
        if mode == "advanced":
            corrected = self._apply_advanced_corrections(corrected)
        
        return corrected
    
    def _apply_advanced_corrections(self, content: str) -> str:
        """Applique des corrections avancées."""
        # Corrections spécifiques au mode avancé
        # Uniformiser les séparateurs
        content = re.sub(r'-{2,}', '─────────────────────', content)
        
        # Optimiser le formatage
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        return content