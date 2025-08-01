# commands/pnj_generator_formatters.py - Formatage des Sorties PNJ

class PNJFormatters:
    """Classe gérant le formatage des PNJ pour différentes sorties"""
    
    def format_pnj_for_roll20(self, pnj: dict, type_pnj: str) -> str:
        """Formate le PNJ pour Roll20 (texte brut)"""
        
        template = f"""=== PNJ GENEREE ===

NOM: {pnj['nom']}
RACE: {pnj['race']}
CLASSE/TYPE: {type_pnj.title()}
GENRE: {pnj['genre'].title()}
AGE: {pnj['age']} ans

--- APPARENCE ---
{pnj['apparence']}

--- PERSONNALITE ---
Trait Positif: {pnj['personnalite']['trait_positif'].title()}
Trait Negatif: {pnj['personnalite']['trait_negatif'].title()}
Manie: {pnj['personnalite']['maniere']}
Motivation: {pnj['personnalite']['motivation'].title()}

--- BACKGROUND ---
{self._format_professional_details_roll20(pnj['details'], type_pnj)}

--- ACCROCHE RP ---
{pnj['secret']}

--- NOTES MJ ---
[Espace libre pour notes personnalisees]

=== FIN PNJ ==="""
        
        return template.strip()

    def format_pnj_for_discord(self, pnj: dict, type_pnj: str) -> str:
        """Formate le PNJ pour Discord (avec formatage)"""
        
        template = f"""** / ======================= PNJ ========================= \\ **

**📛 Nom :** {pnj['nom']}
**🎭 Type :** {type_pnj.title()}
**⚧️ Genre :** {pnj['genre'].title()}
**🧝 Race :** {pnj['race']}
**🎂 Âge :** {pnj['age']} ans

**👤 APPARENCE**
{pnj['apparence']}

**🧠 PERSONNALITÉ**
• **Trait positif :** {pnj['personnalite']['trait_positif'].title()}
• **Trait négatif :** {pnj['personnalite']['trait_negatif'].title()}
• **Manie :** {pnj['personnalite']['maniere']}
• **Motivation :** {pnj['personnalite']['motivation'].title()}

**💼 BACKGROUND**
{self._format_professional_details_discord(pnj['details'], type_pnj)}

**🎲 ACCROCHE RP**
{pnj['secret']}

** \\ ======================= PNJ ========================= / **

*PNJ généré automatiquement - Prêt à utiliser*"""
        
        return template.strip()

    def _format_professional_details_roll20(self, details: dict, type_pnj: str) -> str:
        """Formate les détails professionnels pour Roll20"""
        
        if type_pnj == "marchand":
            return f"""Specialite: {details.get('specialite', 'Marchandises générales')}
Richesse: {details.get('richesse', 'Modeste')}
Reputation: {details.get('reputation', 'Honnête')}
Experience: {details.get('info_extra', 'Établi depuis quelques années')}"""
        
        elif type_pnj == "noble":
            return f"""Titre: {details.get('titre', 'Lord/Lady')}
Domaine: {details.get('domaine', 'Terres agricoles')}
Influence: {details.get('influence', 'Locale')}
Lignee: {details.get('info_extra', 'Famille ancienne')}"""
        
        elif type_pnj == "garde":
            return f"""Rang: {details.get('rang', 'Simple garde')}
Experience: {details.get('experience', '5 ans de service')}
Specialite: {details.get('specialite', 'Patrouilles')}
Background: {details.get('info_extra', 'Natif de la région')}"""
        
        elif type_pnj == "aubergiste":
            return f"""Etablissement: {details.get('etablissement', 'Auberge modeste')}
Reputation: {details.get('reputation', 'Accueillant')}
Specialite: {details.get('specialite_culinaire', 'Cuisine locale')}
Experience: {details.get('info_extra', 'Gérant depuis des années')}"""
        
        elif type_pnj == "pretre":
            return f"""Divinite: {details.get('divinite', 'Divinité majeure')}
Rang: {details.get('rang_clerical', 'Prêtre')}
Temple: {details.get('temple', 'Temple local')}
Devotion: {details.get('info_extra', 'Serviteur fidèle')}"""
        
        elif type_pnj == "aventurier":
            return f"""Classe: {details.get('classe', 'Guerrier')}
Niveau: {details.get('niveau_estime', 'Expérimenté')}
Specialite: {details.get('specialite', 'Exploration')}
Experience: {details.get('info_extra', 'Quelques années d\'aventure')}"""
        
        elif type_pnj == "artisan":
            return f"""Metier: {details.get('metier', 'Artisan')}
Reputation: {details.get('reputation', 'Respecté')}
Specialite: {details.get('specialite', 'Travail de qualité')}
Experience: {details.get('info_extra', 'Maîtrise son art')}"""
        
        elif type_pnj == "paysan":
            return f"""Activite: {details.get('activite', 'Agriculture')}
Statut: {details.get('statut', 'Propriétaire')}
Specialite: {details.get('specialite', 'Cultures variées')}
Experience: {details.get('info_extra', 'Travaille la terre')}"""
        
        elif type_pnj == "voleur":
            return f"""Specialite: {details.get('specialite', 'Vol à la tire')}
Reputation: {details.get('reputation', 'Discret')}
Territoire: {details.get('territoire', 'Quartiers populaires')}
Experience: {details.get('info_extra', 'Actif depuis peu')}"""
        
        elif type_pnj == "mage":
            return f"""Ecole: {details.get('ecole_magie', 'Évocation')}
Niveau: {details.get('niveau_estime', 'Apprenti')}
Specialite: {details.get('specialite', 'Sorts utilitaires')}
Experience: {details.get('info_extra', 'Étudie la magie')}"""
        
        else:
            return "Details a developper selon les besoins de la campagne"

    def _format_professional_details_discord(self, details: dict, type_pnj: str) -> str:
        """Formate les détails professionnels pour Discord"""
        
        if type_pnj == "marchand":
            return f"""• **Spécialité :** {details.get('specialite', 'Marchandises générales')}
• **Richesse :** {details.get('richesse', 'Modeste')}
• **Réputation :** {details.get('reputation', 'Honnête')}
• **Expérience :** {details.get('info_extra', 'Établi depuis quelques années')}"""
        
        elif type_pnj == "noble":
            return f"""• **Titre :** {details.get('titre', 'Lord/Lady')}
• **Domaine :** {details.get('domaine', 'Terres agricoles')}
• **Influence :** {details.get('influence', 'Locale')}
• **Lignée :** {details.get('info_extra', 'Famille ancienne')}"""
        
        elif type_pnj == "garde":
            return f"""• **Rang :** {details.get('rang', 'Simple garde')}
• **Expérience :** {details.get('experience', '5 ans de service')}
• **Spécialité :** {details.get('specialite', 'Patrouilles')}
• **Background :** {details.get('info_extra', 'Natif de la région')}"""
        
        elif type_pnj == "aubergiste":
            return f"""• **Établissement :** {details.get('etablissement', 'Auberge modeste')}
• **Réputation :** {details.get('reputation', 'Accueillant')}
• **Spécialité :** {details.get('specialite_culinaire', 'Cuisine locale')}
• **Expérience :** {details.get('info_extra', 'Gérant depuis des années')}"""
        
        elif type_pnj == "pretre":
            return f"""• **Divinité :** {details.get('divinite', 'Divinité majeure')}
• **Rang :** {details.get('rang_clerical', 'Prêtre')}
• **Temple :** {details.get('temple', 'Temple local')}
• **Dévotion :** {details.get('info_extra', 'Serviteur fidèle')}"""
        
        elif type_pnj == "aventurier":
            return f"""• **Classe :** {details.get('classe', 'Guerrier')}
• **Niveau :** {details.get('niveau_estime', 'Expérimenté')}
• **Spécialité :** {details.get('specialite', 'Exploration')}
• **Expérience :** {details.get('info_extra', 'Quelques années d\'aventure')}"""
        
        elif type_pnj == "artisan":
            return f"""• **Métier :** {details.get('metier', 'Artisan')}
• **Réputation :** {details.get('reputation', 'Respecté')}
• **Spécialité :** {details.get('specialite', 'Travail de qualité')}
• **Expérience :** {details.get('info_extra', 'Maîtrise son art')}"""
        
        elif type_pnj == "paysan":
            return f"""• **Activité :** {details.get('activite', 'Agriculture')}
• **Statut :** {details.get('statut', 'Propriétaire')}
• **Spécialité :** {details.get('specialite', 'Cultures variées')}
• **Expérience :** {details.get('info_extra', 'Travaille la terre')}"""
        
        elif type_pnj == "voleur":
            return f"""• **Spécialité :** {details.get('specialite', 'Vol à la tire')}
• **Réputation :** {details.get('reputation', 'Discret')}
• **Territoire :** {details.get('territoire', 'Quartiers populaires')}
• **Expérience :** {details.get('info_extra', 'Actif depuis peu')}"""
        
        elif type_pnj == "mage":
            return f"""• **École :** {details.get('ecole_magie', 'Évocation')}
• **Niveau :** {details.get('niveau_estime', 'Apprenti')}
• **Spécialité :** {details.get('specialite', 'Sorts utilitaires')}
• **Expérience :** {details.get('info_extra', 'Étudie la magie')}"""
        
        else:
            return "• **Détails :** À développer selon les besoins de la campagne"