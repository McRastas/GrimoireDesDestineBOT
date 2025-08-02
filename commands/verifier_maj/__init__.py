# enhanced_verifier_maj_command.py
"""
Version améliorée de la commande verifier-maj qui vérifie automatiquement
les récompenses déclarées contre les messages de récompense Discord.
Réponse sous forme d'embed Discord uniquement.
"""

import discord
from discord import app_commands
import re
import logging
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from ..base import BaseCommand

logger = logging.getLogger(__name__)


@dataclass
class RewardData:
    """Structure pour stocker les récompenses d'un joueur."""
    xp: int = 0
    po: int = 0
    objects: List[str] = None
    consumed_objects: List[str] = None
    
    def __post_init__(self):
        if self.objects is None:
            self.objects = []
        if self.consumed_objects is None:
            self.consumed_objects = []


@dataclass
class QuestVerification:
    """Résultat de vérification d'une quête."""
    title: str
    link: str
    declared_rewards: RewardData
    actual_rewards: RewardData
    player_found: bool = False
    errors: List[str] = None
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []


class RewardParser:
    """Parse les récompenses depuis les messages Discord."""
    
    def __init__(self):
        # Patterns pour identifier les joueurs et leurs récompenses
        self.player_patterns = [
            r'@(\w+)\s*\[([\w/]+)\]\s*([^,]*?),\s*([^@]+?)(?=@|$)',  # @pseudo [persos] perso, récompenses
            r'@(\w+)\[([^\]]+)\]\s*([^,]*?),\s*([^@]+?)(?=@|$)',     # @pseudo[persos] perso, récompenses
            r'@(\w+)([A-Z][a-z]+),\s*([^@]+?)(?=@|$)',               # @pseudoNomPerso, récompenses (pour McRastasTharaxus)
        ]
        
        # Pattern pour XP global au début du message
        self.global_xp_pattern = re.compile(r'^[^@]*[+](\d+)\s*xp', re.IGNORECASE)
        
        # Patterns pour les récompenses spécifiques
        self.emerald_pattern = re.compile(r'(\d+)\s*émeraudes?\s*d\'une\s*valeur\s*de\s*(\d+)PO', re.IGNORECASE)
        self.ruby_pattern = re.compile(r'(\d+)\s*rubis\s*d\'une\s*valeur\s*de\s*(\d+)PO', re.IGNORECASE)
        self.object_pattern = re.compile(r'([^,]+(?:engrenage|fruit|potion|épée|armure|anneau|bague|ornement)[^,]*)', re.IGNORECASE)
        self.consumed_pattern = re.compile(r'-1?\s*([^,]+(?:fruit|potion)[^,]*)', re.IGNORECASE)
    
    def extract_player_rewards(self, message_content: str, target_player: str) -> RewardData:
        """Extrait les récompenses d'un joueur spécifique depuis un message."""
        rewards = RewardData()
        
        # 1. Extraire l'XP global (donné à tous les joueurs)
        global_xp_match = self.global_xp_pattern.search(message_content)
        if global_xp_match:
            rewards.xp = int(global_xp_match.group(1))
        
        # 2. Chercher les récompenses spécifiques du joueur
        for pattern in self.player_patterns:
            matches = re.finditer(pattern, message_content, re.IGNORECASE)
            
            for match in matches:
                groups = match.groups()
                
                if len(groups) == 4:  # Format: @pseudo [persos] perso, récompenses
                    player_name = groups[0].lower()
                    characters = groups[1]
                    played_char = groups[2]
                    reward_text = groups[3]
                elif len(groups) == 3:  # Format: @pseudoPerso, récompenses
                    combined = groups[0] + groups[1]  # McRastas + Tharaxus
                    player_name = groups[0].lower()
                    played_char = groups[1]
                    reward_text = groups[2]
                    characters = played_char
                else:
                    continue
                
                # Vérifier si c'est le bon joueur
                target_lower = target_player.lower()
                if (target_lower in player_name or 
                    player_name in target_lower or
                    target_lower in characters.lower() or
                    target_lower in played_char.lower()):
                    
                    # Extraire PO depuis les émeraudes/rubis
                    po_total = 0
                    
                    # Émeraudes
                    emerald_matches = self.emerald_pattern.findall(reward_text)
                    for count, value in emerald_matches:
                        po_total += int(count) * int(value)
                    
                    # Rubis
                    ruby_matches = self.ruby_pattern.findall(reward_text)
                    for count, value in ruby_matches:
                        po_total += int(count) * int(value)
                    
                    rewards.po = po_total
                    
                    # Extraire objets obtenus
                    object_matches = self.object_pattern.findall(reward_text)
                    rewards.objects = [obj.strip() for obj in object_matches if not obj.strip().startswith('-')]
                    
                    # Extraire objets consommés
                    consumed_matches = self.consumed_pattern.findall(reward_text)
                    rewards.consumed_objects = [obj.strip() for obj in consumed_matches]
                    
                    break
        
        return rewards


