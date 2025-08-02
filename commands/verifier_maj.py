# commands/verifier_maj.py
import discord
from discord import app_commands
import re
from .base import BaseCommand


class VerifierMajCommand(BaseCommand):

    @property
    def name(self) -> str:
        return "verifier-maj"

    @property
    def description(self) -> str:
        return "Vérifie et propose des ajustements pour un template de mise à jour de fiche D&D"

    def register(self, tree: app_commands.CommandTree):
        """Enregistrement avec paramètre de lien de message"""

        @tree.command(name=self.name, description=self.description)
        @app_commands.describe(
            lien_message="Lien vers le message à vérifier (clic droit > Copier le lien du message)",
            proposer_corrections="Proposer des corrections automatiques"
        )
        @app_commands.choices(proposer_corrections=[
            app_commands.Choice(name="Oui, proposer des ajustements", value="oui"),
            app_commands.Choice(name="Non, vérification seulement", value="non")
        ])
        async def verifier_maj_command(
            interaction: discord.Interaction,
            lien_message: str,
            proposer_corrections: str = "oui"
        ):
            await self.callback(interaction, lien_message, proposer_corrections == "oui")

    async def callback(
        self, 
        interaction: discord.Interaction, 
        lien_message: str,
        proposer_corrections: bool = True
    ):
        try:
            # Parser le lien Discord pour extraire les IDs
            message_info = self._parse_discord_link(lien_message)
            if not message_info:
                await interaction.response.send_message(
                    "❌ **Lien invalide**\n\n"
                    "Utilisez un lien Discord valide :\n"
                    "• **Clic droit** sur le message → **Copier le lien du message**\n"
                    "• Le lien doit ressembler à : `https://discord.com/channels/123.../456.../789...`\n\n"
                    "💡 **Conseil :** Activez le Mode Développeur dans Discord pour accéder facilement aux liens de messages.",
                    ephemeral=True
                )
                return

            guild_id, channel_id, message_id = message_info

            # Vérifier que nous sommes dans le bon serveur
            if guild_id != interaction.guild.id:
                await interaction.response.send_message(
                    f"❌ **Serveur différent**\n\n"
                    f"Le message se trouve sur un autre serveur.\n"
                    f"• **Message :** Serveur ID `{guild_id}`\n"
                    f"• **Commande :** Serveur ID `{interaction.guild.id}`\n\n"
                    f"Utilisez cette commande sur le même serveur que le message à vérifier.",
                    ephemeral=True
                )
                return

            # Récupérer le canal
            try:
                channel = interaction.guild.get_channel(int(channel_id))
                if not channel:
                    await interaction.response.send_message(
                        f"❌ **Canal introuvable**\n\n"
                        f"Le canal avec l'ID `{channel_id}` n'existe pas ou n'est pas accessible.\n"
                        f"Vérifiez que :\n"
                        f"• Le canal existe toujours\n"
                        f"• Le bot a accès à ce canal\n"
                        f"• Le lien est correct",
                        ephemeral=True
                    )
                    return
            except Exception as e:
                await interaction.response.send_message(
                    f"❌ **Erreur d'accès au canal**\n\n"
                    f"Impossible d'accéder au canal : {str(e)}",
                    ephemeral=True
                )
                return

            # Récupérer le message
            try:
                message = await channel.fetch_message(int(message_id))
            except discord.NotFound:
                await interaction.response.send_message(
                    f"❌ **Message introuvable**\n\n"
                    f"Le message avec l'ID `{message_id}` n'existe pas dans {channel.mention}.\n"
                    f"Vérifiez que :\n"
                    f"• Le message n'a pas été supprimé\n"
                    f"• Le lien est correct et complet\n"
                    f"• Vous avez copié le bon lien",
                    ephemeral=True
                )
                return
            except discord.Forbidden:
                await interaction.response.send_message(
                    f"❌ **Accès refusé**\n\n"
                    f"Le bot n'a pas les permissions pour lire les messages dans {channel.mention}.\n"
                    f"Contactez un administrateur pour accorder les permissions nécessaires.",
                    ephemeral=True
                )
                return
            except Exception as e:
                await interaction.response.send_message(
                    f"❌ **Erreur lors de la récupération du message**\n\n"
                    f"Erreur : {str(e)}",
                    ephemeral=True
                )
                return

            # Vérifier que le message a du contenu
            if not message.content.strip():
                await interaction.response.send_message(
                    "❌ **Message vide**\n\n"
                    "Le message ne contient pas de texte à analyser.\n"
                    "Vérifiez que vous avez sélectionné le bon message avec le template de MAJ.",
                    ephemeral=True
                )
                return

            # Effectuer la vérification
            verification_result = self._verify_template(message.content)
            
            # Générer des suggestions si demandé
            suggestions = None
            if proposer_corrections and verification_result['score'] < verification_result['total_checks']:
                suggestions = self._generate_suggestions(message.content, verification_result)
            
            # Créer l'embed de résultat
            embed = self._create_verification_embed(message, verification_result, suggestions)
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
            # NOUVEAU : Envoyer TOUJOURS le template (original ou corrigé)
            template_to_send = None
            if suggestions and suggestions.get('corrected_template'):
                template_to_send = suggestions['corrected_template']
            else:
                # Même si parfait, renvoyer le template original nettoyé
                template_to_send = self._clean_template(message.content)
            
            await self._send_corrected_template(interaction, template_to_send, suggestions)

        except Exception as e:
            await interaction.response.send_message(
                f"❌ **Erreur inattendue**\n\n"
                f"Une erreur s'est produite lors de la vérification : {str(e)}\n\n"
                f"💡 **Vérifiez que :**\n"
                f"• Le lien Discord est complet et correct\n"
                f"• Le message existe toujours\n"
                f"• Vous avez les bonnes permissions", 
                ephemeral=True
            )

    def _parse_discord_link(self, link: str) -> tuple:
        """
        Parse un lien Discord pour extraire guild_id, channel_id, message_id.
        
        Formats acceptés:
        - https://discord.com/channels/GUILD_ID/CHANNEL_ID/MESSAGE_ID
        - https://discordapp.com/channels/GUILD_ID/CHANNEL_ID/MESSAGE_ID
        - discord.com/channels/GUILD_ID/CHANNEL_ID/MESSAGE_ID (sans https)
        
        Returns:
            tuple: (guild_id, channel_id, message_id) ou None si invalide
        """
        # Nettoyer le lien (supprimer les espaces, <> si présents)
        link = link.strip().strip('<>')
        
        # Ajouter https:// si manquant
        if not link.startswith(('http://', 'https://')):
            if link.startswith('discord'):
                link = 'https://' + link
            else:
                return None
        
        # Pattern pour matcher les liens Discord
        patterns = [
            r'https?://discord\.com/channels/(\d+)/(\d+)/(\d+)',
            r'https?://discordapp\.com/channels/(\d+)/(\d+)/(\d+)',
            r'https?://www\.discord\.com/channels/(\d+)/(\d+)/(\d+)',
            r'https?://www\.discordapp\.com/channels/(\d+)/(\d+)/(\d+)'
        ]
        
        for pattern in patterns:
            match = re.match(pattern, link)
            if match:
                try:
                    guild_id = int(match.group(1))
                    channel_id = int(match.group(2))
                    message_id = int(match.group(3))
                    return (guild_id, channel_id, message_id)
                except ValueError:
                    continue
        
        return None

    def _verify_template(self, content: str) -> dict:
        """Vérifie si le contenu respecte le template de mise à jour de fiche"""
        
        result = {
            'score': 0,
            'total_checks': 0,
            'sections_found': [],
            'sections_missing': [],
            'warnings': [],
            'suggestions': [],
            'details': {},
            'placeholders': []
        }
        
        # Éléments obligatoires à vérifier
        required_patterns = {
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
        
        # Vérifier les éléments obligatoires
        result['total_checks'] = len(required_patterns)
        
        for key, pattern in required_patterns.items():
            if re.search(pattern, content, re.IGNORECASE | re.MULTILINE):
                result['score'] += 1
                result['sections_found'].append(key)
                
                # Extraire les détails pour certains éléments
                match = re.search(pattern, content, re.IGNORECASE | re.MULTILINE)
                if match and match.groups():
                    result['details'][key] = match.group(1).strip()
            else:
                result['sections_missing'].append(key)
        
        # Analyser la structure et donner des conseils
        self._analyze_structure(content, result)
        
        return result

    def _analyze_structure(self, content: str, result: dict):
        """Analyse la structure et ajoute des suggestions"""
        
        lines = content.split('\n')
        
        # Vérifier les calculs XP
        xp_line = None
        for line in lines:
            if re.search(r'\*\*Solde XP\s*:\*\*', line, re.IGNORECASE):
                xp_line = line
                break
        
        if xp_line:
            # Chercher un pattern de calcul : X/Y + Z = W/Y
            if not re.search(r'\d+/\d+\s*\+\s*\d+\s*=\s*\d+/\d+', xp_line):
                if '[' in xp_line:
                    result['warnings'].append("XP non calculés - Des placeholders restent à remplir")
                else:
                    result['warnings'].append("Format de calcul XP non standard")
        
        # Vérifier les placeholders non remplis
        placeholders = re.findall(r'\[([A-Z_]+)\]', content)
        result['placeholders'] = list(set(placeholders))  # Supprimer les doublons
        
        if len(result['placeholders']) > 0:
            result['warnings'].append(f"{len(result['placeholders'])} placeholder(s) non rempli(s) : {', '.join(result['placeholders'][:5])}")
        
        # Vérifier la longueur
        char_count = len(content)
        if char_count > 2000:
            result['warnings'].append(f"Message long ({char_count} caractères) - Peut nécessiter plusieurs messages")
        elif char_count < 300:
            result['warnings'].append("Message très court - Vérifiez si toutes les sections sont présentes")

    def _generate_suggestions(self, original_content: str, verification_result: dict) -> dict:
        """Génère des suggestions d'amélioration et un template corrigé"""
        
        suggestions = {
            'corrections': [],
            'ameliorations': [],
            'corrected_template': None,
            'automatic_fixes': []
        }
        
        corrected_content = original_content
        
        # 1. CORRECTIONS AUTOMATIQUES DES SÉPARATEURS
        if 'separator_pj_start' in verification_result['sections_missing']:
            suggestions['automatic_fixes'].append("Ajout du séparateur de début PJ")
            # Trouver où insérer le séparateur (après Classe)
            if 'Classe' in corrected_content:
                corrected_content = re.sub(
                    r'(Classe\s*:\s*.+)',
                    r'\1\n\n** / =======================  PJ  ========================= \\ **',
                    corrected_content,
                    count=1
                )
        
        if 'separator_pj_end' in verification_result['sections_missing']:
            suggestions['automatic_fixes'].append("Ajout du séparateur de fin PJ")
            # Insérer avant le solde final
            if '*Solde' in corrected_content:
                corrected_content = re.sub(
                    r'(\*\*¤\s*Solde\s*:\*\*)',
                    r'** \\ =======================  PJ  ========================= / **\n\n\1',
                    corrected_content,
                    count=1
                )
        
        # 2. CORRECTIONS DES SECTIONS MANQUANTES
        missing_sections = verification_result['sections_missing']
        
        if 'quete' in missing_sections:
            suggestions['corrections'].append({
                'section': 'Quête',
                'correction': '**Quête :** [TITRE_QUETE] + [NOM_MJ] ⁠- [LIEN_MESSAGE_RECOMPENSES]',
                'position': 'Après les séparateurs PJ'
            })
        
        if 'solde_xp' in missing_sections:
            suggestions['corrections'].append({
                'section': 'Solde XP',
                'correction': '**Solde XP :** [XP_ACTUELS]/[XP_REQUIS] + [XP_OBTENUS] = [NOUVEAUX_XP]/[XP_REQUIS] -> 🆙 passage au niveau [NOUVEAU_NIVEAU]',
                'position': 'Après la section Quête'
            })
        
        if 'gain_niveau' in missing_sections:
            suggestions['corrections'].append({
                'section': 'Gain de niveau',
                'correction': '**Gain de niveau :**\nPV : [ANCIENS_PV] + [PV_OBTENUS] = [NOUVEAUX_PV]',
                'position': 'Après Solde XP'
            })
        
        if 'capacites' in missing_sections:
            suggestions['corrections'].append({
                'section': 'Capacités et sorts',
                'correction': '**¤ Capacités et sorts supplémentaires :**\nNouvelle(s) capacité(s) :\n- [CAPACITE_1]\n- [CAPACITE_2]\nNouveau(x) sort(s) :\n- [SORT_1]\n- [SORT_2]',
                'position': 'Après Gain de niveau'
            })
        
        # 3. AMÉLIORATIONS SUGGÉRÉES
        if verification_result['placeholders']:
            suggestions['ameliorations'].append({
                'type': 'Placeholders à remplir',
                'description': f"Remplacer les placeholders : {', '.join(verification_result['placeholders'][:10])}",
                'priority': 'Haute'
            })
        
        # Suggestions basées sur le contenu détecté
        if 'nom_pj' in verification_result['details']:
            nom_pj = verification_result['details']['nom_pj']
            if '[' in nom_pj:
                suggestions['ameliorations'].append({
                    'type': 'Nom du PJ',
                    'description': f"Remplacer '{nom_pj}' par le vrai nom du personnage",
                    'priority': 'Haute'
                })
        
        if 'classe' in verification_result['details']:
            classe = verification_result['details']['classe']
            if '[' in classe:
                suggestions['ameliorations'].append({
                    'type': 'Classe',
                    'description': f"Remplacer '{classe}' par la vraie classe du personnage",
                    'priority': 'Haute'
                })
        
        # 4. SUGGESTIONS POUR LES CALCULS
        if 'solde_xp' in verification_result['details']:
            xp_line = verification_result['details']['solde_xp']
            if '[' in xp_line:
                suggestions['ameliorations'].append({
                    'type': 'Calculs XP',
                    'description': "Compléter les calculs d'expérience avec les vrais chiffres",
                    'priority': 'Moyenne'
                })
        
        # 5. SUGGESTIONS DE FORMATAGE
        if len(original_content) > 1800:
            suggestions['ameliorations'].append({
                'type': 'Longueur du message',
                'description': "Considérer diviser en plusieurs messages pour Discord",
                'priority': 'Basse'
            })
        
        # 6. GÉNÉRER UN TEMPLATE PARTIELLEMENT CORRIGÉ
        if suggestions['automatic_fixes']:
            suggestions['corrected_template'] = self._apply_automatic_fixes(corrected_content, verification_result)
        
        return suggestions

    def _clean_template(self, content: str) -> str:
        """Nettoie et optimise le template même s'il est déjà correct"""
        
        cleaned = content.strip()
        
        # Normaliser les espaces multiples
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
        
        # Normaliser les séparateurs
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
        
        # Normaliser les sections Marchand si présentes
        cleaned = re.sub(
            r'\*\*\s*/\s*=+\s*Marchand\s*=+\s*\\\s*\*\*',
            '**/ ===================== Marchand ===================== \\ **',
            cleaned
        )
        cleaned = re.sub(
            r'\*\*\s*\\\s*=+\s*Marchand\s*=+\s*/\s*\*\*',
            '** \\ ==================== Marchand ====================== / **',
            cleaned
        )
        
        return cleaned

    def _apply_automatic_fixes(self, content: str, verification_result: dict) -> str:
        """Applique les corrections automatiques possibles"""
        
        corrected = content
        
        # Correction des séparateurs manquants
        if 'separator_pj_start' in verification_result['sections_missing']:
            if '** /' not in corrected and 'Classe' in corrected:
                corrected = re.sub(
                    r'(Classe\s*:\s*.+?)(\n|$)',
                    r'\1\n\n** / =======================  PJ  ========================= \\ **\n',
                    corrected,
                    count=1,
                    flags=re.MULTILINE
                )
        
        if 'separator_pj_end' in verification_result['sections_missing']:
            if '** \\' not in corrected and 'Solde' in corrected:
                corrected = re.sub(
                    r'(\*\*¤\s*Solde\s*:\*\*)',
                    r'** \\ =======================  PJ  ========================= / **\n\n\1',
                    corrected,
                    count=1
                )
        
        # Ajout des sections manquantes de base
        missing = verification_result['sections_missing']
        
        # Insérer les sections manquantes dans l'ordre logique
        if 'quete' in missing and '**Quête' not in corrected:
            if '** /' in corrected:
                corrected = re.sub(
                    r'(\*\* / =+ PJ =+ \\ \*\*\n)',
                    r'\1**Quête :** [TITRE_QUETE] + [NOM_MJ] ⁠- [LIEN_MESSAGE_RECOMPENSES]\n',
                    corrected,
                    count=1
                )
        
        if 'solde_xp' in missing and '**Solde XP' not in corrected:
            if '**Quête' in corrected:
                corrected = re.sub(
                    r'(\*\*Quête\s*:\*\*.*?\n)',
                    r'\1**Solde XP :** [XP_ACTUELS]/[XP_REQUIS] + [XP_OBTENUS] = [NOUVEAUX_XP]/[XP_REQUIS] -> 🆙 passage au niveau [NOUVEAU_NIVEAU]\n\n',
                    corrected,
                    count=1,
                    flags=re.DOTALL
                )
        
        return corrected

    def _create_verification_embed(self, message: discord.Message, result: dict, suggestions: dict = None) -> discord.Embed:
        """Crée l'embed avec les résultats de vérification et suggestions"""
        
        # Calculer le pourcentage de conformité
        score_percentage = (result['score'] / result['total_checks']) * 100 if result['total_checks'] > 0 else 0
        
        # Déterminer la couleur selon le score
        if score_percentage >= 90:
            color = 0x2ecc71  # Vert
            status_emoji = "✅"
            status_text = "Excellent"
        elif score_percentage >= 70:
            color = 0xf39c12  # Orange
            status_emoji = "⚠️"
            status_text = "Bon"
        elif score_percentage >= 50:
            color = 0xff9900  # Orange foncé
            status_emoji = "🔸"
            status_text = "Passable"
        else:
            color = 0xe74c3c  # Rouge
            status_emoji = "❌"
            status_text = "Insuffisant"
        
        embed = discord.Embed(
            title=f"{status_emoji} Vérification + Suggestions de MAJ",
            description=f"**Statut :** {status_text} ({score_percentage:.0f}%)",
            color=color
        )
        
        # Informations du message
        embed.add_field(
            name="📝 Message analysé",
            value=f"**Auteur :** {message.author.mention}\n**Canal :** {message.channel.mention}\n**Date :** {discord.utils.format_dt(message.created_at, 'R')}",
            inline=False
        )
        
        # Score de conformité
        embed.add_field(
            name="📊 Score de conformité",
            value=f"**{result['score']}/{result['total_checks']}** éléments obligatoires trouvés\n**{score_percentage:.1f}%** de conformité",
            inline=True
        )
        
        # Caractéristiques détectées
        if result['details'].get('nom_pj') or result['details'].get('classe'):
            char_info = []
            if result['details'].get('nom_pj'):
                char_info.append(f"**PJ :** {result['details']['nom_pj']}")
            if result['details'].get('classe'):
                char_info.append(f"**Classe :** {result['details']['classe']}")
            
            embed.add_field(
                name="🎭 Personnage détecté",
                value="\n".join(char_info),
                inline=True
            )
        
        # NOUVEAU : Corrections automatiques disponibles
        if suggestions and suggestions.get('automatic_fixes'):
            fixes_text = "\n".join([f"✅ {fix}" for fix in suggestions['automatic_fixes'][:3]])
            embed.add_field(
                name="🔧 Corrections automatiques appliquées",
                value=fixes_text,
                inline=False
            )
        
        # NOUVEAU : Suggestions de corrections
        if suggestions and suggestions.get('corrections'):
            corrections_text = []
            for correction in suggestions['corrections'][:3]:
                corrections_text.append(f"**{correction['section']}** - {correction['position']}")
            
            embed.add_field(
                name="🛠️ Sections à ajouter",
                value="\n".join(corrections_text),
                inline=False
            )
        
        # NOUVEAU : Améliorations suggérées
        if suggestions and suggestions.get('ameliorations'):
            ameliorations_text = []
            for amelioration in suggestions['ameliorations'][:3]:
                priority_emoji = {"Haute": "🔴", "Moyenne": "🟡", "Basse": "🟢"}.get(amelioration['priority'], "⚪")
                ameliorations_text.append(f"{priority_emoji} **{amelioration['type']}** : {amelioration['description']}")
            
            embed.add_field(
                name="💡 Améliorations suggérées",
                value="\n".join(ameliorations_text),
                inline=False
            )
        
        # Sections manquantes (si il y en a et pas de suggestions)
        if result['sections_missing'] and not suggestions:
            missing_labels = {
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
            
            missing_list = [missing_labels.get(key, key) for key in result['sections_missing'][:5]]
            if len(result['sections_missing']) > 5:
                missing_list.append(f"... et {len(result['sections_missing']) - 5} autres")
            
            embed.add_field(
                name="❌ Sections manquantes",
                value="\n".join([f"• {item}" for item in missing_list]),
                inline=False
            )
        
        # Avertissements
        if result['warnings']:
            embed.add_field(
                name="⚠️ Avertissements",
                value="\n".join([f"• {w}" for w in result['warnings'][:3]]),
                inline=False
            )
        
        # Conseils selon le score avec mention systématique du template
        if score_percentage < 70:
            embed.add_field(
                name="🎯 Actions recommandées",
                value="• **Consultez le template corrigé ci-dessous**\n• Utilisez `/maj-fiche` pour un nouveau template\n• Complétez les placeholders [EN_MAJUSCULES]\n• Vérifiez les calculs XP et PV",
                inline=False
            )
        else:
            embed.add_field(
                name="🎯 Prochaines étapes",
                value="• **Récupérez le template optimisé ci-dessous**\n• Vérifiez les derniers détails\n• Complétez les éventuels placeholders\n• Votre MAJ est presque prête !",
                inline=False
            )
        
        # Lien vers le message + guide d'utilisation
        embed.add_field(
            name="🔗 Actions",
            value=f"[📖 Voir le message original]({message.jump_url})\n📋 **Template amélioré envoyé ci-dessous**\n\n💡 **Astuce :** Clic droit sur un message → Copier le lien du message",
            inline=True
        )
        
        embed.set_footer(text=f"Vérification avec suggestions • Message ID: {message.id}")
        embed.timestamp = discord.utils.utcnow()
        
        return embed

    async def _send_corrected_template(self, interaction: discord.Interaction, template: str, suggestions: dict = None):
        """Envoie TOUJOURS le template (corrigé ou nettoyé) en follow-up"""
        
        # Déterminer le type de template
        has_corrections = suggestions and (suggestions.get('automatic_fixes') or suggestions.get('corrections'))
        is_perfect = not has_corrections and suggestions
        
        # Titre selon le type
        if has_corrections:
            title = "🔧 Template Corrigé et Amélioré"
            description = "Voici votre template avec toutes les corrections automatiques appliquées :"
            color = 0x2ecc71  # Vert
        elif is_perfect:
            title = "✅ Template Validé et Optimisé"
            description = "Votre template était déjà excellent ! Voici la version nettoyée et prête à utiliser :"
            color = 0x3498db  # Bleu
        else:
            title = "📋 Template Extrait et Nettoyé"
            description = "Voici votre template extrait du message, nettoyé et prêt à utiliser :"
            color = 0x9b59b6  # Violet
        
        # Diviser le template si trop long
        max_length = 1800  # Limite sécurisée pour laisser place aux autres éléments
        
        if len(template) <= max_length:
            # Template complet dans un seul message
            embed = discord.Embed(
                title=title,
                description=description,
                color=color
            )
            
            # Calculer les statistiques du template
            char_count = len(template)
            line_count = len(template.split('\n'))
            placeholder_count = len(re.findall(r'\[([A-Z_]+)\]', template))
            
            embed.add_field(
                name="📊 Statistiques du template",
                value=f"**Caractères :** {char_count}/2000 Discord\n**Lignes :** {line_count}\n**Placeholders à remplir :** {placeholder_count}",
                inline=True
            )
            
            # Afficher les corrections si il y en a
            if has_corrections and suggestions:
                corrections_applied = []
                if suggestions.get('automatic_fixes'):
                    corrections_applied.extend([f"✅ {fix}" for fix in suggestions['automatic_fixes'][:3]])
                
                if corrections_applied:
                    embed.add_field(
                        name="🔧 Corrections appliquées",
                        value="\n".join(corrections_applied),
                        inline=True
                    )
            
            # Instructions d'utilisation
            if placeholder_count > 0:
                embed.add_field(
                    name="📝 Prochaines étapes",
                    value=f"1. **Copiez** le template ci-dessous\n2. **Remplacez** les {placeholder_count} placeholders [EN_MAJUSCULES]\n3. **Complétez** les calculs XP et PV\n4. **Vérifiez** les informations personnage",
                    inline=False
                )
            else:
                embed.add_field(
                    name="🎯 Template prêt !",
                    value="✅ Aucun placeholder à remplir\n✅ Copiez et utilisez directement\n✅ Vérifiez une dernière fois les calculs",
                    inline=False
                )
            
            # Le template lui-même
            embed.add_field(
                name="📋 Votre template final",
                value=f"```\n{template}\n```",
                inline=False
            )
            
            # Conseils selon la longueur
            if char_count > 1900:
                embed.add_field(
                    name="⚠️ Attention",
                    value="Template proche de la limite Discord (2000 caractères). Considérez raccourcir certaines sections si nécessaire.",
                    inline=False
                )
            
            await interaction.followup.send(embed=embed, ephemeral=True)
        
        else:
            # Template trop long - diviser en parties
            embed_intro = discord.Embed(
                title=f"{title} - Multi-parties",
                description=f"{description}\n\n⚠️ **Template long** - Divisé en plusieurs messages pour Discord",
                color=color
            )
            
            # Stats dans l'intro
            char_count = len(template)
            line_count = len(template.split('\n'))
            placeholder_count = len(re.findall(r'\[([A-Z_]+)\]', template))
            
            embed_intro.add_field(
                name="📊 Statistiques",
                value=f"**Total :** {char_count} caractères\n**Lignes :** {line_count}\n**Placeholders :** {placeholder_count}",
                inline=True
            )
            
            if has_corrections and suggestions and suggestions.get('automatic_fixes'):
                embed_intro.add_field(
                    name="🔧 Corrections",
                    value="\n".join([f"✅ {fix}" for fix in suggestions['automatic_fixes'][:3]]),
                    inline=True
                )
            
            embed_intro.add_field(
                name="📝 Instructions",
                value="1. **Copiez** chaque partie dans l'ordre\n2. **Assemblez** en un seul message\n3. **Complétez** les placeholders\n4. **Vérifiez** les calculs",
                inline=False
            )
            
            await interaction.followup.send(embed=embed_intro, ephemeral=True)
            
            # Diviser et envoyer les parties
            parts = self._split_template_for_discord(template)
            
            for i, part in enumerate(parts, 1):
                part_embed = discord.Embed(
                    title=f"📋 Template - Partie {i}/{len(parts)}",
                    description=f"```\n{part}\n```",
                    color=color
                )
                
                part_embed.add_field(
                    name="📏 Cette partie",
                    value=f"**Caractères :** {len(part)}\n**Partie :** {i} sur {len(parts)}",
                    inline=True
                )
                
                if i == 1:
                    part_embed.add_field(
                        name="💡 Conseil",
                        value="Copiez chaque partie et assemblez-les dans l'ordre",
                        inline=True
                    )
                elif i == len(parts):
                    part_embed.add_field(
                        name="✅ Terminé",
                        value=f"Template complet reconstitué !\n**Total final :** {char_count} caractères",
                        inline=True
                    )
                
                await interaction.followup.send(embed=part_embed, ephemeral=True)

        return suggestions

    def _split_template_for_discord(self, template: str) -> list:
        """Divise le template pour respecter les limites Discord"""
        max_length = 1900
        parts = []
        
        if len(template) <= max_length:
            return [template]
        
        lines = template.split('\n')
        current_part = ""
        
        for line in lines:
            if len(current_part + line + '\n') > max_length:
                if current_part:
                    parts.append(current_part.rstrip())
                current_part = line + '\n'
            else:
                current_part += line + '\n'
        
        if current_part:
            parts.append(current_part.rstrip())
        
        return parts