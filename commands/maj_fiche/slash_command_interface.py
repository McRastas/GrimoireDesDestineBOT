# commands/maj_fiche/slash_command_interface.py
import discord
from discord import app_commands
from typing import Optional
from .main_command import MajFicheBaseCommand
from .template_generator import TemplateGenerator


class MajFicheSlashCommand(MajFicheBaseCommand):
    """
    Interface de commande slash Discord pour la mise à jour de fiche.
    Gère l'enregistrement des paramètres et l'interaction avec Discord.
    """

    def __init__(self):
        super().__init__()
        self.template_generator = TemplateGenerator()

    @property
    def name(self) -> str:
        return "maj-fiche"

    @property
    def description(self) -> str:
        return "Génère un template de mise à jour de fiche de personnage D&D"

    def register(self, tree: app_commands.CommandTree):
        """Enregistrement de la commande slash avec tous les paramètres et choix."""

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
        @app_commands.choices(classe=self.CLASSES_CHOICES)
        @app_commands.choices(niveau_actuel=self.NIVEAUX_ACTUELS)
        @app_commands.choices(niveau_cible=self.NIVEAUX_CIBLES)
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
            niveau_actuel: Optional[int] = None,
            niveau_cible: Optional[int] = None,
            titre_quete: Optional[str] = None,
            mj: Optional[str] = None,
            xp_actuels: Optional[int] = None,
            xp_obtenus: Optional[int] = None,
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
        niveau_actuel: Optional[int] = None,
        niveau_cible: Optional[int] = None,
        titre_quete: Optional[str] = None,
        mj: Optional[str] = None,
        xp_actuels: Optional[int] = None,
        xp_obtenus: Optional[int] = None,
        include_marchand: bool = False,
        include_inventaire: bool = True
    ):
        """Traite la commande et génère le template de mise à jour."""
        
        # Validation des paramètres d'entrée
        validation_errors = self.validate_parameters(
            nom_pj, classe, niveau_actuel, niveau_cible, xp_actuels, xp_obtenus
        )
        
        # Génération du template
        template = self.template_generator.generate_full_template(
            nom_pj=nom_pj,
            classe=classe,
            niveau_actuel=niveau_actuel,
            niveau_cible=niveau_cible,
            titre_quete=titre_quete,
            mj=mj,
            xp_actuels=xp_actuels,
            xp_obtenus=xp_obtenus,
            include_marchand=include_marchand,
            include_inventaire=include_inventaire
        )

        # Création de l'embed de réponse
        embed = self._create_response_embed(
            nom_pj, classe, niveau_actuel, niveau_cible,
            titre_quete, mj, xp_actuels, xp_obtenus,
            include_marchand, include_inventaire, validation_errors
        )
        
        # Envoi de la réponse initiale
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # Envoi du template (avec gestion de la longueur)
        await self._send_template_with_smart_handling(interaction, template, {
            'nom_pj': nom_pj,
            'classe': classe,
            'niveau_actuel': niveau_actuel,
            'niveau_cible': niveau_cible,
            'validation_errors': validation_errors
        })

    def _create_response_embed(
        self,
        nom_pj: str,
        classe: str,
        niveau_actuel: Optional[int],
        niveau_cible: Optional[int],
        titre_quete: Optional[str],
        mj: Optional[str],
        xp_actuels: Optional[int],
        xp_obtenus: Optional[int],
        include_marchand: bool,
        include_inventaire: bool,
        validation_errors: list
    ) -> discord.Embed:
        """Crée l'embed de réponse avec toutes les informations."""
        
        # Déterminer la couleur selon la classe (thématique D&D)
        class_colors = {
            "Guerrier": 0x8B4513, "Rôdeur": 0x228B22, "Paladin": 0xFFD700, "Barbare": 0xDC143C,
            "Barde": 0xFF69B4, "Ensorceleur": 0x9400D3, "Magicien": 0x4169E1, "Druide": 0x32CD32,
            "Clerc": 0xFFFFE0, "Moine": 0xF4A460, "Roublard": 0x2F4F4F, "Occultiste": 0x800080,
        }
        
        color = class_colors.get(classe, 0x8B4513)
        
        if validation_errors:
            color = self.get_embed_validation_color(validation_errors)
        
        embed = discord.Embed(
            title="📋 Template de Mise à jour de Fiche D&D",
            description=f"Template personnalisé généré pour **{nom_pj}** ({classe})",
            color=color
        )

        # Section personnage avec émojis de classe
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

        # Informations de session avec calculs automatiques
        session_info = []
        if titre_quete:
            session_info.append(f"🎯 **Quête :** {titre_quete}")
        if mj:
            session_info.append(f"🎲 **MJ :** {mj}")
        
        # Calculs XP automatiques avec validation
        if xp_actuels is not None and xp_obtenus is not None:
            nouveaux_xp = xp_actuels + xp_obtenus
            session_info.append(f"⭐ **XP :** {xp_actuels:,} + {xp_obtenus:,} = **{nouveaux_xp:,}**")
            
            # Estimation du niveau selon les XP (table D&D 5e)
            niveau_estime = self._estimate_level_from_xp(nouveaux_xp)
            if niveau_estime > (niveau_actuel or 1):
                session_info.append(f"🆙 **Niveau estimé :** {niveau_estime}")
        elif xp_actuels is not None:
            session_info.append(f"⭐ **XP actuels :** {xp_actuels:,}")
        elif xp_obtenus is not None:
            session_info.append(f"✨ **XP obtenus :** {xp_obtenus:,}")
        
        if session_info:
            embed.add_field(
                name="📝 Session",
                value="\n".join(session_info),
                inline=True
            )

        # Sections incluses avec comptage
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

        # Alertes et validations
        if validation_errors:
            embed.add_field(
                name="⚠️ Alertes",
                value="\n".join(validation_errors),
                inline=False
            )

        # Statistiques du template
        template_stats = self.template_generator.get_template_stats(
            self.template_generator.generate_full_template(
                nom_pj, classe, niveau_actuel, niveau_cible,
                titre_quete, mj, xp_actuels, xp_obtenus,
                include_marchand, include_inventaire
            )
        )
        
        stats_text = f"**Longueur :** {template_stats['length']} caractères"
        if template_stats['is_too_long']:
            stats_text += " ⚠️ (sera divisé)"
        elif template_stats['needs_splitting']:
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
        """Estime le niveau basé sur les XP selon la table D&D 5e."""
        xp_thresholds = [
            0, 300, 900, 2700, 6500, 14000, 23000, 34000, 48000, 64000,
            85000, 100000, 120000, 140000, 165000, 195000, 225000, 265000, 305000, 355000
        ]
        
        for level, threshold in enumerate(xp_thresholds[1:], 2):
            if xp < threshold:
                return level - 1
        return 20

    async def _send_template_with_smart_handling(
        self, 
        interaction: discord.Interaction, 
        template: str, 
        info: dict
    ):
        """Envoie le template avec gestion intelligente de la longueur Discord."""
        
        template_stats = self.template_generator.get_template_stats(template)
        
        if not template_stats['needs_splitting']:
            # Template de taille acceptable - envoi simple
            await self._send_single_template(interaction, template, template_stats, info)
        else:
            # Template trop long - division nécessaire
            await self._send_multi_part_template(interaction, template, template_stats, info)

    async def _send_single_template(
        self, 
        interaction: discord.Interaction, 
        template: str, 
        stats: dict,
        info: dict
    ):
        """Envoie un template en une seule partie."""
        import re
        
        placeholder_count = len(re.findall(r'\[([A-Z_]+)\]', template))
        
        embed = discord.Embed(
            title="✅ Template Généré avec Succès",
            description=f"Votre template pour **{info['nom_pj']}** est prêt à utiliser !",
            color=0x2ecc71
        )
        
        embed.add_field(
            name="📊 Statistiques",
            value=f"**Caractères :** {stats['length']}\n**Placeholders :** {placeholder_count}\n**Sections :** {stats['sections']}",
            inline=True
        )
        
        if info['niveau_actuel'] and info['niveau_cible']:
            embed.add_field(
                name="📈 Progression",
                value=f"Niveau {info['niveau_actuel']} → {info['niveau_cible']}",
                inline=True
            )
        
        if info['validation_errors']:
            embed.add_field(
                name="⚠️ Attention",
                value="\n".join(info['validation_errors'][:2]),
                inline=False
            )
        
        embed.add_field(
            name="📝 Instructions",
            value="1. **Copiez** le template ci-dessous\n2. **Complétez** les placeholders [EN_MAJUSCULES]\n3. **Postez** dans le canal approprié",
            inline=False
        )
        
        await interaction.followup.send(embed=embed, ephemeral=True)
        
        # Envoyer le template en tant que message séparé
        template_embed = discord.Embed(
            title="📋 Votre Template de Mise à Jour",
            description=f"```\n{template}\n```",
            color=0x3498db
        )
        
        await interaction.followup.send(embed=template_embed, ephemeral=True)

    async def _send_multi_part_template(
        self, 
        interaction: discord.Interaction, 
        template: str, 
        stats: dict,
        info: dict
    ):
        """Envoie un template divisé en plusieurs parties."""
        import re
        
        parts = self.template_generator.split_template_if_needed(template)
        placeholder_count = len(re.findall(r'\[([A-Z_]+)\]', template))
        
        # Embed d'introduction
        embed_intro = discord.Embed(
            title="📋 Template Multi-parties",
            description=f"Template pour **{info['nom_pj']}** - Divisé en {len(parts)} parties",
            color=0xf39c12
        )
        
        embed_intro.add_field(
            name="📊 Informations",
            value=f"**Total :** {stats['length']} caractères\n**Placeholders :** {placeholder_count}\n**Parties :** {len(parts)}",
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
            value="1. **Copiez** chaque partie dans l'ordre\n2. **Assemblez** en un seul message\n3. **Complétez** les placeholders\n4. **Postez** le résultat final",
            inline=False
        )
        
        await interaction.followup.send(embed=embed_intro, ephemeral=True)
        
        # Envoyer chaque partie
        for i, part in enumerate(parts, 1):
            part_embed = discord.Embed(
                title=f"📄 Partie {i}/{len(parts)}",
                description=f"```\n{part}\n```",
                color=0x3498db
            )
            
            if i == len(parts):
                part_embed.set_footer(text="✅ Fin du template - Assemblez toutes les parties")
            
            await interaction.followup.send(embed=part_embed, ephemeral=True)