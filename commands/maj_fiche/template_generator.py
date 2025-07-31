# commands/maj_fiche/template_generator.py
from typing import Optional, Dict, List, Tuple


class TemplateGenerator:
    """
    Générateur de templates de mise à jour de fiche D&D.
    Gère la création des différentes sections et le formatage du contenu.
    """

    def __init__(self):
        # Table d'XP par niveau D&D 5e
        self.XP_TABLE = {
            1: 0, 2: 300, 3: 900, 4: 2700, 5: 6500,
            6: 14000, 7: 23000, 8: 34000, 9: 48000, 10: 64000,
            11: 85000, 12: 100000, 13: 120000, 14: 140000, 15: 165000,
            16: 195000, 17: 225000, 18: 265000, 19: 305000, 20: 355000
        }

        # PV par niveau selon la classe
        self.HP_PER_LEVEL = {
            "Guerrier": 10, "Rôdeur": 10, "Paladin": 10, "Barbare": 12,
            "Barde": 8, "Ensorceleur": 6, "Magicien": 6, "Druide": 8,
            "Clerc": 8, "Moine": 8, "Roublard": 8, "Occultiste": 8
        }

        # Suggestions par classe et niveau
        self.CLASS_FEATURES = {
            "Guerrier": {
                2: ["Action Surge", "Second souffle récupéré"],
                3: ["Archétype martial", "Manœuvres/Sorts selon l'archétype"],
                4: ["Amélioration de caractéristique", "Don optionnel"],
                5: ["Attaque supplémentaire", "Maîtrise accrue"]
            },
            "Magicien": {
                2: ["École de magie", "Sorts d'école gratuits"],
                3: ["Sorts de niveau 2", "Emplacements niveau 2"],
                4: ["Amélioration de caractéristique", "Tour de magie supplémentaire"],
                5: ["Sorts de niveau 3", "Emplacements niveau 3"]
            },
            "Clerc": {
                2: ["Canal divin", "Sorts de domaine"],
                3: ["Sorts de niveau 2", "Emplacements niveau 2"],
                4: ["Amélioration de caractéristique", "Tour de magie supplémentaire"],
                5: ["Sorts de niveau 3", "Sorts de domaine niveau 3"]
            }
            # Autres classes à compléter selon besoins
        }

        self.SPELL_SUGGESTIONS = {
            "Magicien": {
                2: ["Flèche acide de Melf", "Rayon ardent", "Toile d'araignée"],
                3: ["Boule de feu", "Éclair", "Vol", "Contresort"]
            },
            "Clerc": {
                2: ["Aide", "Immobiliser un humanoïde", "Silence"],
                3: ["Dissipation de la magie", "Esprits gardiens", "Mot de guérison de groupe"]
            }
        }

    def generate_full_template(
        self,
        nom_pj: str,
        classe: str,
        niveau_actuel: Optional[int] = None,
        niveau_cible: Optional[int] = None,
        titre_quete: Optional[str] = None,
        mj: Optional[str] = None,
        xp_actuels: Optional[int] = None,
        xp_obtenus: Optional[int] = None,
        include_marchand: bool = False,
        include_inventaire: bool = True
    ) -> str:
        """
        Génère le template complet de mise à jour de fiche.
        
        Returns:
            str: Le template formaté prêt à utiliser
        """
        sections = []
        
        # En-tête avec informations de base
        sections.append(self._generate_header(nom_pj, classe))
        
        # Séparateur de début
        sections.append("** / =======================  PJ  ========================= \\ **")
        
        # Section Quête
        sections.append(self._generate_quest_section(titre_quete, mj))
        
        # Section XP
        sections.append(self._generate_xp_section(xp_actuels, xp_obtenus, niveau_actuel, niveau_cible))
        
        # Section Gain de niveau
        sections.append(self._generate_level_section(classe, niveau_actuel, niveau_cible))
        
        # Section PV
        sections.append(self._generate_hp_section(classe, niveau_actuel, niveau_cible))
        
        # Section Capacités et sorts
        sections.append(self._generate_abilities_section(classe, niveau_cible))
        
        # Section Inventaire (optionnelle)
        if include_inventaire:
            sections.append(self._generate_inventory_section(titre_quete))
        
        # Séparateur de fin PJ
        sections.append("** \\ =======================  PJ  ========================= / **")
        
        # Section Marchand (optionnelle)
        if include_marchand:
            sections.append(self._generate_merchant_section())
        
        # Section Solde final
        sections.append(self._generate_balance_section())
        
        # Mention finale
        sections.append("*Fiche R20 à jour.*")
        
        return "\n\n".join(filter(None, sections))

    def _generate_header(self, nom_pj: str, classe: str) -> str:
        """Génère l'en-tête du template."""
        return f"Nom du PJ : {nom_pj}\nClasse : {classe}"

    def _generate_quest_section(self, titre_quete: Optional[str], mj: Optional[str]) -> str:
        """Génère la section Quête avec pré-remplissage intelligent."""
        if titre_quete and mj:
            return f"**Quête :** {titre_quete} + {mj} ⁠- [LIEN_MESSAGE_RECOMPENSES]"
        elif titre_quete:
            return f"**Quête :** {titre_quete} + [NOM_MJ] ⁠- [LIEN_MESSAGE_RECOMPENSES]"
        elif mj:
            return f"**Quête :** [TITRE_QUETE] + {mj} ⁠- [LIEN_MESSAGE_RECOMPENSES]"
        else:
            return "**Quête :** [TITRE_QUETE] + [NOM_MJ] ⁠- [LIEN_MESSAGE_RECOMPENSES]"

    def _generate_xp_section(
        self, 
        xp_actuels: Optional[int], 
        xp_obtenus: Optional[int],
        niveau_actuel: Optional[int],
        niveau_cible: Optional[int]
    ) -> str:
        """Génère la section XP avec calculs automatiques."""
        if xp_actuels is not None and xp_obtenus is not None:
            nouveau_total = xp_actuels + xp_obtenus
            section = f"**Solde XP :** {xp_actuels:,} + {xp_obtenus:,} = **{nouveau_total:,} XP**"
            
            # Vérification cohérence avec niveau cible
            if niveau_cible and niveau_cible in self.XP_TABLE:
                xp_requis = self.XP_TABLE[niveau_cible]
                if nouveau_total >= xp_requis:
                    section += f" ✅ (Suffisant pour niveau {niveau_cible})"
                else:
                    manque = xp_requis - nouveau_total
                    section += f" ⚠️ (Manque {manque:,} XP pour niveau {niveau_cible})"
            
            return section
        elif xp_actuels is not None:
            return f"**Solde XP :** {xp_actuels:,} + [XP_OBTENUS] = [NOUVEAU_TOTAL]"
        elif xp_obtenus is not None:
            return f"**Solde XP :** [XP_ACTUELS] + {xp_obtenus:,} = [NOUVEAU_TOTAL]"
        else:
            return "**Solde XP :** [XP_ACTUELS] + [XP_OBTENUS] = [NOUVEAU_TOTAL]"

    def _generate_level_section(
        self, 
        classe: str, 
        niveau_actuel: Optional[int], 
        niveau_cible: Optional[int]
    ) -> str:
        """Génère la section Gain de niveau."""
        if niveau_actuel and niveau_cible:
            if niveau_cible - niveau_actuel == 1:
                return f"**Gain de niveau :** Niveau {niveau_actuel} → **Niveau {niveau_cible}** 🎉"
            else:
                gain = niveau_cible - niveau_actuel
                return f"**Gain de niveau :** Niveau {niveau_actuel} → **Niveau {niveau_cible}** (+{gain} niveaux) 🚀"
        elif niveau_cible:
            return f"**Gain de niveau :** [NIVEAU_ACTUEL] → **Niveau {niveau_cible}**"
        else:
            return "**Gain de niveau :** [NIVEAU_ACTUEL] → [NIVEAU_CIBLE]"

    def _generate_hp_section(
        self, 
        classe: str, 
        niveau_actuel: Optional[int], 
        niveau_cible: Optional[int]
    ) -> str:
        """Génère la section PV avec calculs par classe."""
        pv_par_niveau = self.HP_PER_LEVEL.get(classe, 8)
        
        if niveau_actuel and niveau_cible:
            if niveau_cible - niveau_actuel == 1:
                return f"PV : [PV_NIVEAU_{niveau_actuel}] + {pv_par_niveau} (+ mod. CON) = [PV_NIVEAU_{niveau_cible}]"
            else:
                niveaux_gagnes = niveau_cible - niveau_actuel
                pv_totaux = pv_par_niveau * niveaux_gagnes
                return f"PV : [PV_NIVEAU_{niveau_actuel}] + {pv_totaux} (+ {niveaux_gagnes} × mod. CON) = [PV_NIVEAU_{niveau_cible}]"
        elif niveau_actuel:
            nouveau_niveau = niveau_actuel + 1
            return f"PV : [PV_NIVEAU_{niveau_actuel}] + {pv_par_niveau} (+ mod. CON) = [PV_NIVEAU_{nouveau_niveau}]"
        else:
            return "PV : [ANCIENS_PV] + [PV_OBTENUS] = [NOUVEAUX_PV]"

    def _generate_abilities_section(self, classe: str, niveau_cible: Optional[int]) -> str:
        """Génère la section Capacités et sorts avec suggestions par classe."""
        section = "**¤ Capacités et sorts supplémentaires :**\n"
        
        if niveau_cible and classe in self.CLASS_FEATURES:
            features = self.CLASS_FEATURES[classe].get(niveau_cible, [])
            spells = self.SPELL_SUGGESTIONS.get(classe, {}).get(niveau_cible, [])
            
            section += f"Nouvelle(s) capacité(s) niveau {niveau_cible} :\n"
            for feature in features[:2]:
                section += f"- {feature}\n"
            if len(features) < 2:
                for i in range(2 - len(features)):
                    section += f"- [CAPACITE_{i+1}]\n"
            
            section += f"Nouveau(x) sort(s) niveau {niveau_cible} :\n"
            for spell in spells[:2]:
                section += f"- {spell}\n"
            if len(spells) < 2:
                for i in range(2 - len(spells)):
                    section += f"- [SORT_{i+1}]\n"
        else:
            section += "Nouvelle(s) capacité(s) :\n"
            section += "- [CAPACITE_1]\n- [CAPACITE_2]\n"
            section += "Nouveau(x) sort(s) :\n"
            section += "- [SORT_1]\n- [SORT_2]\n"
        
        section += "Sort remplacé :\n- [ANCIEN_SORT] -> [NOUVEAU_SORT]"
        
        return section

    def _generate_inventory_section(self, titre_quete: Optional[str]) -> str:
        """Génère la section Inventaire."""
        section = "**¤ Inventaire**\n"
        
        if titre_quete:
            section += f"Objets lootés ({titre_quete}) :\n"
        else:
            section += "Objets lootés :\n"
        
        section += "- [OBJET_1]\n- [OBJET_2]\n- [OBJET_3]\n"
        section += "PO lootées: [MONTANT_PO]"
        
        return section

    def _generate_merchant_section(self) -> str:
        """Génère la section Marchand."""
        section = "**/ ===================== Marchand ===================== \\ **\n"
        section += "**¤ Inventaire**\n"
        section += "ACHAT : [QUANTITE] [OBJET] x [PRIX_UNITAIRE] = -[MONTANT_TOTAL] PO\n"
        section += "VENTE : [QUANTITE] [OBJET] x [PRIX_UNITAIRE] = +[MONTANT_TOTAL] PO\n"
        section += "** \\ ==================== Marchand ====================== / **"
        
        return section

    def _generate_balance_section(self) -> str:
        """Génère la section Solde final."""
        return "**¤ Solde :**\n[ANCIEN_SOLDE] +/- [PO_RECUES_DEPENSEES] = [NOUVEAU_SOLDE]"

    def get_template_stats(self, template: str) -> Dict[str, any]:
        """
        Calcule les statistiques du template généré.
        
        Returns:
            Dict avec longueur, nombre de placeholders, etc.
        """
        import re
        
        stats = {
            'length': len(template),
            'lines': len(template.split('\n')),
            'placeholders': len(re.findall(r'\[([A-Z_]+)\]', template)),
            'sections': len([line for line in template.split('\n') if line.startswith('**') and ':' in line]),
            'is_too_long': len(template) > 2000,
            'needs_splitting': len(template) > 1800
        }
        
        return stats

    def split_template_if_needed(self, template: str, max_length: int = 1800) -> List[str]:
        """
        Divise le template en plusieurs parties si nécessaire pour Discord.
        
        Args:
            template: Le template à diviser
            max_length: Longueur maximale par partie
            
        Returns:
            List[str]: Liste des parties du template
        """
        if len(template) <= max_length:
            return [template]
        
        parts = []
        lines = template.split('\n')
        current_part = []
        current_length = 0
        
        for line in lines:
            line_length = len(line) + 1  # +1 pour le '\n'
            
            if current_length + line_length > max_length and current_part:
                # Sauvegarder la partie actuelle
                parts.append('\n'.join(current_part))
                current_part = [line]
                current_length = line_length
            else:
                current_part.append(line)
                current_length += line_length
        
        # Ajouter la dernière partie
        if current_part:
            parts.append('\n'.join(current_part))
        
        return parts

    def add_class_specific_suggestions(self, classe: str, niveau: int) -> Dict[str, List[str]]:
        """
        Retourne des suggestions spécifiques à la classe pour un niveau donné.
        
        Returns:
            Dict avec 'features' et 'spells' comme clés
        """
        features = self.CLASS_FEATURES.get(classe, {}).get(niveau, [])
        spells = self.SPELL_SUGGESTIONS.get(classe, {}).get(niveau, [])
        
        return {
            'features': features,
            'spells': spells
        }