class FicheParser:
    """Parse les mises à jour de fiche pour extraire les informations."""
    
    def __init__(self):
        # Patterns pour extraire les informations de la fiche
        self.name_pattern = re.compile(r'Nom du PJ\s*:\s*(.+?)(?:\n|$)', re.IGNORECASE)
        self.class_pattern = re.compile(r'Classe\s*:\s*(.+?)(?:\n|$)', re.IGNORECASE)
        
        # Pattern pour les quêtes avec liens
        self.quest_pattern = re.compile(
            r'-\s*(.+?)\s*-\s*.*?\s*-\s*(https://discord\.com/channels/\d+/\d+/\d+)[^,]*,?\s*([^-\n]*)',
            re.IGNORECASE | re.MULTILINE
        )
        
        # Patterns pour les totaux déclarés
        self.total_xp_pattern = re.compile(r'Solde XP\s*:.*?[+](\d+)XP', re.IGNORECASE | re.DOTALL)
        self.total_po_pattern = re.compile(r'PO\s+Lootées\s*:\s*[+](\d+)\s*PO', re.IGNORECASE)
        self.total_objects_pattern = re.compile(r'Objet\s+Lootées?\s*:\s*(.+?)(?:\n|Don)', re.IGNORECASE)
    
    def parse_fiche(self, content: str) -> Dict:
        """Parse une mise à jour de fiche complète."""
        result = {
            'nom_pj': None,
            'classe': None,
            'quests': [],
            'total_declared': RewardData(),
            'errors': []
        }
        
        # Extraire nom du PJ
        name_match = self.name_pattern.search(content)
        if name_match:
            result['nom_pj'] = name_match.group(1).strip()
        else:
            result['errors'].append("Nom du PJ non trouvé")
        
        # Extraire classe
        class_match = self.class_pattern.search(content)
        if class_match:
            result['classe'] = class_match.group(1).strip()
        
        # Extraire les quêtes avec leurs liens
        quest_matches = self.quest_pattern.finditer(content)
        for match in quest_matches:
            quest_title = match.group(1).strip()
            quest_link = match.group(2).strip()
            quest_rewards_text = match.group(3).strip()
            
            # Parser les récompenses déclarées pour cette quête
            declared_rewards = RewardData()
            
            # XP de la quête
            xp_matches = re.findall(r'[+](\d+)\s*XP', quest_rewards_text, re.IGNORECASE)
            declared_rewards.xp = sum(int(x) for x in xp_matches)
            
            result['quests'].append({
                'title': quest_title,
                'link': quest_link,
                'declared_rewards': declared_rewards,
                'raw_text': quest_rewards_text
            })
        
        # Extraire les totaux déclarés
        total_xp_match = self.total_xp_pattern.search(content)
        if total_xp_match:
            result['total_declared'].xp = int(total_xp_match.group(1))
        
        total_po_match = self.total_po_pattern.search(content)
        if total_po_match:
            result['total_declared'].po = int(total_po_match.group(1))
        
        total_objects_match = self.total_objects_pattern.search(content)
        if total_objects_match:
            objects_text = total_objects_match.group(1).strip()
            # Parse les objets (séparer objets obtenus et consommés)
            objects = []
            consumed = []
            
            items = [item.strip() for item in objects_text.split(',')]
            for item in items:
                if item.startswith('-'):
                    consumed.append(item[1:].strip())
                else:
                    objects.append(item)
            
            result['total_declared'].objects = objects
            result['total_declared'].consumed_objects = consumed
        
        return result


