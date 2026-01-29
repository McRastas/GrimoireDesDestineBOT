"""
Commande Top MJ - Répertorie les MJ les plus actifs
Compte les posts dans le canal récompenses avec au moins 2 mentions
"""

import discord
from discord import app_commands
from collections import defaultdict
from typing import Optional
from datetime import datetime, timedelta, timezone
from .base import BaseCommand


class TopMjCommand(BaseCommand):
    """Commande pour afficher le top des MJ les plus actifs."""

    @property
    def name(self) -> str:
        return "top-mj"

    @property
    def description(self) -> str:
        return "Affiche le top des MJ les plus actifs sur le serveur"
    
    def register(self, tree: app_commands.CommandTree):
        """Enregistre la commande avec ses paramètres."""
        @app_commands.command(name=self.name, description=self.description)
        @app_commands.describe(
            nombre="Nombre de MJ à afficher (entre 5 et 50, défaut: 10)",
            periode="Filtrer sur les 30 derniers jours uniquement (défaut: Non)"
        )
        async def top_mj_cmd(
            interaction: discord.Interaction, 
            nombre: Optional[int] = 10,
            periode: Optional[bool] = False
        ):
            await self.callback(interaction, nombre, periode)
        
        tree.add_command(top_mj_cmd)

    async def callback(
        self, 
        interaction: discord.Interaction,
        nombre: int = 10,
        periode: bool = False
    ):
        """Analyse les posts dans le canal récompenses et affiche le classement des MJ."""
        
        # Validation du nombre (entre 5 et 50)
        nombre_original = nombre
        if nombre < 5:
            nombre = 5
        elif nombre > 50:
            nombre = 50
        
        # Réponse discrète (ephemeral) - visible uniquement par l'utilisateur
        await interaction.response.defer(ephemeral=True)
        
        # Message d'avertissement si le nombre a été ajusté
        adjusted_warning = ""
        if nombre_original != nombre:
            adjusted_warning = f"⚠️ Nombre ajusté de {nombre_original} à {nombre} (limites: 5-50)\n\n"

        try:
            # Chercher le canal récompenses (plusieurs variantes possibles)
            recompense_channel = None
            for channel in interaction.guild.text_channels:
                if channel.name.lower() in ['recompenses', 'récompenses', 'recompense']:
                    recompense_channel = channel
                    break

            if not recompense_channel:
                await interaction.followup.send(
                    "❌ Le canal **récompenses** n'a pas été trouvé sur ce serveur.\n"
                    "Assurez-vous qu'un canal avec ce nom existe.",
                    ephemeral=True
                )
                return

            # Calculer la période
            periode_text = "30 derniers jours" if periode else "tout l'historique"
            date_limite = None
            if periode:
                date_limite = datetime.now(timezone.utc) - timedelta(days=30)

            # Message de progression (ephemeral)
            await interaction.followup.send(
                f"{adjusted_warning}📊 Analyse des messages en cours...\n"
                f"Canal : #{recompense_channel.name}\n"
                f"Période : {periode_text}",
                ephemeral=True
            )

            # Collecter tous les messages
            all_messages = []
            if periode and date_limite:
                # Filtrer sur les 30 derniers jours
                async for message in recompense_channel.history(limit=None, after=date_limite):
                    all_messages.append(message)
                    
                    # Limite de sécurité (10000 messages max)
                    if len(all_messages) >= 10000:
                        break
            else:
                # Tout l'historique
                async for message in recompense_channel.history(limit=None):
                    all_messages.append(message)
                    
                    # Limite de sécurité (10000 messages max)
                    if len(all_messages) >= 10000:
                        break

            # Compter les posts valides par auteur
            mj_stats = defaultdict(int)

            for message in all_messages:
                # Vérifier si le message a au moins 2 mentions
                if len(message.mentions) >= 2:
                    mj_stats[message.author.id] += 1

            # Trier et prendre le top X (selon l'argument)
            sorted_mj = sorted(
                mj_stats.items(),
                key=lambda x: x[1],
                reverse=True
            )[:nombre]

            if not sorted_mj:
                await interaction.edit_original_response(
                    content=f"📊 Aucun MJ trouvé avec des posts contenant au moins 2 mentions sur {periode_text}."
                )
                return

            # Créer l'embed (sera ephemeral automatiquement)
            embed = discord.Embed(
                title=f"🏆 Top {nombre} des MJ les plus actifs",
                description=f"Classement basé sur les posts dans #{recompense_channel.name} avec au moins 2 mentions\n📅 Période : {periode_text}",
                color=discord.Color.gold(),
                timestamp=discord.utils.utcnow()
            )

            # Médailles pour le podium
            medals = ['🥇', '🥈', '🥉']
            
            # Construire le classement
            ranking_text = ""
            for i, (user_id, count) in enumerate(sorted_mj):
                try:
                    user = await self.bot.fetch_user(user_id)
                    user_name = f"{user.display_name}"
                except:
                    user_name = f"Utilisateur inconnu"
                
                # Icône pour le classement
                if i < 3:
                    icon = medals[i]
                else:
                    icon = f"**{i + 1}.**"
                
                sessions_text = "session" if count == 1 else "sessions"
                ranking_text += f"{icon} {user_name} - **{count}** {sessions_text}\n"

            embed.add_field(
                name="📊 Classement",
                value=ranking_text,
                inline=False
            )

            # Statistiques supplémentaires
            total_sessions = sum(count for _, count in sorted_mj)
            total_mj = len(mj_stats)
            
            stats_text = (
                f"**Total sessions (top {nombre}) :** {total_sessions}\n"
                f"**Messages analysés :** {len(all_messages)}\n"
                f"**MJ actifs (total) :** {total_mj}"
            )
            
            embed.add_field(
                name="📈 Statistiques",
                value=stats_text,
                inline=False
            )

            embed.set_footer(
                text=f"Demandé par {interaction.user.display_name} • Visible uniquement par vous"
            )

            # Éditer le message initial (reste ephemeral)
            await interaction.edit_original_response(
                content=None,
                embed=embed
            )

        except discord.Forbidden:
            await interaction.followup.send(
                "❌ Je n'ai pas la permission de lire l'historique du canal récompenses.\n"
                "Vérifiez que le bot a bien la permission `Lire l'historique des messages`.",
                ephemeral=True
            )
        except Exception as e:
            print(f"❌ Erreur dans top-mj: {e}")
            await interaction.followup.send(
                f"❌ Une erreur est survenue lors de l'analyse des messages.\n"
                f"Erreur : {str(e)}",
                ephemeral=True
            )