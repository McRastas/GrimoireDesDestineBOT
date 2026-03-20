"""
Commande Discord : /bump

DESCRIPTION:
    Permet de bump le serveur sur Disboard avec un cooldown anti-spam de 2h.
    Enregistre le timestamp du dernier bump dans un fichier JSON persistant.

FONCTIONNEMENT:
    - Vérifie si 2h se sont écoulées depuis le dernier bump
    - Si cooldown actif : message éphémère avec le temps restant
    - Si disponible : enregistre le timestamp et envoie un rappel public
      pour que quelqu'un utilise la commande /bump de Disboard

UTILISATION:
    /bump
"""

import discord
from discord import app_commands
from .base import BaseCommand
import json
import logging
import os
from datetime import datetime, timezone, timedelta

logger = logging.getLogger(__name__)

BUMP_COOLDOWN_HOURS = 2
DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data",
                         "bump_cooldown.json")

DISBOARD_BOT_ID = 302050872383242240


def _load_data() -> dict:
    """Charge les données de cooldown depuis le fichier JSON."""
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Erreur lecture bump_cooldown.json: {e}")
    return {}


def _save_data(data: dict):
    """Sauvegarde les données de cooldown dans le fichier JSON."""
    try:
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        logger.error(f"Erreur écriture bump_cooldown.json: {e}")


def _get_last_bump(guild_id: int) -> datetime | None:
    """Retourne le datetime UTC du dernier bump pour ce serveur."""
    data = _load_data()
    ts = data.get(str(guild_id))
    if ts:
        return datetime.fromisoformat(ts)
    return None


def _set_last_bump(guild_id: int):
    """Enregistre le timestamp actuel comme dernier bump."""
    data = _load_data()
    data[str(guild_id)] = datetime.now(timezone.utc).isoformat()
    _save_data(data)


def _format_remaining(delta: timedelta) -> str:
    """Formate un timedelta en 'Xh Ymin'."""
    total_seconds = int(delta.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    if hours > 0:
        return f"{hours}h {minutes}min"
    return f"{minutes}min"


class DisboardBumpCommand(BaseCommand):

    @property
    def name(self) -> str:
        return "bump"

    @property
    def description(self) -> str:
        return "Rappelle de bump le serveur sur Disboard (cooldown 2h)"

    def register(self, tree: app_commands.CommandTree):
        """Enregistrement de la commande bump."""

        @tree.command(name=self.name, description=self.description)
        async def bump_command(interaction: discord.Interaction):
            await self.callback(interaction)

        # Écoute les confirmations de bump de Disboard pour màj le cooldown
        self._register_disboard_listener()

    def _register_disboard_listener(self):
        """Enregistre un listener sur les messages de Disboard."""

        bot = self.bot

        @bot.event
        async def on_message(message: discord.Message):
            # Ignorer les messages qui ne viennent pas de Disboard
            if message.author.id != DISBOARD_BOT_ID:
                return
            # Disboard envoie un embed avec "Bump done" en cas de succès
            if message.embeds:
                embed = message.embeds[0]
                description = (embed.description or "").lower()
                if "bump done" in description or "serveur mis en avant" in description:
                    if message.guild:
                        _set_last_bump(message.guild.id)
                        logger.info(
                            f"Bump Disboard détecté sur {message.guild.name}, cooldown réinitialisé."
                        )

    async def callback(self, interaction: discord.Interaction):
        guild_id = interaction.guild_id
        now = datetime.now(timezone.utc)
        last_bump = _get_last_bump(guild_id)

        if last_bump:
            elapsed = now - last_bump
            cooldown = timedelta(hours=BUMP_COOLDOWN_HOURS)

            if elapsed < cooldown:
                remaining = cooldown - elapsed
                embed = discord.Embed(
                    title="⏳ Cooldown actif",
                    description=
                    f"Le serveur a déjà été bump récemment.\n\n"
                    f"Prochain bump disponible dans **{_format_remaining(remaining)}**.",
                    color=0xe74c3c)
                embed.set_footer(text="Disboard impose un délai de 2h entre chaque bump.")
                await interaction.response.send_message(embed=embed,
                                                        ephemeral=True)
                return

        # Cooldown expiré ou premier bump : enregistrer et envoyer le rappel
        _set_last_bump(guild_id)

        embed = discord.Embed(
            title="🔔 C'est l'heure de bump !",
            description=
            "Le serveur peut être mis en avant sur **Disboard** !\n\n"
            "Utilisez la commande `/bump` du bot **DISBOARD** pour promouvoir le serveur.",
            color=0x2ecc71)
        embed.add_field(
            name="Comment faire ?",
            value="Tapez `/bump` et sélectionnez la commande du bot **DISBOARD** dans la liste.",
            inline=False)
        embed.set_footer(text=f"Bumped par {interaction.user.display_name} • Prochain bump dans 2h")

        await interaction.response.send_message(embed=embed)
