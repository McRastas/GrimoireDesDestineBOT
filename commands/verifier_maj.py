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
        """Enregistrement avec paramètre d'ID de message"""

        @tree.command(name=self.name, description=self.description)
        @app_commands.describe(
            message_id="ID du message à vérifier",
            canal="Canal où se trouve le message (optionnel, par défaut le canal actuel)",
            proposer_corrections="Proposer des corrections automatiques"
        )
        @app_commands.choices(proposer_corrections=[
            app_commands.Choice(name="Oui, proposer des ajustements", value="oui"),
            app_commands.Choice(name="Non, vérification seulement", value="non")
        ])
        async def verifier_maj_command(
            interaction: discord.Interaction,
            message_id: str,
            canal: discord.TextChannel = None,
            proposer_corrections: str = "oui"
        ):
            await self.callback(interaction, message_id, canal, proposer_corrections == "oui")

    async def callback(
        self, 
        interaction: discord.Interaction, 
        message_id: str, 
        canal: discord.TextChannel = None,
        proposer_corrections: bool = True
    ):
        try:
            # Utiliser le canal spécifié ou le canal actuel
            target_channel = canal or interaction.channel
            
            # Récupérer le message
            try:
                message_id_int = int(message_id)
                message = await target_channel.fetch_message(message_id_int)
            except ValueError:
                await interaction.response.send_message(
                    "❌ L'ID du message doit être un nombre valide.", 
                    ephemeral=True
                )
                return
            except discord.NotFound:
                await interaction.response.send_message(
                    f"❌ Message avec l'ID `{message_id}` introuvable dans {target_channel.mention}.", 
                    ephemeral=True
                )
                return
            except discord.Forbidden:
                await interaction.response.send_message(
                    f"❌ Pas d'autorisation pour lire les messages dans {target_channel.mention}.", 
                    ephemeral=True
                )
                return

            # Analyser le contenu du message
            content = message.content
            if not content.strip():
                await interaction.response.send_message(
                    "❌ Le message est vide ou ne contient que des embeds.", 
                    ephemeral=True
                )
                return

            # Effectuer la vérification
            verification_result = self._verify_template(content)
            
            # Générer des suggestions si demandé
            suggestions = None
            if proposer_corrections and verification_result['score'] < verification_result['total_checks']:
                suggestions = self._generate_suggestions(content, verification_result)
            
            # Créer l'embed de résultat
            embed = self._create_verification_embed(message, verification_result, suggestions)
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
            # Envoyer le template corrigé si des corrections sont disponibles
            if suggestions and suggestions.get('corrected_template'):
                await self._send_corrected_template(interaction, suggestions['corrected_template'])

        except Exception as e:
            await interaction.response.send_message(
                f"❌ Erreur lors de la vérification : {str(e)}", 
                ephemeral=True
            )

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
        
        # Conseils selon le score
        if score_percentage < 70:
            embed.add_field(
                name="🎯 Actions recommandées",
                value="• Consultez le template corrigé ci-dessous\n• Utilisez `/maj-fiche` pour un nouveau template\n• Complétez les placeholders [EN_MAJUSCULES]\n• Vérifiez les calculs XP et PV",
                inline=False
            )
        
        # Lien vers le message
        embed.add_field(
            name="🔗 Actions",
            value=f"[📖 Voir le message original]({message.jump_url})",
            inline=True
        )
        
        embed.set_footer(text=f"Vérification avec suggestions • Message ID: {message.id}")
        embed.timestamp = discord.utils.utcnow()
        
        return embed

    async def _send_corrected_template(self, interaction: discord.Interaction, corrected_template: str):
        """Envoie le template corrigé en follow-up"""
        
        # Diviser le template si trop long
        max_length = 1900
        
        if len(corrected_template) <= max_length:
            # Template complet
            embed = discord.Embed(
                title="🔧 Template Corrigé",
                description=f"Voici votre template avec les corrections automatiques appliquées :",
                color=0x2ecc71
            )
            
            embed.add_field(
                name="📋 Template amélioré",
                value=f"```\n{corrected_template}\n```",
                inline=False
            )
            
            embed.add_field(
                name="✅ Corrections appliquées",
                value="• Séparateurs PJ ajoutés\n• Sections manquantes insérées\n• Structure améliorée",
                inline=False
            )
            
            embed.add_field(
                name="📝 Prochaines étapes",
                value="1. Copiez le template corrigé\n2. Remplacez les placeholders [EN_MAJUSCULES]\n3. Complétez les calculs XP et PV\n4. Vérifiez les informations personnage",
                inline=False
            )
            
            await interaction.followup.send(embed=embed, ephemeral=True)
        
        else:
            # Template trop long - diviser
            embed = discord.Embed(
                title="🔧 Template Corrigé (Partie 1)",
                description="Template trop long - divisé en plusieurs parties",
                color=0x2ecc71
            )
            
            parts = self._split_template_for_discord(corrected_template)
            
            for i, part in enumerate(parts, 1):
                part_embed = discord.Embed(
                    title=f"🔧 Template Corrigé - Partie {i}/{len(parts)}",
                    description=f"```\n{part}\n```",
                    color=0x2ecc71
                )
                
                if i == len(parts):  # Dernière partie
                    part_embed.add_field(
                        name="✅ Corrections appliquées",
                        value="• Séparateurs PJ ajoutés\n• Sections manquantes insérées\n• Structure améliorée",
                        inline=False
                    )
                
                await interaction.followup.send(embed=part_embed, ephemeral=True)

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