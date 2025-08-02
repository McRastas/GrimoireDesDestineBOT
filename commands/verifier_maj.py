# commands/verifier_maj.py
"""
Commande de vérification de template de mise à jour de fiche D&D.
Version améliorée utilisant les modules du répertoire maj_fiche.
"""

import discord
from discord import app_commands
import re
import logging
from typing import Optional, Dict, Any
from .base import BaseCommand

# Import des modules maj_fiche pour la logique de validation
from .maj_fiche.validation_system import TemplateValidator
from .maj_fiche.template_generator import TemplateGenerator
from .maj_fiche.main_command import MajFicheBaseCommand

logger = logging.getLogger(__name__)


class VerifierMajCommand(BaseCommand):
    """
    Commande pour vérifier et corriger les templates de mise à jour de fiche D&D.
    Utilise les modules maj_fiche pour une validation cohérente.
    """

    def __init__(self, bot):
        super().__init__(bot)
        self.validator = TemplateValidator()
        self.generator = TemplateGenerator()
        self.base_command = MajFicheBaseCommand(bot)

    @property
    def name(self) -> str:
        return "verifier-maj"

    @property
    def description(self) -> str:
        return "Vérifie et propose des corrections pour un template de mise à jour de fiche D&D"

    def register(self, tree: app_commands.CommandTree):
        """Enregistrement avec paramètres optimisés"""

        @tree.command(name=self.name, description=self.description)
        @app_commands.describe(
            lien_message="Lien vers le message à vérifier (clic droit > Copier le lien du message)",
            mode_correction="Type de correction à appliquer",
            proposer_ameliorations="Proposer des améliorations supplémentaires"
        )
        @app_commands.choices(mode_correction=[
            app_commands.Choice(name="🔧 Corrections automatiques + suggestions", value="auto"),
            app_commands.Choice(name="📋 Vérification uniquement", value="check"),
            app_commands.Choice(name="✨ Corrections + optimisations avancées", value="advanced")
        ])
        @app_commands.choices(proposer_ameliorations=[
            app_commands.Choice(name="✅ Oui - Suggérer des améliorations", value="oui"),
            app_commands.Choice(name="❌ Non - Validation simple", value="non")
        ])
        async def verifier_maj_command(
            interaction: discord.Interaction,
            lien_message: str,
            mode_correction: str = "auto",
            proposer_ameliorations: str = "oui"
        ):
            await self.callback(
                interaction, 
                lien_message, 
                mode_correction, 
                proposer_ameliorations == "oui"
            )

    async def callback(
        self, 
        interaction: discord.Interaction, 
        lien_message: str,
        mode_correction: str = "auto",
        proposer_ameliorations: bool = True
    ):
        """Callback principal avec gestion d'erreur robuste"""
        try:
            # Différer la réponse pour éviter les timeouts
            await interaction.response.defer(ephemeral=True)
            
            logger.info(f"Vérification template demandée par {interaction.user} - Mode: {mode_correction}")
            
            # Parser et valider le lien Discord
            message_info = self._parse_discord_link(lien_message)
            if not message_info:
                await interaction.followup.send(
                    embed=self._create_error_embed(
                        "Lien invalide",
                        "Utilisez un lien Discord valide :\n"
                        "• **Clic droit** sur le message → **Copier le lien du message**\n"
                        "• Format attendu : `https://discord.com/channels/123.../456.../789...`\n\n"
                        "💡 **Astuce :** Activez le Mode Développeur dans Discord si nécessaire."
                    ),
                    ephemeral=True
                )
                return

            # Récupérer le message Discord
            message = await self._fetch_discord_message(interaction, message_info)
            if not message:
                return  # L'erreur a déjà été envoyée

            # Vérifier le contenu du message
            if not message.content.strip():
                await interaction.followup.send(
                    embed=self._create_error_embed(
                        "Message vide",
                        "Le message ne contient pas de texte à analyser.\n"
                        "Vérifiez que vous avez sélectionné le bon message avec le template de MAJ."
                    ),
                    ephemeral=True
                )
                return

            # Effectuer la validation avec le système maj_fiche
            verification_result = self.validator.verify_template(message.content)
            
            # Générer les corrections selon le mode choisi
            corrections = None
            if mode_correction in ["auto", "advanced"]:
                corrections = self.validator.generate_corrections(message.content, verification_result)
                
                # Mode avancé : ajouter des optimisations supplémentaires
                if mode_correction == "advanced":
                    corrections = self._add_advanced_optimizations(corrections, message.content)

            # Créer l'embed de résultats
            result_embed = self._create_verification_embed(
                message, verification_result, corrections, mode_correction
            )
            
            # Envoyer l'embed de résultats
            await interaction.followup.send(embed=result_embed, ephemeral=True)
            
            # Envoyer le template corrigé si nécessaire
            if mode_correction != "check":
                await self._send_corrected_template(
                    interaction, message.content, verification_result, corrections, proposer_ameliorations
                )
            
            logger.info(f"Vérification terminée avec succès pour {interaction.user}")
            
        except Exception as e:
            logger.error(f"Erreur dans verifier-maj: {e}", exc_info=True)
            
            error_embed = self._create_error_embed(
                "Erreur inattendue",
                f"Une erreur s'est produite lors de la vérification.\n\n"
                f"**Erreur :** {str(e)}\n\n"
                f"💡 **Solutions :**\n"
                f"• Vérifiez que le lien est correct et complet\n"
                f"• Réessayez dans quelques instants\n"
                f"• Contactez un administrateur si le problème persiste"
            )
            
            try:
                await interaction.followup.send(embed=error_embed, ephemeral=True)
            except:
                logger.error(f"Impossible d'envoyer le message d'erreur pour {interaction.user}")

    def _parse_discord_link(self, link: str) -> Optional[tuple]:
        """
        Parse un lien Discord pour extraire guild_id, channel_id, message_id.
        Version améliorée avec support de plusieurs formats.
        """
        # Nettoyer le lien
        link = link.strip().strip('<>')
        
        # Ajouter https:// si manquant
        if not link.startswith(('http://', 'https://')):
            if link.startswith('discord'):
                link = 'https://' + link
            else:
                return None
        
        # Patterns pour différents formats Discord
        patterns = [
            r'https?://(?:www\.)?discord(?:app)?\.com/channels/(\d+)/(\d+)/(\d+)',
            r'https?://(?:www\.)?discord\.gg/channels/(\d+)/(\d+)/(\d+)',
            r'https?://ptb\.discord(?:app)?\.com/channels/(\d+)/(\d+)/(\d+)',
            r'https?://canary\.discord(?:app)?\.com/channels/(\d+)/(\d+)/(\d+)'
        ]
        
        for pattern in patterns:
            match = re.match(pattern, link)
            if match:
                try:
                    return (int(match.group(1)), int(match.group(2)), int(match.group(3)))
                except ValueError:
                    continue
        
        return None

    async def _fetch_discord_message(
        self, 
        interaction: discord.Interaction, 
        message_info: tuple
    ) -> Optional[discord.Message]:
        """Récupère le message Discord avec gestion d'erreur complète"""
        
        guild_id, channel_id, message_id = message_info
        
        # Vérifier le serveur
        if guild_id != interaction.guild.id:
            await interaction.followup.send(
                embed=self._create_error_embed(
                    "Serveur différent",
                    f"Le message se trouve sur un autre serveur.\n\n"
                    f"• **Message :** Serveur ID `{guild_id}`\n"
                    f"• **Commande :** Serveur ID `{interaction.guild.id}`\n\n"
                    f"Utilisez cette commande sur le même serveur que le message."
                ),
                ephemeral=True
            )
            return None
        
        # Récupérer le canal
        try:
            channel = interaction.guild.get_channel(int(channel_id))
            if not channel:
                await interaction.followup.send(
                    embed=self._create_error_embed(
                        "Canal introuvable",
                        f"Le canal avec l'ID `{channel_id}` n'existe pas ou n'est pas accessible.\n\n"
                        f"**Vérifiez que :**\n"
                        f"• Le canal existe toujours\n"
                        f"• Le bot a accès à ce canal\n"
                        f"• Le lien est correct"
                    ),
                    ephemeral=True
                )
                return None
        except Exception as e:
            await interaction.followup.send(
                embed=self._create_error_embed(
                    "Erreur d'accès au canal",
                    f"Impossible d'accéder au canal : {str(e)}"
                ),
                ephemeral=True
            )
            return None
        
        # Récupérer le message
        try:
            message = await channel.fetch_message(int(message_id))
            return message
        except discord.NotFound:
            await interaction.followup.send(
                embed=self._create_error_embed(
                    "Message introuvable",
                    f"Le message avec l'ID `{message_id}` n'existe pas dans {channel.mention}.\n\n"
                    f"**Vérifiez que :**\n"
                    f"• Le message n'a pas été supprimé\n"
                    f"• Le lien est correct et complet\n"
                    f"• Vous avez copié le bon lien"
                ),
                ephemeral=True
            )
            return None
        except discord.Forbidden:
            await interaction.followup.send(
                embed=self._create_error_embed(
                    "Accès refusé",
                    f"Le bot n'a pas les permissions pour lire les messages dans {channel.mention}.\n"
                    f"Contactez un administrateur pour accorder les permissions nécessaires."
                ),
                ephemeral=True
            )
            return None
        except Exception as e:
            await interaction.followup.send(
                embed=self._create_error_embed(
                    "Erreur de récupération",
                    f"Erreur lors de la récupération du message : {str(e)}"
                ),
                ephemeral=True
            )
            return None

    def _create_verification_embed(
        self, 
        message: discord.Message, 
        verification_result: Dict[str, Any],
        corrections: Optional[Dict[str, Any]] = None,
        mode: str = "auto"
    ) -> discord.Embed:
        """Crée l'embed de résultats de vérification avec les infos maj_fiche"""
        
        completion = verification_result.get('completion_percentage', 0)
        
        # Déterminer couleur et statut
        if completion >= 90:
            color, emoji, status = 0x2ecc71, "✅", "Excellent"
        elif completion >= 70:
            color, emoji, status = 0xf39c12, "🟡", "Bon"
        elif completion >= 50:
            color, emoji, status = 0xff9900, "🟠", "Passable"
        else:
            color, emoji, status = 0xe74c3c, "❌", "Insuffisant"
        
        embed = discord.Embed(
            title=f"{emoji} Vérification Template D&D",
            description=f"**Statut :** {status} ({completion:.0f}% complet)",
            color=color
        )
        
        # Informations du message
        embed.add_field(
            name="📝 Message analysé",
            value=(
                f"**Auteur :** {message.author.mention}\n"
                f"**Canal :** {message.channel.mention}\n"
                f"**Date :** {discord.utils.format_dt(message.created_at, 'R')}"
            ),
            inline=False
        )
        
        # Score détaillé avec système maj_fiche
        score_text = (
            f"**{verification_result['score']}/{verification_result['total_checks']}** sections obligatoires\n"
            f"**{completion:.1f}%** de conformité\n"
            f"**{len(verification_result.get('placeholders', []))}** placeholders à compléter"
        )
        embed.add_field(
            name="📊 Analyse détaillée",
            value=score_text,
            inline=True
        )
        
        # Informations personnage détectées
        details = verification_result.get('details', {})
        if details.get('nom_pj') or details.get('classe'):
            char_info = []
            if details.get('nom_pj'):
                char_info.append(f"**PJ :** {details['nom_pj']}")
            if details.get('classe'):
                char_info.append(f"**Classe :** {details['classe']}")
            
            embed.add_field(
                name="🎭 Personnage",
                value=self._safe_field_value("\n".join(char_info)),
                inline=True
            )
        
        # Sections manquantes (limitées pour l'affichage)
        if verification_result.get('sections_missing'):
            missing_labels = []
            section_labels = {
                'nom_pj': 'Nom PJ', 'classe': 'Classe', 'quete': 'Quête',
                'solde_xp': 'Solde XP', 'gain_niveau': 'Gain niveau',
                'capacites': 'Capacités', 'solde_final': 'Solde final'
            }
            
            for section in verification_result['sections_missing'][:5]:
                label = section_labels.get(section, section)
                missing_labels.append(f"• {label}")
            
            if len(verification_result['sections_missing']) > 5:
                missing_labels.append(f"• ... et {len(verification_result['sections_missing']) - 5} autres")
            
            embed.add_field(
                name="❌ Sections manquantes",
                value=self._safe_field_value("\n".join(missing_labels)),
                inline=False
            )
        
        # Corrections automatiques appliquées
        if corrections and corrections.get('automatic_fixes'):
            fixes_text = "\n".join([f"✅ {fix}" for fix in corrections['automatic_fixes'][:4]])
            embed.add_field(
                name="🔧 Corrections automatiques",
                value=self._safe_field_value(fixes_text),
                inline=False
            )
        
        # Alertes importantes
        warnings = verification_result.get('warnings', [])
        if warnings:
            warnings_text = "\n".join([f"⚠️ {w}" for w in warnings[:3]])
            embed.add_field(
                name="⚠️ Alertes",
                value=self._safe_field_value(warnings_text),
                inline=False
            )
        
        # Footer avec informations sur le mode
        mode_descriptions = {
            "check": "Mode vérification uniquement",
            "auto": "Mode corrections automatiques",
            "advanced": "Mode optimisations avancées"
        }
        
        embed.set_footer(
            text=f"{mode_descriptions.get(mode, 'Mode inconnu')} • Système maj_fiche v2.0"
        )
        embed.timestamp = discord.utils.utcnow()
        
        return embed

    def _add_advanced_optimizations(
        self, 
        corrections: Dict[str, Any], 
        content: str
    ) -> Dict[str, Any]:
        """Ajoute des optimisations avancées au mode advanced"""
        
        if not corrections.get('improvements'):
            corrections['improvements'] = []
        
        # Optimisations avancées spécifiques
        
        # 1. Optimisation des calculs XP avec table D&D
        if re.search(r'\[XP_', content):
            corrections['improvements'].append({
                'type': 'Calculs XP automatiques',
                'description': 'Utiliser les calculs automatiques XP basés sur les niveaux D&D 5e',
                'priority': 'Haute',
                'template': '**Solde XP :** [XP_ACTUELS] + [XP_OBTENUS] = [NOUVEAUX_XP] -> 🆙 passage au niveau [NOUVEAU_NIVEAU]'
            })
        
        # 2. Suggestions de sorts par classe
        if re.search(r'\[SORT_', content):
            classe_match = re.search(r'Classe\s*:\s*([A-Za-zÀ-ÿ]+)', content)
            if classe_match:
                classe = classe_match.group(1)
                suggestions = self.generator.add_class_specific_suggestions(classe, 3)  # Niveau exemple
                if suggestions.get('spells'):
                    corrections['improvements'].append({
                        'type': 'Suggestions de sorts',
                        'description': f'Sorts recommandés pour {classe} : {", ".join(suggestions["spells"][:3])}',
                        'priority': 'Moyenne'
                    })
        
        # 3. Optimisation de la structure
        if len(content) > 1800:
            corrections['improvements'].append({
                'type': 'Optimisation longueur',
                'description': 'Réorganiser le template pour optimiser la longueur Discord',
                'priority': 'Moyenne'
            })
        
        # 4. Validation des calculs PV
        if re.search(r'PV\s*:', content):
            corrections['improvements'].append({
                'type': 'Validation PV',
                'description': 'Vérifier la cohérence des calculs de Points de Vie avec les modificateurs',
                'priority': 'Haute'
            })
        
        return corrections

    async def _send_corrected_template(
        self,
        interaction: discord.Interaction,
        original_content: str,
        verification_result: Dict[str, Any],
        corrections: Optional[Dict[str, Any]],
        include_improvements: bool
    ):
        """Envoie le template corrigé en utilisant la logique maj_fiche"""
        
        # Déterminer le template à envoyer
        if corrections and corrections.get('corrected_template'):
            final_template = corrections['corrected_template']
            template_type = "corrigé"
        else:
            # Utiliser le nettoyage basique si pas de corrections
            final_template = self._clean_template_basic(original_content)
            template_type = "nettoyé"
        
        # Calculer les statistiques avec le système maj_fiche
        template_stats = self.generator.get_template_stats(final_template)
        
        # Créer l'embed principal
        embed = discord.Embed(
            title=f"📋 Template D&D {template_type.title()}",
            description=f"Votre template a été {template_type} et optimisé avec le système maj_fiche.",
            color=0x2ecc71 if template_type == "corrigé" else 0x3498db
        )
        
        # Statistiques du template
        embed.add_field(
            name="📊 Statistiques",
            value=(
                f"**Caractères :** {template_stats['length']}/2000\n"
                f"**Placeholders :** {template_stats['placeholders']}\n"
                f"**Sections :** {template_stats['sections']}"
            ),
            inline=True
        )
        
        # Résumé des corrections
        if corrections:
            fixes_count = len(corrections.get('automatic_fixes', []))
            manual_count = len(corrections.get('manual_corrections', []))
            
            embed.add_field(
                name="🔧 Corrections appliquées",
                value=(
                    f"**Automatiques :** {fixes_count}\n"
                    f"**Manuelles suggérées :** {manual_count}\n"
                    f"**Qualité :** {self.validator.get_validation_summary(verification_result)}"
                ),
                inline=True
            )
        
        # Instructions selon l'état
        placeholder_count = template_stats['placeholders']
        if placeholder_count > 0:
            embed.add_field(
                name="📝 Prochaines étapes",
                value=(
                    f"1. **Copiez** le template ci-dessous\n"
                    f"2. **Complétez** les {placeholder_count} placeholders [EN_MAJUSCULES]\n"
                    f"3. **Vérifiez** les calculs XP et PV\n"
                    f"4. **Utilisez** dans le canal approprié"
                ),
                inline=False
            )
        else:
            embed.add_field(
                name="🎯 Template prêt !",
                value="✅ Aucun placeholder à compléter\n✅ Prêt à utiliser directement\n✅ Validé par le système maj_fiche",
                inline=False
            )
        
        # Envoyer l'embed d'introduction
        await interaction.followup.send(embed=embed, ephemeral=True)
        
        # Envoyer le template selon sa longueur
        if template_stats['needs_splitting']:
            await self._send_template_multipart(interaction, final_template, template_stats)
        else:
            await self._send_template_single(interaction, final_template, template_stats)
        
        # Envoyer les améliorations suggérées si demandées
        if include_improvements and corrections and corrections.get('improvements'):
            await self._send_improvements_suggestions(interaction, corrections['improvements'])

    async def _send_template_single(
        self, 
        interaction: discord.Interaction, 
        template: str, 
        stats: Dict[str, Any]
    ):
        """Envoie un template en une seule partie"""
        
        embed = discord.Embed(
            title="📄 Votre Template Final",
            description=f"Template complet ({stats['length']} caractères)",
            color=0x3498db
        )
        
        # Diviser le template en chunks pour l'embed
        max_field_length = 1020
        if len(template) <= max_field_length:
            embed.add_field(
                name="Template complet",
                value=f"```\n{template}\n```",
                inline=False
            )
        else:
            # Template trop long même pour un seul embed
            template_chunks = [template[i:i+max_field_length-10] for i in range(0, len(template), max_field_length-10)]
            
            for i, chunk in enumerate(template_chunks[:3]):  # Limiter à 3 chunks max
                embed.add_field(
                    name=f"Template (partie {i+1})" if len(template_chunks) > 1 else "Template",
                    value=f"```\n{chunk}\n```",
                    inline=False
                )
        
        await interaction.followup.send(embed=embed, ephemeral=True)

    async def _send_template_multipart(
        self, 
        interaction: discord.Interaction, 
        template: str, 
        stats: Dict[str, Any]
    ):
        """Envoie un template divisé en plusieurs parties"""
        
        parts = self.generator.split_template_if_needed(template)
        
        for i, part in enumerate(parts, 1):
            embed = discord.Embed(
                title=f"📄 Template - Partie {i}/{len(parts)}",
                description=f"```\n{part}\n```",
                color=0x3498db
            )
            
            embed.add_field(
                name="📏 Informations",
                value=f"**Partie :** {i}/{len(parts)}\n**Caractères :** {len(part)}",
                inline=True
            )
            
            if i == 1:
                embed.add_field(
                    name="💡 Instructions",
                    value="Copiez chaque partie dans l'ordre et assemblez-les",
                    inline=True
                )
            elif i == len(parts):
                embed.add_field(
                    name="✅ Terminé",
                    value=f"Template complet reconstitué ! Total: {stats['length']} caractères",
                    inline=True
                )
            
            await interaction.followup.send(embed=embed, ephemeral=True)

    async def _send_improvements_suggestions(
        self, 
        interaction: discord.Interaction, 
        improvements: list
    ):
        """Envoie les suggestions d'amélioration"""
        
        if not improvements:
            return
        
        embed = discord.Embed(
            title="💡 Suggestions d'Amélioration",
            description="Améliorations supplémentaires recommandées pour votre template :",
            color=0xf39c12
        )
        
        priority_colors = {"Haute": "🔴", "Moyenne": "🟡", "Basse": "🟢"}
        
        for i, improvement in enumerate(improvements[:5], 1):  # Limiter à 5 suggestions
            priority = improvement.get('priority', 'Moyenne')
            priority_emoji = priority_colors.get(priority, "⚪")
            
            embed.add_field(
                name=f"{priority_emoji} {improvement.get('type', 'Amélioration')}",
                value=f"{improvement.get('description', 'Aucune description')}\n**Priorité :** {priority}",
                inline=False
            )
        
        if len(improvements) > 5:
            embed.add_field(
                name="📝 Note",
                value=f"+ {len(improvements) - 5} autres suggestions disponibles",
                inline=False
            )
        
        await interaction.followup.send(embed=embed, ephemeral=True)

    def _clean_template_basic(self, content: str) -> str:
        """Nettoyage basique du template sans les modules maj_fiche"""
        
        cleaned = content.strip()
        
        # Normaliser les espaces multiples
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
        
        # Normaliser les séparateurs PJ
        cleaned = re.sub(
            r'\*\*\s*/\s*=+\s*PJ\s*=+\s*\\\s*\*\*',
            '** / =======================  PJ  ========================= \\ **',
            cleaned
        )
        cleaned = re.sub(
            r'\*\*\s*\\\s*=+\s*PJ\s*=+\s*/\s*\*\*',
            '** \\ =======================  PJ  ========================= / **',
            cleaned
        )
        
        return cleaned

    def _create_error_embed(self, title: str, description: str) -> discord.Embed:
        """Crée un embed d'erreur standardisé"""
        
        embed = discord.Embed(
            title=f"❌ {title}",
            description=description,
            color=0xe74c3c
        )
        
        embed.set_footer(text="Commande verifier-maj • Système maj_fiche")
        embed.timestamp = discord.utils.utcnow()
        
        return embed

    def _safe_field_value(self, text: str, max_length: int = 1020) -> str:
        """Sécurise un texte pour les champs Discord"""
        if len(text) <= max_length:
            return text
        return text[:max_length-3] + "..."