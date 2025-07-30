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
        return "Vérifie si un message respecte le template de mise à jour de fiche D&D"

    def register(self, tree: app_commands.CommandTree):
        """Enregistrement avec paramètre d'ID de message"""

        @tree.command(name=self.name, description=self.description)
        @app_commands.describe(
            message_id="ID du message à vérifier",
            canal="Canal où se trouve le message (optionnel, par défaut le canal actuel)"
        )
        async def verifier_maj_command(
            interaction: discord.Interaction,
            message_id: str,
            canal: discord.TextChannel = None
        ):
            await self.callback(interaction, message_id, canal)

    async def callback(
        self, 
        interaction: discord.Interaction, 
        message_id: str, 
        canal: discord.TextChannel = None
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
            
            # Créer l'embed de résultat
            embed = self._create_verification_embed(message, verification_result)
            
            await interaction.response.send_message(embed=embed, ephemeral=True)

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
            'details': {}
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
        
        # Éléments optionnels
        optional_patterns = {
            'separator_marchand_start': r'\*\*\s*/\s*=+\s*Marchand\s*=+\s*\\\s*\*\*',
            'separator_marchand_end': r'\*\*\s*\\\s*=+\s*Marchand\s*=+\s*/\s*\*\*',
            'inventaire': r'\*\*¤\s*Inventaire\*\*'
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
        
        # Vérifier les éléments optionnels
        for key, pattern in optional_patterns.items():
            if re.search(pattern, content, re.IGNORECASE | re.MULTILINE):
                result['sections_found'].append(key)
        
        # Analyser la structure et donner des conseils
        self._analyze_structure(content, result)
        
        return result

    def _analyze_structure(self, content: str, result: dict):
        """Analyse la structure et ajoute des suggestions"""
        
        lines = content.split('\n')
        
        # Vérifier l'ordre des sections
        section_order = []
        for i, line in enumerate(lines):
            if 'Nom du PJ' in line:
                section_order.append(('nom_pj', i))
            elif 'Classe' in line:
                section_order.append(('classe', i))
            elif re.search(r'\*\*Quête\s*:\*\*', line, re.IGNORECASE):
                section_order.append(('quete', i))
            elif re.search(r'\*\*Solde XP\s*:\*\*', line, re.IGNORECASE):
                section_order.append(('solde_xp', i))
            elif re.search(r'\*\*Gain de niveau\s*:\*\*', line, re.IGNORECASE):
                section_order.append(('gain_niveau', i))
        
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
        placeholder_count = len(re.findall(r'\[([A-Z_]+)\]', content))
        if placeholder_count > 0:
            result['warnings'].append(f"{placeholder_count} placeholder(s) non rempli(s) trouvé(s)")
        
        # Suggestions selon les sections manquantes
        if 'separator_marchand_start' in result['sections_found']:
            result['suggestions'].append("✅ Section Marchand détectée")
        
        if 'inventaire' in result['sections_found']:
            result['suggestions'].append("✅ Section Inventaire détectée")
        
        # Vérifier la longueur
        char_count = len(content)
        if char_count > 2000:
            result['warnings'].append(f"Message long ({char_count} caractères) - Peut nécessiter plusieurs messages")
        elif char_count < 300:
            result['warnings'].append("Message très court - Vérifiez si toutes les sections sont présentes")

    def _create_verification_embed(self, message: discord.Message, result: dict) -> discord.Embed:
        """Crée l'embed avec les résultats de vérification"""
        
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
            title=f"{status_emoji} Vérification du Template de MAJ",
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
        
        # Sections manquantes (si il y en a)
        if result['sections_missing']:
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
        
        # Suggestions
        if result['suggestions']:
            embed.add_field(
                name="💡 Suggestions",
                value="\n".join([f"• {s}" for s in result['suggestions'][:3]]),
                inline=False
            )
        
        # Conseils selon le score
        if score_percentage < 70:
            embed.add_field(
                name="🛠️ Recommandations",
                value="• Utilisez `/maj-fiche` pour générer un template correct\n• Vérifiez que toutes les sections obligatoires sont présentes\n• Respectez le format avec les séparateurs `** / === PJ === \\ **`",
                inline=False
            )
        
        # Lien vers le message
        embed.add_field(
            name="🔗 Actions",
            value=f"[📖 Voir le message original]({message.jump_url})",
            inline=True
        )
        
        embed.set_footer(text=f"Vérification effectuée • Message ID: {message.id}")
        embed.timestamp = discord.utils.utcnow()
        
        return embed