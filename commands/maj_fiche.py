# commands/maj_fiche.py
import discord
from discord import app_commands
from .base import BaseCommand


class MajFicheCommand(BaseCommand):

    @property
    def name(self) -> str:
        return "maj-fiche"

    @property
    def description(self) -> str:
        return "Génère un template de mise à jour de fiche de personnage D&D"

    def register(self, tree: app_commands.CommandTree):
        """Enregistrement avec paramètres personnalisables et listes déroulantes"""

        @tree.command(name=self.name, description=self.description)
        @app_commands.describe(
            nom_pj="Nom du personnage",
            classe="Classe du personnage", 
            niveau_actuel="Niveau actuel du personnage",
            niveau_cible="Nouveau niveau visé (optionnel)",
            titre_quete="Titre de la quête (optionnel)",
            mj="Nom du MJ (optionnel)",
            xp_actuels="XP actuels (optionnel)",
            xp_obtenus="XP obtenus cette session (optionnel)",
            include_marchand="Inclure la section Marchand",
            include_inventaire="Inclure la section Inventaire détaillée"
        )
        # NOUVEAU : Choix prédéfinis pour les classes D&D 5e
        @app_commands.choices(classe=[
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
        ])
        # NOUVEAU : Choix prédéfinis pour les niveaux actuels (1-20)
        @app_commands.choices(niveau_actuel=[
            app_commands.Choice(name="Niveau 1", value=1),
            app_commands.Choice(name="Niveau 2", value=2),
            app_commands.Choice(name="Niveau 3", value=3),
            app_commands.Choice(name="Niveau 4", value=4),
            app_commands.Choice(name="Niveau 5", value=5),
            app_commands.Choice(name="Niveau 6", value=6),
            app_commands.Choice(name="Niveau 7", value=7),
            app_commands.Choice(name="Niveau 8", value=8),
            app_commands.Choice(name="Niveau 9", value=9),
            app_commands.Choice(name="Niveau 10", value=10),
            app_commands.Choice(name="Niveau 11", value=11),
            app_commands.Choice(name="Niveau 12", value=12),
            app_commands.Choice(name="Niveau 13", value=13),
            app_commands.Choice(name="Niveau 14", value=14),
            app_commands.Choice(name="Niveau 15", value=15),
            app_commands.Choice(name="Niveau 16", value=16),
            app_commands.Choice(name="Niveau 17", value=17),
            app_commands.Choice(name="Niveau 18", value=18),
            app_commands.Choice(name="Niveau 19", value=19),
            app_commands.Choice(name="Niveau 20", value=20),
        ])
        # NOUVEAU : Choix prédéfinis pour les niveaux cibles (2-20)
        @app_commands.choices(niveau_cible=[
            app_commands.Choice(name="Niveau 2", value=2),
            app_commands.Choice(name="Niveau 3", value=3),
            app_commands.Choice(name="Niveau 4", value=4),
            app_commands.Choice(name="Niveau 5", value=5),
            app_commands.Choice(name="Niveau 6", value=6),
            app_commands.Choice(name="Niveau 7", value=7),
            app_commands.Choice(name="Niveau 8", value=8),
            app_commands.Choice(name="Niveau 9", value=9),
            app_commands.Choice(name="Niveau 10", value=10),
            app_commands.Choice(name="Niveau 11", value=11),
            app_commands.Choice(name="Niveau 12", value=12),
            app_commands.Choice(name="Niveau 13", value=13),
            app_commands.Choice(name="Niveau 14", value=14),
            app_commands.Choice(name="Niveau 15", value=15),
            app_commands.Choice(name="Niveau 16", value=16),
            app_commands.Choice(name="Niveau 17", value=17),
            app_commands.Choice(name="Niveau 18", value=18),
            app_commands.Choice(name="Niveau 19", value=19),
            app_commands.Choice(name="Niveau 20", value=20),
        ])
        @app_commands.choices(include_marchand=[
            app_commands.Choice(name="✅ Oui - Inclure section Marchand", value="oui"),
            app_commands.Choice(name="❌ Non - Pas de section Marchand", value="non")
        ])
        @app_commands.choices(include_inventaire=[
            app_commands.Choice(name="✅ Oui - Inventaire détaillé", value="oui"),
            app_commands.Choice(name="❌ Non - Inventaire minimal", value="non")
        ])
        async def maj_fiche_command(
            interaction: discord.Interaction,
            nom_pj: str,
            classe: str,
            niveau_actuel: int = None,
            niveau_cible: int = None,
            titre_quete: str = None,
            mj: str = None,
            xp_actuels: int = None,
            xp_obtenus: int = None,
            include_marchand: str = "non",
            include_inventaire: str = "oui"
        ):
            await self.callback(
                interaction, nom_pj, classe, niveau_actuel, niveau_cible,
                titre_quete, mj, xp_actuels, xp_obtenus, 
                include_marchand == "oui", include_inventaire == "oui"
            )

    async def callback(
        self, 
        interaction: discord.Interaction,
        nom_pj: str,
        classe: str,
        niveau_actuel: int = None,
        niveau_cible: int = None,
        titre_quete: str = None,
        mj: str = None,
        xp_actuels: int = None,
        xp_obtenus: int = None,
        include_marchand: bool = False,
        include_inventaire: bool = True
    ):
        # NOUVEAU : Validation intelligente des niveaux
        validation_errors = []
        
        if niveau_actuel and niveau_cible:
            if niveau_cible <= niveau_actuel:
                validation_errors.append(f"❌ Niveau cible ({niveau_cible}) doit être supérieur au niveau actuel ({niveau_actuel})")
            if niveau_cible - niveau_actuel > 1:
                validation_errors.append(f"⚠️ Attention : Passage de {niveau_actuel} à {niveau_cible} (+{niveau_cible - niveau_actuel} niveaux)")
        
        if xp_actuels is not None and xp_actuels < 0:
            validation_errors.append("❌ Les XP actuels ne peuvent pas être négatifs")
            
        if xp_obtenus is not None and xp_obtenus < 0:
            validation_errors.append("❌ Les XP obtenus ne peuvent pas être négatifs")

        # Générer le template de fiche avec toutes les améliorations
        template = self._generate_template(
            nom_pj, classe, niveau_actuel, niveau_cible,
            titre_quete, mj, xp_actuels, xp_obtenus,
            include_marchand, include_inventaire
        )

        # NOUVEAU : Créer l'embed avec informations de classe et niveaux
        embed = self._create_enhanced_embed(
            nom_pj, classe, niveau_actuel, niveau_cible,
            titre_quete, mj, xp_actuels, xp_obtenus,
            include_marchand, include_inventaire, validation_errors
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # NOUVEAU : Envoyer le template avec gestion intelligente de la longueur
        await self._send_enhanced_template(interaction, template, {
            'nom_pj': nom_pj,
            'classe': classe,
            'niveau_actuel': niveau_actuel,
            'niveau_cible': niveau_cible,
            'validation_errors': validation_errors
        })

    def _create_enhanced_embed(self, nom_pj, classe, niveau_actuel, niveau_cible, 
                              titre_quete, mj, xp_actuels, xp_obtenus,
                              include_marchand, include_inventaire, validation_errors):
        """Crée un embed amélioré avec toutes les informations"""
        
        # Déterminer la couleur selon la classe (thématique D&D)
        class_colors = {
            "Guerrier": 0x8B4513,      # Marron
            "Rôdeur": 0x228B22,        # Vert forêt
            "Paladin": 0xFFD700,       # Or
            "Barbare": 0xDC143C,       # Rouge crimson
            "Barde": 0xFF69B4,         # Rose
            "Ensorceleur": 0x9400D3,   # Violet
            "Magicien": 0x4169E1,      # Bleu royal
            "Druide": 0x32CD32,        # Vert lime
            "Clerc": 0xFFFFE0,         # Blanc cassé
            "Moine": 0xF4A460,         # Brun sable
            "Roublard": 0x2F4F4F,      # Gris ardoise
            "Occultiste": 0x800080,    # Pourpre
        }
        
        color = class_colors.get(classe, 0x8B4513)
        
        embed = discord.Embed(
            title="📋 Template de Mise à jour de Fiche D&D",
            description=f"Template personnalisé généré pour **{nom_pj}** ({classe})",
            color=color
        )

        # NOUVEAU : Section personnage avec émojis de classe
        class_emojis = {
            "Guerrier": "⚔️", "Rôdeur": "🏹", "Paladin": "🛡️", "Barbare": "🪓",
            "Barde": "🎵", "Ensorceleur": "✨", "Magicien": "📜", "Druide": "🌿",
            "Clerc": "⛪", "Moine": "👊", "Roublard": "🗡️", "Occultiste": "👹"
        }
        
        character_info = f"{class_emojis.get(classe, '⚔️')} **{classe}**"
        if niveau_actuel:
            character_info += f" - Niveau {niveau_actuel}"
        if niveau_cible:
            character_info += f" → {niveau_cible}"
            
        embed.add_field(
            name="🎭 Personnage",
            value=character_info,
            inline=True
        )

        # NOUVEAU : Informations de session avec calculs automatiques
        session_info = []
        if titre_quete:
            session_info.append(f"🎯 **Quête :** {titre_quete}")
        if mj:
            session_info.append(f"🎲 **MJ :** {mj}")
        
        # NOUVEAU : Calculs XP automatiques avec validation
        if xp_actuels is not None and xp_obtenus is not None:
            nouveaux_xp = xp_actuels + xp_obtenus
            session_info.append(f"⭐ **XP :** {xp_actuels} + {xp_obtenus} = **{nouveaux_xp}**")
            
            # NOUVEAU : Estimation du niveau selon les XP (table D&D 5e)
            niveau_estime = self._estimate_level_from_xp(nouveaux_xp)
            if niveau_estime > (niveau_actuel or 1):
                session_info.append(f"🆙 **Niveau estimé :** {niveau_estime}")
        elif xp_actuels is not None:
            session_info.append(f"⭐ **XP actuels :** {xp_actuels}")
        elif xp_obtenus is not None:
            session_info.append(f"✨ **XP obtenus :** {xp_obtenus}")
        
        if session_info:
            embed.add_field(
                name="📝 Session",
                value="\n".join(session_info),
                inline=True
            )

        # NOUVEAU : Sections incluses avec comptage
        sections_incluses = ["📊 Quête et XP", "📈 Gain de niveau", "🎯 Capacités"]
        if include_inventaire:
            sections_incluses.append("📦 Inventaire")
        if include_marchand:
            sections_incluses.append("🛒 Marchand")
        sections_incluses.append("💰 Solde final")
        
        embed.add_field(
            name=f"📋 Sections ({len(sections_incluses)})",
            value="\n".join([f"• {section}" for section in sections_incluses]),
            inline=False
        )

        # NOUVEAU : Alertes et validations
        if validation_errors:
            embed.add_field(
                name="⚠️ Alertes",
                value="\n".join(validation_errors),
                inline=False
            )

        # NOUVEAU : Statistiques du template
        template_length = len(self._generate_template(
            nom_pj, classe, niveau_actuel, niveau_cible,
            titre_quete, mj, xp_actuels, xp_obtenus,
            include_marchand, include_inventaire
        ))
        
        stats_text = f"**Longueur :** {template_length} caractères"
        if template_length > 2000:
            stats_text += " ⚠️ (sera divisé)"
        elif template_length > 1800:
            stats_text += " 🟡 (proche limite)"
        else:
            stats_text += " ✅ (taille OK)"
            
        embed.add_field(
            name="📊 Statistiques",
            value=stats_text,
            inline=True
        )
        
        embed.add_field(
            name="💡 Utilisation",
            value="Template personnalisé envoyé ci-dessous !\nComplétez les placeholders `[EN_MAJUSCULES]`",
            inline=True
        )
        
        embed.set_footer(
            text=f"Généré par {interaction.user.display_name} • Template D&D 5e"
        )
        embed.timestamp = discord.utils.utcnow()
        
        return embed

    def _estimate_level_from_xp(self, xp: int) -> int:
        """Estime le niveau basé sur les XP selon la table D&D 5e"""
        xp_thresholds = [
            0, 300, 900, 2700, 6500, 14000, 23000, 34000, 48000, 64000,
            85000, 100000, 120000, 140000, 165000, 195000, 225000, 265000, 305000, 355000
        ]
        
        for level, threshold in enumerate(xp_thresholds[1:], 2):
            if xp < threshold:
                return level - 1
        return 20

    def _generate_template(
        self, nom_pj, classe, niveau_actuel, niveau_cible,
        titre_quete, mj, xp_actuels, xp_obtenus,
        include_marchand, include_inventaire
    ) -> str:
        """Génère le template de mise à jour avec les informations pré-remplies"""
        
        template = f"Nom du PJ : {nom_pj}\n"
        template += f"Classe : {classe}\n\n"
        
        template += "** / =======================  PJ  ========================= \\ **\n"
        
        # Section Quête - PRÉ-REMPLIE avec logique intelligente
        if titre_quete and mj:
            template += f"**Quête :** {titre_quete} + {mj} ⁠- [LIEN_MESSAGE_RECOMPENSES]\n"
        elif titre_quete:
            template += f"**Quête :** {titre_quete} + [NOM_MJ] ⁠- [LIEN_MESSAGE_RECOMPENSES]\n"
        elif mj:
            template += f"**Quête :** [TITRE_QUETE] + {mj} ⁠- [LIEN_MESSAGE_RECOMPENSES]\n"
        else:
            template += "**Quête :** [TITRE_QUETE] + [NOM_MJ] ⁠- [LIEN_MESSAGE_RECOMPENSES]\n"
        
        # Section XP - CALCULS AUTOMATIQUES INTELLIGENTS
        if xp_actuels is not None and xp_obtenus is not None:
            nouveaux_xp = xp_actuels + xp_obtenus
            
            # NOUVEAU : Calcul intelligent du niveau et XP requis
            if niveau_cible:
                xp_requis = self._get_xp_for_level(niveau_cible)
                template += f"**Solde XP :** {xp_actuels}/{xp_requis} + {xp_obtenus} = {nouveaux_xp}/{xp_requis} -> 🆙 passage au niveau {niveau_cible}\n\n"
            elif niveau_actuel:
                nouveau_niveau = niveau_actuel + 1
                xp_requis = self._get_xp_for_level(nouveau_niveau)
                template += f"**Solde XP :** {xp_actuels}/{xp_requis} + {xp_obtenus} = {nouveaux_xp}/{xp_requis} -> 🆙 passage au niveau {nouveau_niveau}\n\n"
            else:
                # Estimation automatique du niveau
                niveau_estime = self._estimate_level_from_xp(nouveaux_xp)
                xp_requis = self._get_xp_for_level(niveau_estime + 1)
                template += f"**Solde XP :** {xp_actuels}/[XP_REQUIS] + {xp_obtenus} = {nouveaux_xp}/{xp_requis} -> 🆙 passage au niveau {niveau_estime}\n\n"
        elif niveau_actuel and niveau_cible:
            xp_requis = self._get_xp_for_level(niveau_cible)
            template += f"**Solde XP :** [XP_ACTUELS]/{xp_requis} + [XP_OBTENUS] = [NOUVEAUX_XP]/{xp_requis} -> 🆙 passage au niveau {niveau_cible}\n\n"
        elif niveau_actuel:
            nouveau_niveau = niveau_actuel + 1
            xp_requis = self._get_xp_for_level(nouveau_niveau)
            template += f"**Solde XP :** [XP_ACTUELS]/{xp_requis} + [XP_OBTENUS] = [NOUVEAUX_XP]/{xp_requis} -> 🆙 passage au niveau {nouveau_niveau}\n\n"
        else:
            template += "**Solde XP :** [XP_ACTUELS]/[XP_REQUIS] + [XP_OBTENUS] = [NOUVEAUX_XP]/[XP_REQUIS] -> 🆙 passage au niveau [NOUVEAU_NIVEAU]\n\n"
        
        # Section Gain de niveau - AVEC CALCULS DE PV SELON LA CLASSE
        template += "**Gain de niveau :**\n"
        if niveau_actuel and niveau_cible:
            pv_par_niveau = self._get_hp_per_level(classe)
            template += f"PV : [PV_NIVEAU_{niveau_actuel}] + {pv_par_niveau} (+ mod. CON) = [PV_NIVEAU_{niveau_cible}]\n\n"
        elif niveau_actuel:
            nouveau_niveau = niveau_actuel + 1
            pv_par_niveau = self._get_hp_per_level(classe)
            template += f"PV : [PV_NIVEAU_{niveau_actuel}] + {pv_par_niveau} (+ mod. CON) = [PV_NIVEAU_{nouveau_niveau}]\n\n"
        else:
            template += "PV : [ANCIENS_PV] + [PV_OBTENUS] = [NOUVEAUX_PV]\n\n"
        
        # Section Capacités et sorts - AVEC SUGGESTIONS SPÉCIFIQUES À LA CLASSE
        template += "**¤ Capacités et sorts supplémentaires :**\n"
        if niveau_cible:
            suggestions = self._get_class_features_suggestions(classe, niveau_cible)
            template += f"Nouvelle(s) capacité(s) niveau {niveau_cible} :\n"
            if suggestions['features']:
                for feature in suggestions['features'][:2]:
                    template += f"- {feature}\n"
            else:
                template += "- [CAPACITE_1]\n- [CAPACITE_2]\n"
                
            template += f"Nouveau(x) sort(s) niveau {niveau_cible} :\n"
            if suggestions['spells']:
                for spell in suggestions['spells'][:2]:
                    template += f"- {spell}\n"
            else:
                template += "- [SORT_1]\n- [SORT_2]\n"
        else:
            template += "Nouvelle(s) capacité(s) :\n"
            template += "- [CAPACITE_1]\n"
            template += "- [CAPACITE_2]\n"
            template += "Nouveau(x) sort(s) :\n"
            template += "- [SORT_1]\n"
            template += "- [SORT_2]\n"
            
        template += "Sort remplacé :\n"
        template += "- [ANCIEN_SORT] -> [NOUVEAU_SORT]\n\n"
        
        # Section Inventaire (si demandée)
        if include_inventaire:
            template += "**¤ Inventaire**\n"
            if titre_quete:
                template += f"Objets lootés ({titre_quete}) :\n"
            else:
                template += "Objets lootés :\n"
            template += "- [OBJET_1]\n"
            template += "- [OBJET_2]\n"
            template += "- [OBJET_3]\n"
            template += "PO lootées: [MONTANT_PO]\n"
        
        template += "** \\ =======================  PJ  ========================= / **\n\n"
        
        # Section Marchand (si demandée)
        if include_marchand:
            template += "**/ ===================== Marchand ===================== \\ **\n"
            template += "**¤ Inventaire**\n"
            template += "ACHAT : [QUANTITE] [OBJET] x [PRIX_UNITAIRE] = -[MONTANT_TOTAL] PO\n"
            template += "VENTE : [QUANTITE] [OBJET] x [PRIX_UNITAIRE] = +[MONTANT_TOTAL] PO\n"
            template += "** \\ ==================== Marchand ====================== / **\n\n"
        
        # Section Solde final - AVEC CALCULS SI DONNÉES FOURNIES
        template += "**¤ Solde :**\n"
        template += "[ANCIEN_SOLDE] +/- [PO_RECUES_DEPENSEES] = [NOUVEAU_SOLDE]\n\n"
        template += "*Fiche R20 à jour.*"
        
        return template

    def _get_xp_for_level(self, level: int) -> int:
        """Retourne les XP requis pour atteindre un niveau donné (D&D 5e)"""
        xp_table = [
            0, 300, 900, 2700, 6500, 14000, 23000, 34000, 48000, 64000,
            85000, 100000, 120000, 140000, 165000, 195000, 225000, 265000, 305000, 355000
        ]
        return xp_table[min(level - 1, 19)] if level > 0 else 0

    def _get_hp_per_level(self, classe: str) -> str:
        """Retourne les PV moyens par niveau selon la classe"""
        hp_per_class = {
            "Guerrier": "6",
            "Paladin": "6", 
            "Barbare": "7",
            "Rôdeur": "6",
            "Barde": "5",
            "Clerc": "5",
            "Druide": "5",
            "Moine": "5",
            "Roublard": "5",
            "Occultiste": "5",
            "Ensorceleur": "4",
            "Magicien": "4"
        }
        return hp_per_class.get(classe, "5")

    def _get_class_features_suggestions(self, classe: str, niveau: int) -> dict:
        """Suggère des capacités et sorts selon la classe et le niveau"""
        
        # Base de données simplifiée des capacités par classe
        class_features = {
            "Guerrier": {
                2: ["Action Surge", "Second souffle"],
                3: ["Archétype martial", "Style de combat"],
                4: ["Amélioration de caractéristique", "Exploit"],
                5: ["Attaque supplémentaire", "Second Wind amélioré"],
            },
            "Magicien": {
                2: ["Tradition arcanique", "Récupération arcanique"],
                3: ["Sorts de 2e niveau", "Tradition arcanique (capacité)"],
                4: ["Amélioration de caractéristique", "Tours de magie"],
                5: ["Sorts de 3e niveau", "Tradition arcanique améliorée"],
            },
            "Roublard": {
                2: ["Action sournoise", "Ruse"],
                3: ["Archétype de roublard", "Expertise"],
                4: ["Amélioration de caractéristique", "Action sournoise +1d6"],
                5: ["Attaque sournoise améliorée", "Esquive instinctive"],
            }
        }
        
        # Sorts suggérés par classe (exemples)
        class_spells = {
            "Magicien": ["Bouclier", "Projectile magique", "Toile d'araignée", "Boule de feu"],
            "Clerc": ["Soins", "Bénédiction", "Aide", "Restauration"],
            "Barde": ["Charme-personne", "Inspiration", "Suggestion", "Hypnose"],
            "Ensorceleur": ["Mains brûlantes", "Projectile magique", "Image miroir", "Flou"],
        }
        
        features = class_features.get(classe, {}).get(niveau, ["[CAPACITE_CLASSE]", "[CAPACITE_NIVEAU]"])
        spells = class_spells.get(classe, ["[SORT_CLASSE]", "[SORT_NIVEAU]"])
        
        return {
            'features': features,
            'spells': spells[:3]  # Max 3 suggestions
        }

    async def _send_enhanced_template(self, interaction: discord.Interaction, template: str, info: dict):
        """Envoie le template avec gestion améliorée"""
        
        # Calculer la longueur totale
        total_length = len(template)
        discord_limit = 1900  # Limite sécurisée
        
        if total_length <= discord_limit:
            # Template complet dans un seul message
            embed = discord.Embed(
                title="📋 Votre Template de MAJ",
                description=f"Template personnalisé pour **{info['nom_pj']}** ({info['classe']})",
                color=0x2ecc71
            )
            
            # Statistiques détaillées
            placeholder_count = len(re.findall(r'\[([A-Z_]+)\]', template))
            embed.add_field(
                name="📊 Statistiques",
                value=f"**Caractères :** {total_length}/2000\n**Placeholders :** {placeholder_count}",
                inline=True
            )
            
            # Informations de niveau si disponibles
            if info['niveau_actuel'] and info['niveau_cible']:
                embed.add_field(
                    name="📈 Progression",
                    value=f"Niveau {info['niveau_actuel']} → {info['niveau_cible']}",
                    inline=True
                )
            
            # Alertes si présentes
            if info['validation_errors']:
                embed.add_field(
                    name="⚠️ Attention",
                    value="\n".join(info['validation_errors'][:2]),
                    inline=False
                )
            
            # Instructions d'utilisation
            if placeholder_count > 0:
                embed.add_field(
                    name="📝 Prochaines étapes",
                    value=f"1. **Copiez** le template ci-dessous\n2. **Remplacez** les {placeholder_count} placeholders [EN_MAJUSCULES]\n3. **Vérifiez** les calculs automatiques\n4. **Postez** votre MAJ !",
                    inline=False
                )
            else:
                embed.add_field(
                    name="🎯 Template prêt !",
                    value="✅ Template pré-rempli avec vos informations\n✅ Vérifiez les calculs XP/PV\n✅ Prêt à poster !",
                    inline=False
                )
            
            # Template dans un bloc de code formaté
            embed.add_field(
                name="📋 Votre Template Final",
                value=f"```\n{template}\n```",
                inline=False
            )
            
            # Conseil selon la longueur
            if total_length > 1800:
                embed.add_field(
                    name="💡 Conseil",
                    value="Template proche de la limite Discord. Tout devrait bien passer, mais vous pouvez raccourcir si nécessaire.",
                    inline=False
                )
            
            await interaction.followup.send(embed=embed, ephemeral=True)
        
        else:
            # Template trop long - diviser en parties
            embed_intro = discord.Embed(
                title="📋 Template de MAJ - Multi-parties",
                description=f"Template pour **{info['nom_pj']}** ({info['classe']}) - Divisé car trop long pour Discord",
                color=0xf39c12
            )
            
            # Stats dans l'intro
            placeholder_count = len(re.findall(r'\[([A-Z_]+)\]', template))
            
            embed_intro.add_field(
                name="📊 Informations",
                value=f"**Total :** {total_length} caractères\n**Placeholders :** {placeholder_count}\n**Parties :** {self._calculate_parts_needed(template)}",
                inline=True
            )
            
            if info['niveau_actuel'] and info['niveau_cible']:
                embed_intro.add_field(
                    name="📈 Niveau",
                    value=f"{info['niveau_actuel']} → {info['niveau_cible']}",
                    inline=True
                )
            
            if info['validation_errors']:
                embed_intro.add_field(
                    name="⚠️ Alertes",
                    value="\n".join(info['validation_errors'][:2]),
                    inline=False
                )
            
            embed_intro.add_field(
                name="📝 Instructions",
                value="1. **Copiez** chaque partie dans l'ordre\n2. **Assemblez** en un seul message\n3. **Complétez** les placeholders restants\n4. **Vérifiez** et postez !",
                inline=False
            )
            
            await interaction.followup.send(embed=embed_intro, ephemeral=True)
            
            # Diviser et envoyer les parties
            parts = self._split_template_for_discord(template)
            
            for i, part in enumerate(parts, 1):
                part_embed = discord.Embed(
                    title=f"📋 Template - Partie {i}/{len(parts)}",
                    description=f"```\n{part}\n```",
                    color=0x2ecc71
                )
                
                part_embed.add_field(
                    name="📏 Cette partie",
                    value=f"**Longueur :** {len(part)} caractères\n**Partie :** {i} sur {len(parts)}",
                    inline=True
                )
                
                if i == 1:
                    part_embed.add_field(
                        name="💡 Astuce",
                        value="Copiez chaque partie et collez-les bout à bout",
                        inline=True
                    )
                elif i == len(parts):
                    part_embed.add_field(
                        name="✅ Fini !",
                        value=f"Template complet reconstitué !\n**{total_length}** caractères au total",
                        inline=True
                    )
                
                await interaction.followup.send(embed=part_embed, ephemeral=True)

    def _calculate_parts_needed(self, template: str) -> int:
        """Calcule le nombre de parties nécessaires"""
        return len(self._split_template_for_discord(template))

    def _split_template_for_discord(self, template: str) -> list:
        """Divise le template pour respecter les limites Discord"""
        max_length = 1900  # Limite sécurisée
        parts = []
        
        if len(template) <= max_length:
            return [template]
        
        lines = template.split('\n')
        current_part = ""
        
        for line in lines:
            # Si ajouter cette ligne dépasse la limite
            if len(current_part + line + '\n') > max_length:
                if current_part:
                    parts.append(current_part.rstrip())
                current_part = line + '\n'
            else:
                current_part += line + '\n'
        
        # Ajouter la dernière partie
        if current_part:
            parts.append(current_part.rstrip())
        
        return parts