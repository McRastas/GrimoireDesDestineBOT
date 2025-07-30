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
        """Enregistrement avec paramètres personnalisables"""

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
        @app_commands.choices(include_marchand=[
            app_commands.Choice(name="Oui", value="oui"),
            app_commands.Choice(name="Non", value="non")
        ])
        @app_commands.choices(include_inventaire=[
            app_commands.Choice(name="Oui", value="oui"),
            app_commands.Choice(name="Non", value="non")
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
        # Générer le template de fiche
        template = self._generate_template(
            nom_pj, classe, niveau_actuel, niveau_cible,
            titre_quete, mj, xp_actuels, xp_obtenus,
            include_marchand, include_inventaire
        )

        # Créer l'embed avec le template
        embed = discord.Embed(
            title="📋 Template de Mise à Jour de Fiche",
            description=f"Template personnalisé généré pour **{nom_pj}** ({classe})",
            color=0x8B4513
        )

        # Montrer ce qui a été pré-rempli
        infos_preremplies = []
        if titre_quete:
            infos_preremplies.append(f"🎯 Quête: {titre_quete}")
        if mj:
            infos_preremplies.append(f"🎲 MJ: {mj}")
        if niveau_actuel:
            infos_preremplies.append(f"📊 Niveau actuel: {niveau_actuel}")
        if niveau_cible:
            infos_preremplies.append(f"⬆️ Niveau cible: {niveau_cible}")
        if xp_actuels is not None:
            infos_preremplies.append(f"⭐ XP actuels: {xp_actuels}")
        if xp_obtenus is not None:
            infos_preremplies.append(f"✨ XP obtenus: {xp_obtenus}")
        
        sections_incluses = []
        if include_inventaire:
            sections_incluses.append("📦 Inventaire")
        if include_marchand:
            sections_incluses.append("🛒 Marchand")
        
        if infos_preremplies:
            embed.add_field(
                name="✅ Informations pré-remplies",
                value="\n".join(infos_preremplies),
                inline=True
            )
        
        if sections_incluses:
            embed.add_field(
                name="📋 Sections incluses",
                value="\n".join(sections_incluses),
                inline=True
            )

        # Discord a une limite de 1024 caractères par champ d'embed
        # On envoie toujours le template en plusieurs messages pour éviter les erreurs
        embed.add_field(
            name="📝 Template généré",
            value="Template personnalisé envoyé ci-dessous, prêt à utiliser !",
            inline=False
        )
        
        embed.add_field(
            name="💡 Utilisation",
            value="Copiez le template complet et complétez les placeholders `[EN_MAJUSCULES]`",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # Diviser le template en parties plus petites pour Discord
        parts = self._split_template_for_discord(template)
        
        # Calculer la longueur totale du template
        total_length = len(template)
        discord_limit = 2000
        remaining_chars = discord_limit - total_length
        
        for i, part in enumerate(parts, 1):
            part_length = len(part)
            
            # Créer l'embed avec les infos de caractères
            part_embed = discord.Embed(
                title=f"📋 Template - Partie {i}/{len(parts)}",
                description=f"```\n{part}\n```",
                color=0x8B4513
            )
            
            # Ajouter les informations de longueur
            if len(parts) == 1:
                # Template complet dans un seul message
                if remaining_chars >= 0:
                    part_embed.add_field(
                        name="📊 Caractères",
                        value=f"**Longueur :** {total_length}/{discord_limit}\n**✅ Restant :** {remaining_chars} caractères",
                        inline=True
                    )
                else:
                    part_embed.add_field(
                        name="📊 Caractères",
                        value=f"**Longueur :** {total_length}/{discord_limit}\n**⚠️ Dépassement :** {abs(remaining_chars)} caractères",
                        inline=True
                    )
                    part_embed.add_field(
                        name="💡 Conseil",
                        value="Template trop long pour un seul message Discord. Copiez en plusieurs fois ou réduisez le contenu.",
                        inline=False
                    )
            else:
                # Template divisé en plusieurs parties
                part_embed.add_field(
                    name="📊 Cette partie",
                    value=f"**Longueur :** {part_length} caractères",
                    inline=True
                )
                
                if i == len(parts):  # Dernière partie
                    part_embed.add_field(
                        name="📊 Total complet",
                        value=f"**{total_length} caractères** au total\n⚠️ Divisé car > {discord_limit}",
                        inline=True
                    )
            
            await interaction.followup.send(embed=part_embed, ephemeral=True)

    def _generate_template(
        self, nom_pj, classe, niveau_actuel, niveau_cible,
        titre_quete, mj, xp_actuels, xp_obtenus,
        include_marchand, include_inventaire
    ) -> str:
        """Génère le template de mise à jour avec les informations pré-remplies"""
        
        template = f"Nom du PJ : {nom_pj}\n"
        template += f"Classe : {classe}\n\n"
        
        template += "** / =======================  PJ  ========================= \\ **\n"
        
        # Section Quête - PRÉ-REMPLIE
        if titre_quete and mj:
            template += f"**Quête :** {titre_quete} + {mj} ⁠- [LIEN_MESSAGE_RECOMPENSES]\n"
        elif titre_quete:
            template += f"**Quête :** {titre_quete} + [NOM_MJ] ⁠- [LIEN_MESSAGE_RECOMPENSES]\n"
        elif mj:
            template += f"**Quête :** [TITRE_QUETE] + {mj} ⁠- [LIEN_MESSAGE_RECOMPENSES]\n"
        else:
            template += "**Quête :** [TITRE_QUETE] + [NOM_MJ] ⁠- [LIEN_MESSAGE_RECOMPENSES]\n"
        
        # Section XP - CALCULS AUTOMATIQUES
        if xp_actuels is not None and xp_obtenus is not None:
            nouveaux_xp = xp_actuels + xp_obtenus
            if niveau_cible:
                template += f"**Solde XP :** {xp_actuels}/[XP_REQUIS_NIV_{niveau_cible}] + {xp_obtenus} = {nouveaux_xp}/[XP_REQUIS_NIV_{niveau_cible}] -> 🆙 passage au niveau {niveau_cible}\n\n"
            elif niveau_actuel:
                nouveau_niveau = niveau_actuel + 1
                template += f"**Solde XP :** {xp_actuels}/[XP_REQUIS_NIV_{nouveau_niveau}] + {xp_obtenus} = {nouveaux_xp}/[XP_REQUIS_NIV_{nouveau_niveau}] -> 🆙 passage au niveau {nouveau_niveau}\n\n"
            else:
                template += f"**Solde XP :** {xp_actuels}/[XP_REQUIS] + {xp_obtenus} = {nouveaux_xp}/[XP_REQUIS] -> 🆙 passage au niveau [NOUVEAU_NIVEAU]\n\n"
        elif niveau_actuel and niveau_cible:
            template += f"**Solde XP :** [XP_ACTUELS]/[XP_REQUIS_NIV_{niveau_cible}] + [XP_OBTENUS] = [NOUVEAUX_XP]/[XP_REQUIS_NIV_{niveau_cible}] -> 🆙 passage au niveau {niveau_cible}\n\n"
        elif niveau_actuel:
            nouveau_niveau = niveau_actuel + 1
            template += f"**Solde XP :** [XP_ACTUELS]/[XP_REQUIS_NIV_{nouveau_niveau}] + [XP_OBTENUS] = [NOUVEAUX_XP]/[XP_REQUIS_NIV_{nouveau_niveau}] -> 🆙 passage au niveau {nouveau_niveau}\n\n"
        else:
            template += "**Solde XP :** [XP_ACTUELS]/[XP_REQUIS] + [XP_OBTENUS] = [NOUVEAUX_XP]/[XP_REQUIS] -> 🆙 passage au niveau [NOUVEAU_NIVEAU]\n\n"
        
        # Section Gain de niveau - AVEC NIVEAUX PRÉ-REMPLIS
        template += "**Gain de niveau :**\n"
        if niveau_actuel and niveau_cible:
            template += f"PV : [PV_NIVEAU_{niveau_actuel}] + [PV_GAGNES_NIV_{niveau_cible}] = [PV_NIVEAU_{niveau_cible}]\n\n"
        elif niveau_actuel:
            nouveau_niveau = niveau_actuel + 1
            template += f"PV : [PV_NIVEAU_{niveau_actuel}] + [PV_GAGNES_NIV_{nouveau_niveau}] = [PV_NIVEAU_{nouveau_niveau}]\n\n"
        else:
            template += "PV : [ANCIENS_PV] + [PV_OBTENUS] = [NOUVEAUX_PV]\n\n"
        
        # Section Capacités et sorts - AVEC NIVEAUX POUR RÉFÉRENCE
        template += "**¤ Capacités et sorts supplémentaires :**\n"
        if niveau_cible:
            template += f"Nouvelle(s) capacité(s) niveau {niveau_cible} :\n"
        else:
            template += "Nouvelle(s) capacité(s) :\n"
        template += "- [CAPACITE_1]\n"
        template += "- [CAPACITE_2]\n"
        
        if niveau_cible:
            template += f"Nouveau(x) sort(s) niveau {niveau_cible} :\n"
        else:
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

    def _split_template_for_discord(self, template: str) -> list:
        """Divise le template pour respecter les limites Discord (1900 caractères max par message)"""
        max_length = 1900  # Limite sécurisée pour Discord (2000 - marge pour ```\n\n```)
        parts = []
        
        if len(template) <= max_length:
            return [template]
        
        # Diviser par lignes pour préserver la structure
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