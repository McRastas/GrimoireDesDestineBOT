# commands/maj_fiche/validation_system.py
import re
from typing import Dict, List, Tuple, Optional, Any


class TemplateValidator:
    """
    Système de validation et correction des templates de mise à jour de fiche D&D.
    Vérifie la conformité, détecte les erreurs et propose des corrections.
    """

    def __init__(self):
        # Patterns des éléments obligatoires du template
        self.REQUIRED_PATTERNS = {
            'nom_pj': r'Nom du PJ\s*:\s*(.+)',
            'classe': r'Classe\s*:\s*(.+)',
            'separator_pj_start': r'\*\*\s*/\s*=+\s*PJ\s*=+\s*\\\s*\*\*',
            'quete': r'\*\*Quête\s*:\*\*\s*(.+)',
            'solde_xp': r'\*\*Solde XP\s*:\*\*\s*(.+)',
            'gain_niveau': r'\*\*Gain de niveau\s*:\*\*',
            'pv_calcul': r'PV\s*:\s*(.+)',
            'capacites': r'\*\*¤\s*Capacités et sorts supplémentaires\s*:\*\*',
            'separator_pj_end': r'\*\*\s*\\\s*=+\s*PJ\s*=+\s*/\s*\*\*',
            'solde_final': r'\*\*¤\s*Solde\s*:\*\*',
            'fiche_maj': r'\*Fiche R20 à jour\.\*'
        }
        
        # Labels lisibles pour les sections
        self.SECTION_LABELS = {
            'nom_pj': 'Nom du PJ',
            'classe': 'Classe',
            'separator_pj_start': 'Séparateur début PJ',
            'quete': 'Section Quête',
            'solde_xp': 'Solde XP',
            'gain_niveau': 'Gain de niveau',
            'pv_calcul': 'Calcul PV',
            'capacites': 'Capacités et sorts',
            'separator_pj_end': 'Séparateur fin PJ',
            'solde_final': 'Solde final',
            'fiche_maj': 'Mention "Fiche R20 à jour"'
        }
        
        # Templates de correction pour les sections manquantes
        self.CORRECTION_TEMPLATES = {
            'separator_pj_start': '** / =======================  PJ  ========================= \\ **',
            'quete': '**Quête :** [TITRE_QUETE] + [NOM_MJ] ⁠- [LIEN_MESSAGE_RECOMPENSES]',
            'solde_xp': '**Solde XP :** [XP_ACTUELS] + [XP_OBTENUS] = [NOUVEAUX_XP]',
            'gain_niveau': '**Gain de niveau :** [NIVEAU_ACTUEL] → [NIVEAU_CIBLE]',
            'pv_calcul': 'PV : [ANCIENS_PV] + [PV_OBTENUS] = [NOUVEAUX_PV]',
            'capacites': '''**¤ Capacités et sorts supplémentaires :**
Nouvelle(s) capacité(s) :
- [CAPACITE_1]
- [CAPACITE_2]
Nouveau(x) sort(s) :
- [SORT_1]
- [SORT_2]
Sort remplacé :
- [ANCIEN_SORT] -> [NOUVEAU_SORT]''',
            'separator_pj_end': '** \\ =======================  PJ  ========================= / **',
            'solde_final': '**¤ Solde :**\n[ANCIEN_SOLDE] +/- [PO_RECUES_DEPENSEES] = [NOUVEAU_SOLDE]',
            'fiche_maj': '*Fiche R20 à jour.*'
        }

    def verify_template(self, content: str) -> Dict[str, Any]:
        """
        Vérifie si le contenu respecte le template de mise à jour de fiche.
        
        Args:
            content: Le contenu du template à vérifier
            
        Returns:
            Dict contenant le résultat de la vérification
        """
        result = {
            'score': 0,
            'total_checks': len(self.REQUIRED_PATTERNS),
            'sections_found': [],
            'sections_missing': [],
            'warnings': [],
            'suggestions': [],
            'details': {},
            'placeholders': [],
            'completion_percentage': 0.0
        }
        
        # Vérifier les éléments obligatoires
        for key, pattern in self.REQUIRED_PATTERNS.items():
            if re.search(pattern, content, re.IGNORECASE | re.MULTILINE):
                result['score'] += 1
                result['sections_found'].append(key)
                
                # Extraire les détails pour certains éléments
                match = re.search(pattern, content, re.IGNORECASE | re.MULTILINE)
                if match and match.groups():
                    result['details'][key] = match.group(1).strip()
            else:
                result['sections_missing'].append(key)
        
        # Calculer le pourcentage de completion
        result['completion_percentage'] = (result['score'] / result['total_checks']) * 100
        
        # Analyser la structure et donner des conseils
        self._analyze_structure(content, result)
        
        return result

    def _analyze_structure(self, content: str, result: Dict[str, Any]):
        """Analyse la structure du template et ajoute des avertissements/suggestions."""
        lines = content.split('\n')
        
        # 1. Vérifier les calculs XP
        self._check_xp_calculations(content, result)
        
        # 2. Vérifier les placeholders non remplis
        placeholders = re.findall(r'\[([A-Z_]+)\]', content)
        result['placeholders'] = list(set(placeholders))  # Supprimer les doublons
        
        if len(result['placeholders']) > 0:
            if len(result['placeholders']) > 10:
                result['warnings'].append(f"{len(result['placeholders'])} placeholders non remplis - Template très incomplet")
            elif len(result['placeholders']) > 5:
                result['warnings'].append(f"{len(result['placeholders'])} placeholders non remplis")
            else:
                result['suggestions'].append(f"Compléter les {len(result['placeholders'])} placeholders restants")
        
        # 3. Vérifier la longueur du message
        char_count = len(content)
        if char_count > 2000:
            result['warnings'].append(f"Message très long ({char_count} caractères) - Dépassera la limite Discord")
        elif char_count > 1800:
            result['warnings'].append(f"Message long ({char_count} caractères) - Proche de la limite Discord")
        elif char_count < 300:
            result['warnings'].append("Message très court - Vérifiez si toutes les sections sont présentes")
        
        # 4. Vérifier la cohérence des niveaux
        self._check_level_consistency(content, result)
        
        # 5. Vérifier la présence de sections optionnelles
        self._check_optional_sections(content, result)

    def _check_xp_calculations(self, content: str, result: Dict[str, Any]):
        """Vérifie les calculs d'XP dans le template."""
        xp_lines = [line for line in content.split('\n') if re.search(r'\*\*Solde XP\s*:\*\*', line, re.IGNORECASE)]
        
        if xp_lines:
            xp_line = xp_lines[0]
            
            # Chercher un pattern de calcul mathématique
            if re.search(r'\d+\s*\+\s*\d+\s*=\s*\d+', xp_line):
                # Vérifier si le calcul est correct
                calculation_match = re.search(r'(\d+)\s*\+\s*(\d+)\s*=\s*(\d+)', xp_line)
                if calculation_match:
                    a, b, c = map(int, calculation_match.groups())
                    if a + b != c:
                        result['warnings'].append(f"Erreur de calcul XP : {a} + {b} ≠ {c}")
                    else:
                        result['suggestions'].append("Calcul XP correct ✅")
            elif '[' in xp_line:
                result['suggestions'].append("XP non calculés - Placeholders à compléter")
            else:
                result['warnings'].append("Format de calcul XP non standard")

    def _check_level_consistency(self, content: str, result: Dict[str, Any]):
        """Vérifie la cohérence des niveaux mentionnés."""
        # Extraire les niveaux mentionnés
        level_patterns = [
            r'Niveau\s+(\d+)',
            r'niveau\s+(\d+)',
            r'→\s*(\d+)',
            r'PV_NIVEAU_(\d+)'
        ]
        
        levels_found = []
        for pattern in level_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            levels_found.extend([int(m) for m in matches])
        
        if len(set(levels_found)) > 2:
            unique_levels = sorted(set(levels_found))
            result['suggestions'].append(f"Niveaux détectés : {', '.join(map(str, unique_levels))}")

    def _check_optional_sections(self, content: str, result: Dict[str, Any]):
        """Vérifie la présence de sections optionnelles."""
        # Section Inventaire
        if re.search(r'\*\*¤\s*Inventaire\*\*', content, re.IGNORECASE):
            result['suggestions'].append("Section Inventaire présente ✅")
        
        # Section Marchand
        if re.search(r'Marchand', content, re.IGNORECASE):
            result['suggestions'].append("Section Marchand présente ✅")

    def generate_corrections(self, content: str, verification_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Génère des suggestions de correction et un template amélioré.
        
        Returns:
            Dict contenant les corrections et le template corrigé
        """
        corrections = {
            'automatic_fixes': [],
            'manual_corrections': [],
            'improvements': [],
            'corrected_template': content,
            'priority_issues': []
        }
        
        corrected_content = content.strip()
        
        # 1. Corrections automatiques des séparateurs
        corrected_content, auto_fixes = self._fix_separators(corrected_content, verification_result)
        corrections['automatic_fixes'].extend(auto_fixes)
        
        # 2. Corrections automatiques du formatage
        corrected_content, format_fixes = self._fix_formatting(corrected_content)
        corrections['automatic_fixes'].extend(format_fixes)
        
        # 3. Générer les corrections manuelles pour sections manquantes
        corrections['manual_corrections'] = self._generate_manual_corrections(verification_result)
        
        # 4. Suggestions d'amélioration
        corrections['improvements'] = self._generate_improvements(content, verification_result)
        
        # 5. Identifier les problèmes prioritaires
        corrections['priority_issues'] = self._identify_priority_issues(verification_result)
        
        corrections['corrected_template'] = corrected_content
        
        return corrections

    def _fix_separators(self, content: str, verification_result: Dict[str, Any]) -> Tuple[str, List[str]]:
        """Corrige automatiquement les séparateurs manquants."""
        fixes = []
        corrected = content
        
        # Séparateur de début PJ
        if 'separator_pj_start' in verification_result['sections_missing']:
            if 'Classe' in corrected:
                corrected = re.sub(
                    r'(Classe\s*:\s*.+)',
                    r'\1\n\n** / =======================  PJ  ========================= \\ **',
                    corrected,
                    count=1
                )
                fixes.append("Ajout du séparateur de début PJ")
        
        # Séparateur de fin PJ
        if 'separator_pj_end' in verification_result['sections_missing']:
            # Insérer avant le solde final
            if re.search(r'\*\*¤\s*Solde\s*:\*\*', corrected):
                corrected = re.sub(
                    r'(\*\*¤\s*Solde\s*:\*\*)',
                    r'** \\ =======================  PJ  ========================= / **\n\n\1',
                    corrected,
                    count=1
                )
                fixes.append("Ajout du séparateur de fin PJ")
        
        return corrected, fixes

    def _fix_formatting(self, content: str) -> Tuple[str, List[str]]:
        """Corrige le formatage du template."""
        fixes = []
        corrected = content
        
        # Normaliser les espaces multiples
        if re.search(r'\n{3,}', corrected):
            corrected = re.sub(r'\n{3,}', '\n\n', corrected)
            fixes.append("Normalisation des espaces multiples")
        
        # Normaliser les séparateurs existants
        # Séparateur début PJ
        old_start_pattern = r'\*\*\s*/\s*=+\s*PJ\s*=+\s*\\\s*\*\*'
        new_start = '** / =======================  PJ  ========================= \\ **'
        if re.search(old_start_pattern, corrected) and new_start not in corrected:
            corrected = re.sub(old_start_pattern, new_start, corrected)
            fixes.append("Normalisation du séparateur de début PJ")
        
        # Séparateur fin PJ
        old_end_pattern = r'\*\*\s*\\\s*=+\s*PJ\s*=+\s*/\s*\*\*'
        new_end = '** \\ =======================  PJ  ========================= / **'
        if re.search(old_end_pattern, corrected) and new_end not in corrected:
            corrected = re.sub(old_end_pattern, new_end, corrected)
            fixes.append("Normalisation du séparateur de fin PJ")
        
        # Normaliser la mention finale
        if re.search(r'\*\s*Fiche\s+R20\s+à\s+jour\.?\s*\*', corrected, re.IGNORECASE):
            corrected = re.sub(
                r'\*\s*Fiche\s+R20\s+à\s+jour\.?\s*\*',
                '*Fiche R20 à jour.*',
                corrected,
                flags=re.IGNORECASE
            )
            fixes.append("Normalisation de la mention finale")
        
        return corrected, fixes

    def _generate_manual_corrections(self, verification_result: Dict[str, Any]) -> List[Dict[str, str]]:
        """Génère la liste des corrections manuelles nécessaires."""
        corrections = []
        
        for missing_section in verification_result['sections_missing']:
            if missing_section in self.CORRECTION_TEMPLATES:
                corrections.append({
                    'section': self.SECTION_LABELS.get(missing_section, missing_section),
                    'template': self.CORRECTION_TEMPLATES[missing_section],
                    'position': self._get_insertion_position(missing_section),
                    'priority': self._get_correction_priority(missing_section)
                })
        
        # Trier par priorité
        priority_order = {'Critique': 0, 'Haute': 1, 'Moyenne': 2, 'Basse': 3}
        corrections.sort(key=lambda x: priority_order.get(x['priority'], 4))
        
        return corrections

    def _generate_improvements(self, content: str, verification_result: Dict[str, Any]) -> List[Dict[str, str]]:
        """Génère des suggestions d'amélioration."""
        improvements = []
        
        # Amélioration de la longueur
        char_count = len(content)
        if char_count > 1800:
            improvements.append({
                'type': 'Longueur du message',
                'description': "Considérer diviser en plusieurs messages pour Discord",
                'priority': 'Moyenne'
            })
        
        # Amélioration des placeholders
        placeholder_count = len(verification_result['placeholders'])
        if placeholder_count > 5:
            improvements.append({
                'type': 'Placeholders',
                'description': f"Compléter les {placeholder_count} placeholders pour finaliser le template",
                'priority': 'Haute'
            })
        elif placeholder_count > 0:
            improvements.append({
                'type': 'Placeholders',
                'description': f"Compléter les derniers {placeholder_count} placeholders",
                'priority': 'Moyenne'
            })
        
        # Amélioration des calculs
        if any('calcul' in w.lower() for w in verification_result['warnings']):
            improvements.append({
                'type': 'Calculs',
                'description': "Vérifier et corriger les calculs d'XP et PV",
                'priority': 'Haute'
            })
        
        return improvements

    def _identify_priority_issues(self, verification_result: Dict[str, Any]) -> List[str]:
        """Identifie les problèmes prioritaires à résoudre."""
        priority_issues = []
        
        # Sections critiques manquantes
        critical_sections = ['nom_pj', 'classe', 'quete', 'solde_xp']
        missing_critical = [s for s in critical_sections if s in verification_result['sections_missing']]
        
        if missing_critical:
            priority_issues.append(f"Sections critiques manquantes : {', '.join([self.SECTION_LABELS[s] for s in missing_critical])}")
        
        # Erreurs de calcul
        calc_warnings = [w for w in verification_result['warnings'] if 'calcul' in w.lower()]
        if calc_warnings:
            priority_issues.extend(calc_warnings)
        
        # Template très incomplet
        if verification_result['completion_percentage'] < 50:
            priority_issues.append("Template très incomplet - Moins de 50% des sections présentes")
        
        return priority_issues

    def _get_insertion_position(self, section: str) -> str:
        """Retourne la position d'insertion recommandée pour une section."""
        positions = {
            'separator_pj_start': 'Après la ligne Classe',
            'quete': 'Après le séparateur de début PJ',
            'solde_xp': 'Après la section Quête',
            'gain_niveau': 'Après le Solde XP',
            'pv_calcul': 'Dans la section Gain de niveau',
            'capacites': 'Après le calcul PV',
            'separator_pj_end': 'Avant le solde final',
            'solde_final': 'Avant la mention finale',
            'fiche_maj': 'À la fin du template'
        }
        return positions.get(section, 'Position appropriée selon le template')

    def _get_correction_priority(self, section: str) -> str:
        """Retourne la priorité de correction pour une section."""
        priorities = {
            'nom_pj': 'Critique',
            'classe': 'Critique',
            'quete': 'Critique',
            'solde_xp': 'Haute',
            'gain_niveau': 'Haute',
            'pv_calcul': 'Haute',
            'capacites': 'Moyenne',
            'separator_pj_start': 'Moyenne',
            'separator_pj_end': 'Moyenne',
            'solde_final': 'Moyenne',
            'fiche_maj': 'Basse'
        }
        return priorities.get(section, 'Moyenne')

    def get_validation_summary(self, verification_result: Dict[str, Any]) -> str:
        """Génère un résumé textuel de la validation."""
        completion = verification_result['completion_percentage']
        
        if completion >= 90:
            return f"✅ Template excellent ({completion:.0f}% complet)"
        elif completion >= 70:
            return f"🟡 Template bon ({completion:.0f}% complet) - Quelques ajustements recommandés"
        elif completion >= 50:
            return f"🟠 Template incomplet ({completion:.0f}% complet) - Corrections nécessaires"
        else:
            return f"❌ Template très incomplet ({completion:.0f}% complet) - Reconstruction recommandée"