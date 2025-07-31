# commands/maj_fiche/main_command.py
import discord
from discord import app_commands
from ..base import BaseCommand
from typing import Optional, List, Dict, Any


class MajFicheBaseCommand(BaseCommand):
    """
    Classe de base commune pour les commandes de mise à jour de fiche.
    Contient les méthodes utilitaires et la logique de validation partagée.
    """

    def __init__(self, bot):  # ✅ CORRECTION: Ajout du paramètre bot
        super().__init__(bot)   # ✅ CORRECTION: Passage de bot au parent
        
        # Dictionnaire des classes D&D avec émojis pour réutilisation
        self.CLASSES_CHOICES = [
            app_commands.Choice(name="🗡️ Guerrier", value="Guerrier"),
            app_commands.Choice(name="🏹 Rôdeur", value="Rôdeur"),
            app_commands.Choice(name="🛡️ Paladin", value="Paladin"),
            app_commands.Choice(name="🗡️ Barbare", value="Barbare"),
            app_commands.Choice(name="🎭 Barde", value="Barde"),
            app_commands.Choice(name="🔮 Ensorceleur", value="Ensorceleur"),
            app_commands.Choice(name="📚 Magicien", value="Magicien"),
            app_commands.Choice(name="🌿 Druide", value="Druide"),
            app_commands.Choice(name="⛪ Clerc", value="Clerc"),
            app_commands.Choice(name="🗡️ Moine", value="Moine"),
            app_commands.Choice(name="🎯 Roublard", value="Roublard"),
            app_commands.Choice(name="👹 Occultiste", value="Occultiste"),
        ]

        # Choix pour les niveaux (1-20)
        self.NIVEAUX_ACTUELS = [
            app_commands.Choice(name=f"Niveau {i}", value=i) for i in range(1, 21)
        ]
        
        # Choix pour les niveaux cibles (2-20)
        self.NIVEAUX_CIBLES = [
            app_commands.Choice(name=f"Niveau {i}", value=i) for i in range(2, 21)
        ]

        # Choix oui/non pour les options
        self.OUI_NON_CHOICES = [
            app_commands.Choice(name="✅ Oui", value="oui"),
            app_commands.Choice(name="❌ Non", value="non")
        ]

    def validate_parameters(
        self, 
        nom_pj: str,
        classe: str,
        niveau_actuel: Optional[int] = None,
        niveau_cible: Optional[int] = None,
        xp_actuels: Optional[int] = None,
        xp_obtenus: Optional[int] = None
    ) -> List[str]:
        """
        Valide les paramètres d'entrée et retourne la liste des erreurs.
        
        Returns:
            List[str]: Liste des erreurs de validation (vide si tout est OK)
        """
        errors = []
        
        # Validation du nom
        if not nom_pj or len(nom_pj.strip()) < 2:
            errors.append("❌ Le nom du PJ doit contenir au moins 2 caractères")
        
        # Validation des niveaux
        if niveau_actuel and niveau_cible:
            if niveau_actuel >= niveau_cible:
                errors.append(f"⚠️ Le niveau cible ({niveau_cible}) doit être supérieur au niveau actuel ({niveau_actuel})")
            if niveau_cible - niveau_actuel > 5:
                errors.append(f"⚠️ Progression de {niveau_cible - niveau_actuel} niveaux - vérifiez si c'est correct")
        
        # Validation des XP
        if xp_actuels is not None and xp_actuels < 0:
            errors.append("❌ Les XP actuels ne peuvent pas être négatifs")
        if xp_obtenus is not None and xp_obtenus < 0:
            errors.append("❌ Les XP obtenus ne peuvent pas être négatifs")
        
        return errors

    def format_progression_info(
        self, 
        niveau_actuel: Optional[int],
        niveau_cible: Optional[int],
        xp_actuels: Optional[int],
        xp_obtenus: Optional[int]
    ) -> Dict[str, any]:
        """
        Formate les informations de progression pour l'affichage.
        
        Returns:
            Dict contenant les infos formatées et calculs
        """
        xp_table = {
            1: 0, 2: 300, 3: 900, 4: 2700, 5: 6500,
            6: 14000, 7: 23000, 8: 34000, 9: 48000, 10: 64000,
            11: 85000, 12: 100000, 13: 120000, 14: 140000, 15: 165000,
            16: 195000, 17: 225000, 18: 265000, 19: 305000, 20: 355000
        }
        
        result = {
            'text_niveau': 'Non spécifié',
            'text_xp': 'Non spécifié',
            'progression_info': '',
            'nouveau_total_xp': None
        }
        
        # Formatage des niveaux
        if niveau_actuel and niveau_cible:
            result['text_niveau'] = f"Niveau {niveau_actuel} → **Niveau {niveau_cible}**"
            if niveau_cible - niveau_actuel == 1:
                result['progression_info'] = f"🎉 Passage au niveau {niveau_cible} !"
            else:
                result['progression_info'] = f"🚀 Progression de {niveau_cible - niveau_actuel} niveaux !"
                
        elif niveau_actuel:
            result['text_niveau'] = f"Niveau {niveau_actuel}"
        elif niveau_cible:
            result['text_niveau'] = f"**Niveau {niveau_cible}**"

        # Gestion des XP
        if xp_actuels is not None and xp_obtenus is not None:
            result['nouveau_total_xp'] = xp_actuels + xp_obtenus  
            result['text_xp'] = f"{xp_actuels:,} + {xp_obtenus:,} = **{result['nouveau_total_xp']:,} XP**"
            
            # Vérification de cohérence avec les niveaux
            if niveau_cible and niveau_cible in xp_table:
                xp_requis = xp_table[niveau_cible]
                if result['nouveau_total_xp'] >= xp_requis:
                    result['progression_info'] += f" ✅ XP suffisants pour le niveau {niveau_cible}"
                else:
                    manque = xp_requis - result['nouveau_total_xp']
                    result['progression_info'] += f" ⚠️ Il manque {manque:,} XP pour le niveau {niveau_cible}"
                    
        elif xp_actuels is not None:
            result['text_xp'] = f"{xp_actuels:,} XP"
        elif xp_obtenus is not None:
            result['text_xp'] = f"+{xp_obtenus:,} XP cette session"

        return result

    def format_template_header(
        self,
        nom_pj: str,
        classe: str,
        titre_quete: Optional[str] = None,
        mj: Optional[str] = None
    ) -> str:
        """
        Génère l'en-tête du template avec les informations de base.
        """
        header_parts = []
        
        # Titre principal
        header_parts.append("# 📝 Mise à jour de fiche de personnage")
        header_parts.append("")
        
        # Informations de base
        header_parts.append("## 👤 Informations du personnage")
        header_parts.append(f"**Nom du PJ :** {nom_pj}")
        header_parts.append(f"**Classe :** {classe}")
        
        if titre_quete:
            header_parts.append(f"**Quête :** {titre_quete}")
        
        if mj:
            header_parts.append(f"**MJ :** {mj}")
            
        header_parts.append("")
        
        return "\n".join(header_parts)

    def get_embed_validation_color(self, validation_errors: List[str]) -> int:
        """
        Retourne la couleur d'embed selon le nombre d'erreurs de validation.
        """
        if not validation_errors:
            return 0x2ecc71  # Vert - Tout va bien
        elif any("❌" in error for error in validation_errors):
            return 0xe74c3c  # Rouge - Erreurs critiques
        else:
            return 0xf39c12  # Orange - Avertissements seulement

    def create_validation_embed(
        self, 
        validation_errors: List[str],
        nom_pj: str,
        classe: str
    ) -> discord.Embed:
        """
        Crée un embed Discord pour afficher les erreurs de validation.
        """
        color = self.get_embed_validation_color(validation_errors)
        
        embed = discord.Embed(
            title="⚠️ Validation du template",
            description=f"Template pour **{nom_pj}** ({classe})",
            color=color
        )
        
        if validation_errors:
            embed.add_field(
                name="Problèmes détectés",
                value="\n".join(validation_errors),
                inline=False
            )
        else:
            embed.add_field(
                name="✅ Validation réussie",
                value="Tous les paramètres sont corrects !",
                inline=False
            )
            
        return embed