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
            description=f"Template généré pour **{nom_pj}** ({classe})",
            color=0x8B4513
        )

        # Le template est trop long pour un embed, on l'envoie en code block
        if len(template) > 4000:
            # Si trop long, diviser en plusieurs parties
            parts = self._split_template(template)
            
            embed.add_field(
                name="📝 Template généré",
                value="Template trop long, envoyé en plusieurs messages.",
                inline=False
            )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
            for i, part in enumerate(parts, 1):
                part_embed = discord.Embed(
                    title=f"📋 Template - Partie {i}/{len(parts)}",
                    description=f"```\n{part}\n```",
                    color=0x8B4513
                )
                await interaction.followup.send(embed=part_embed, ephemeral=True)
        else:
            embed.add_field(
                name="📝 Template généré",
                value=f"```\n{template}\n```",
                inline=False
            )
            
            embed.add_field(
                name="💡 Utilisation",
                value="Copiez ce template et remplissez les informations manquantes",
                inline=False
            )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)

    def _generate_template(
        self, nom_pj, classe, niveau_actuel, niveau_cible,
        titre_quete, mj, xp_actuels, xp_obtenus,
        include_marchand, include_inventaire
    ) -> str:
        """Génère le template de mise à jour"""
        
        template = f"Nom du PJ : {nom_pj}\n"
        template += f"Classe : {classe}\n\n"
        
        template += "** / =======================  PJ  ========================= \\ **\n"
        
        # Section Quête
        if titre_quete and mj:
            template += f"**Quête :** {titre_quete} + {mj} ⁠- lien du message dans ⁠récompenses\n"
        elif titre_quete:
            template += f"**Quête :** {titre_quete} + [NOM_MJ] ⁠- lien du message dans ⁠récompenses\n"
        else:
            template += "**Quête :** [TITRE_QUETE] + [NOM_MJ] ⁠- lien du message dans ⁠récompenses\n"
        
        # Section XP
        if xp_actuels is not None and xp_obtenus is not None:
            nouveaux_xp = xp_actuels + xp_obtenus
            if niveau_cible:
                template += f"**Solde XP :** {xp_actuels}/[XP_REQUIS] + {xp_obtenus} = {nouveaux_xp}/[XP_REQUIS] -> 🆙 passage au niveau {niveau_cible}\n\n"
            else:
                template += f"**Solde XP :** {xp_actuels}/[XP_REQUIS] + {xp_obtenus} = {nouveaux_xp}/[XP_REQUIS] -> 🆙 passage au niveau [NOUVEAU_NIVEAU]\n\n"
        elif niveau_actuel and niveau_cible:
            template += f"**Solde XP :** [XP_ACTUELS]/[XP_REQUIS] + [XP_OBTENUS] = [NOUVEAUX_XP]/[XP_REQUIS] -> 🆙 passage au niveau {niveau_cible}\n\n"
        else:
            template += "**Solde XP :** [XP_ACTUELS]/[XP_REQUIS] + [XP_OBTENUS] = [NOUVEAUX_XP]/[XP_REQUIS] -> 🆙 passage au niveau [NOUVEAU_NIVEAU]\n\n"
        
        # Section Gain de niveau
        template += "**Gain de niveau :**\n"
        template += "PV : [ANCIENS_PV] + [PV_OBTENUS] = [NOUVEAUX_PV]\n\n"
        
        # Section Capacités et sorts
        template += "**¤ Capacités et sorts supplémentaires :**\n"
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
            template += "Objets lootés :\n"
            template += "- [OBJET_1]\n"
            template += "- [OBJET_2]\n"
            template += "PO lootées: [MONTANT_PO]\n"
        
        template += "** \\ =======================  PJ  ========================= / **\n\n"
        
        # Section Marchand (si demandée)
        if include_marchand:
            template += "**/ ===================== Marchand ===================== \\ **\n"
            template += "**¤ Inventaire**\n"
            template += "ACHAT / VENTE : [QUANTITE] [OBJET] x [PRIX_UNITAIRE] = [MONTANT_TOTAL]\n"
            template += "ACHAT / VENTE : [QUANTITE] [OBJET] x [PRIX_UNITAIRE] = [MONTANT_TOTAL]\n"
            template += "** \\ ==================== Marchand ====================== / **\n\n"
        
        # Section Solde final
        template += "**¤ Solde :**\n"
        template += "[ANCIEN_SOLDE] +/- [PO_RECUES_DEPENSEES] = [NOUVEAU_SOLDE]\n\n"
        template += "*Fiche R20 à jour.*"
        
        return template

    def _split_template(self, template: str) -> list:
        """Divise le template en plusieurs parties si trop long"""
        max_length = 3800  # Laisser de la marge pour l'embed
        parts = []
        
        if len(template) <= max_length:
            return [template]
        
        # Diviser par sections principales
        sections = template.split("** / =")
        current_part = ""
        
        for i, section in enumerate(sections):
            if i > 0:
                section = "** / =" + section
            
            if len(current_part + section) > max_length:
                if current_part:
                    parts.append(current_part.strip())
                current_part = section
            else:
                current_part += section
        
        if current_part:
            parts.append(current_part.strip())
        
        return parts