class VerifierMajCommand(BaseCommand):
    """
    Version améliorée de verifier-maj qui vérifie automatiquement
    les récompenses déclarées contre les messages Discord.
    """
    
    def __init__(self, bot):
        super().__init__(bot)
        self.fiche_parser = FicheParser()
        self.reward_parser = RewardParser()
    
    @property
    def name(self) -> str:
        return "verifier-maj"
    
    @property
    def description(self) -> str:
        return "Vérifie une mise à jour de fiche en comparant avec les messages de récompense Discord"
    
    def register(self, tree: app_commands.CommandTree):
        """Enregistrement de la commande."""
        
        @tree.command(name=self.name, description=self.description)
        @app_commands.describe(
            lien_message="Lien vers la mise à jour de fiche à vérifier"
        )
        async def verifier_maj_command(
            interaction: discord.Interaction,
            lien_message: str
        ):
            await self.callback(interaction, lien_message)
    
    async def callback(
        self,
        interaction: discord.Interaction,
        lien_message: str
    ):
        """Fonction principale de vérification."""
        
        try:
            # Différer la réponse pour éviter les timeouts
            await interaction.response.defer(ephemeral=True)
            
            # 1. Récupérer le message de la fiche
            fiche_message = await self.get_message_from_link(lien_message)
            if not fiche_message:
                embed = discord.Embed(
                    title="❌ Erreur",
                    description="Impossible de récupérer le message de la fiche.\nVérifiez que le lien est correct et que j'ai accès au canal.",
                    color=0xff0000
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            
            # 2. Parser la fiche
            fiche_data = self.fiche_parser.parse_fiche(fiche_message.content)
            
            if not fiche_data['nom_pj']:
                embed = discord.Embed(
                    title="❌ Erreur de format",
                    description="Ce message ne semble pas être une mise à jour de fiche valide.\nJe n'ai pas pu trouver le nom du PJ.",
                    color=0xff0000
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            
            # 3. Vérifier chaque quête
            verifications = []
            for quest in fiche_data['quests']:
                verification = await self.verify_quest_rewards(
                    quest, fiche_data['nom_pj']
                )
                verifications.append(verification)
            
            # 4. Créer l'embed de résultat
            embed = await self.create_verification_embed(fiche_data, verifications)
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Erreur dans verifier-maj: {e}", exc_info=True)
            embed = discord.Embed(
                title="❌ Erreur inattendue",
                description=f"Une erreur s'est produite: {str(e)}\nContactez un administrateur si le problème persiste.",
                color=0xff0000
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
    
    async def verify_quest_rewards(self, quest: dict, player_name: str) -> QuestVerification:
        """Vérifie les récompenses d'une quête spécifique."""
        
        verification = QuestVerification(
            title=quest['title'],
            link=quest['link'],
            declared_rewards=quest['declared_rewards'],
            actual_rewards=RewardData()
        )
        
        # Récupérer le message de récompense
        reward_message = await self.get_message_from_link(quest['link'])
        
        if not reward_message:
            verification.errors.append("Message de récompense inaccessible")
            return verification
        
        # Extraire les récompenses du message
        verification.actual_rewards = self.reward_parser.extract_player_rewards(
            reward_message.content, player_name
        )
        
        # Vérifier si le joueur est trouvé
        verification.player_found = (
            verification.actual_rewards.xp > 0 or 
            verification.actual_rewards.po > 0 or 
            len(verification.actual_rewards.objects) > 0
        )
        
        if not verification.player_found:
            verification.warnings.append("Joueur non trouvé dans le message de récompense")
        
        # Comparer les récompenses
        if verification.declared_rewards.xp != verification.actual_rewards.xp:
            verification.errors.append(
                f"XP: déclaré {verification.declared_rewards.xp}, réel {verification.actual_rewards.xp}"
            )
        
        if verification.declared_rewards.po != verification.actual_rewards.po:
            verification.errors.append(
                f"PO: déclaré {verification.declared_rewards.po}, réel {verification.actual_rewards.po}"
            )
        
        return verification
    
    async def get_message_from_link(self, link: str) -> Optional[discord.Message]:
        """Récupère un message Discord à partir d'un lien."""
        # Parser le lien
        match = re.search(r'https://discord\.com/channels/(\d+)/(\d+)/(\d+)', link)
        if not match:
            return None
        
        guild_id, channel_id, message_id = map(int, match.groups())
        
        try:
            guild = self.bot.get_guild(guild_id)
            if not guild:
                return None
            
            channel = guild.get_channel(channel_id)
            if not channel:
                return None
            
            message = await channel.fetch_message(message_id)
            return message
            
        except Exception as e:
            logger.error(f"Erreur récupération message: {e}")
            return None
    
    async def create_verification_embed(
        self,
        fiche_data: dict,
        verifications: List[QuestVerification]
    ) -> discord.Embed:
        """Crée l'embed de résultat de vérification."""
        
        # Calculer les statistiques
        total_errors = sum(len(v.errors) for v in verifications)
        total_warnings = sum(len(v.warnings) for v in verifications)
        total_quests = len(verifications)
        
        # Déterminer la couleur
        if total_errors == 0:
            color = 0x00ff00  # Vert
            status_emoji = "✅"
            status_text = "Tout est correct !"
        elif total_errors <= 2:
            color = 0xff6600  # Orange
            status_emoji = "⚠️"
            status_text = f"{total_errors} erreur(s) trouvée(s)"
        else:
            color = 0xff0000  # Rouge
            status_emoji = "❌"
            status_text = f"{total_errors} erreur(s) trouvée(s)"
        
        # Créer l'embed principal
        embed = discord.Embed(
            title=f"{status_emoji} Vérification de fiche D&D",
            description=f"**{fiche_data['nom_pj']}** - {fiche_data.get('classe', 'Classe non spécifiée')}",
            color=color
        )
        
        # Résumé
        summary_text = f"{status_text}\n"
        summary_text += f"📊 **{total_quests}** quête(s) vérifiée(s)\n"
        if total_warnings > 0:
            summary_text += f"⚠️ **{total_warnings}** avertissement(s)"
        
        embed.add_field(
            name="📋 Résumé",
            value=summary_text,
            inline=False
        )
        
        # Détails par quête (limité à 3 quêtes pour éviter de dépasser les limites Discord)
        for i, verification in enumerate(verifications[:3], 1):
            quest_emoji = "✅" if not verification.errors else "❌"
            
            # Titre de la quête (tronqué)
            quest_title = verification.title[:30] + "..." if len(verification.title) > 30 else verification.title
            
            # Détails des récompenses
            field_value = f"{quest_emoji} **XP**: {verification.declared_rewards.xp}"
            if verification.actual_rewards.xp != verification.declared_rewards.xp:
                field_value += f" → {verification.actual_rewards.xp}"
            
            field_value += f"\n**PO**: {verification.declared_rewards.po}"
            if verification.actual_rewards.po != verification.declared_rewards.po:
                field_value += f" → {verification.actual_rewards.po}"
            
            # Erreurs (limitées)
            if verification.errors:
                field_value += f"\n🔴 {verification.errors[0]}"
                if len(verification.errors) > 1:
                    field_value += f"\n+{len(verification.errors)-1} autres erreurs"
            
            # Avertissements
            if verification.warnings:
                field_value += f"\n🟡 {verification.warnings[0][:50]}"
            
            embed.add_field(
                name=f"🎯 {quest_title}",
                value=field_value,
                inline=True
            )
        
        # Si plus de 3 quêtes, ajouter une note
        if len(verifications) > 3:
            embed.add_field(
                name="📝 Note",
                value=f"Seules les 3 premières quêtes sont affichées. Total: {len(verifications)} quêtes.",
                inline=False
            )
        
        # Footer avec timestamp
        embed.set_footer(
            text="Vérification automatique • Bot Faerûn",
            icon_url="https://cdn.discordapp.com/emojis/940620090687827968.png"
        )
        embed.timestamp = discord.utils.utcnow()
        
        return embed