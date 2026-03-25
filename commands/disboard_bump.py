"""
Commande Discord : /bump
+ Planificateur automatique pour bumper Disboard

DESCRIPTION:
    Planifie automatiquement le bump du serveur sur Disboard.
    Après chaque bump confirmé par Disboard, le bot choisit aléatoirement
    le prochain horaire entre 2h et 3h plus tard, et l'écrit dans un fichier JSON.

FONCTIONNEMENT:
    - Tâche de fond qui vérifie chaque minute si c'est l'heure de bumper
    - Quand c'est l'heure : envoie un rappel public dans le canal 'bump' configuré
    - Quand Disboard confirme le bump : choisit aléatoirement le prochain horaire
      (entre 2h et 3h) et sauvegarde dans bump_schedule.json
    - /bump : permet de déclencher manuellement et voir le prochain horaire planifié

UTILISATION:
    /bump
"""

import discord
from discord import app_commands
from discord.ext import tasks
from .base import BaseCommand
import json
import logging
import os
import random
from datetime import datetime, timezone, timedelta

logger = logging.getLogger(__name__)

BUMP_MIN_HOURS = 2
BUMP_MAX_HOURS = 3
DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data",
                         "bump_schedule.json")

DISBOARD_BOT_ID = 302050872383242240


def _load_data() -> dict:
    """Charge les données de planification depuis le fichier JSON."""
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Erreur lecture bump_schedule.json: {e}")
    return {}


def _save_data(data: dict):
    """Sauvegarde les données de planification dans le fichier JSON."""
    try:
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        logger.error(f"Erreur écriture bump_schedule.json: {e}")


def _pick_next_bump_time(from_time: datetime = None) -> datetime:
    """Choisit aléatoirement le prochain horaire de bump entre 2h et 3h."""
    if from_time is None:
        from_time = datetime.now(timezone.utc)
    delay_seconds = random.uniform(BUMP_MIN_HOURS * 3600, BUMP_MAX_HOURS * 3600)
    return from_time + timedelta(seconds=delay_seconds)


def _record_bump_and_schedule_next(guild_id: int) -> datetime:
    """Enregistre le bump actuel, choisit le prochain horaire et sauvegarde. Retourne le prochain horaire."""
    data = _load_data()
    now = datetime.now(timezone.utc)
    next_bump = _pick_next_bump_time(now)

    data[str(guild_id)] = {
        "last_bump": now.isoformat(),
        "next_bump": next_bump.isoformat()
    }
    _save_data(data)
    logger.info(
        f"Bump enregistré pour guild {guild_id}. Prochain bump planifié : {next_bump.isoformat()}"
    )
    return next_bump


def _get_guild_data(guild_id: int) -> dict:
    data = _load_data()
    return data.get(str(guild_id), {})


def _get_last_bump(guild_id: int) -> datetime | None:
    ts = _get_guild_data(guild_id).get("last_bump")
    if ts:
        return datetime.fromisoformat(ts)
    return None


def _get_next_bump(guild_id: int) -> datetime | None:
    ts = _get_guild_data(guild_id).get("next_bump")
    if ts:
        return datetime.fromisoformat(ts)
    return None


def _format_remaining(delta: timedelta) -> str:
    """Formate un timedelta en 'Xh Ymin'."""
    total_seconds = int(delta.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    if hours > 0:
        return f"{hours}h {minutes}min"
    return f"{minutes}min"


class DisboardBumpCommand(BaseCommand):

    def __init__(self, bot):
        super().__init__(bot)
        self._scheduler_started = False

    @property
    def name(self) -> str:
        return "bump"

    @property
    def description(self) -> str:
        return "Bump le serveur sur Disboard (planification automatique 2-3h)"

    def register(self, tree: app_commands.CommandTree):
        """Enregistrement de la commande bump et démarrage du planificateur."""

        @tree.command(name=self.name, description=self.description)
        async def bump_command(interaction: discord.Interaction):
            await self.callback(interaction)

        self._register_disboard_listener()

        if not self._scheduler_started:
            self._bump_scheduler.start()
            self._scheduler_started = True
            logger.info("Planificateur automatique de bump Disboard démarré.")

    # ---------- Tâche de planification automatique ----------

    @tasks.loop(minutes=1)
    async def _bump_scheduler(self):
        """Vérifie chaque minute si c'est l'heure de bumper pour chaque serveur."""
        now = datetime.now(timezone.utc)
        data = _load_data()

        for guild_id_str, guild_data in data.items():
            try:
                next_bump_str = guild_data.get("next_bump")
                if not next_bump_str:
                    continue

                next_bump = datetime.fromisoformat(next_bump_str)
                if now >= next_bump:
                    guild = self.bot.get_guild(int(guild_id_str))
                    if guild:
                        await self._send_bump_reminder(guild)
            except Exception as e:
                logger.error(f"Erreur planificateur bump (guild {guild_id_str}): {e}")

    @_bump_scheduler.before_loop
    async def _before_bump_scheduler(self):
        await self.bot.wait_until_ready()

    async def _send_bump_reminder(self, guild: discord.Guild):
        """Envoie un rappel public dans le canal de bump configuré."""
        from config import Config

        channel = Config.get_channel(guild, 'bump')
        if not channel:
            # Fallback : canal système ou premier canal texte accessible
            channel = guild.system_channel or next(
                (c for c in guild.text_channels
                 if c.permissions_for(guild.me).send_messages),
                None
            )

        if not channel:
            logger.warning(f"Aucun canal de bump disponible sur {guild.name}")
            return

        try:
            embed = discord.Embed(
                title="🔔 C'est l'heure de bump Disboard !",
                description="Le serveur peut être mis en avant sur **Disboard** !\n\n"
                            "Utilisez la commande `/bump` du bot **DISBOARD** pour promouvoir le serveur.",
                color=0x2ecc71)
            embed.add_field(
                name="Comment faire ?",
                value="Tapez `/bump` et sélectionnez la commande du bot **DISBOARD** dans la liste.",
                inline=False)
            embed.set_footer(text="Le prochain horaire sera fixé automatiquement après confirmation.")

            await channel.send(embed=embed)
            logger.info(f"Rappel de bump envoyé dans #{channel.name} sur {guild.name}")
        except Exception as e:
            logger.error(f"Erreur envoi rappel bump sur {guild.name}: {e}")

    # ---------- Listener sur les messages de Disboard ----------

    def _register_disboard_listener(self):
        """Enregistre un listener sur les messages de Disboard."""
        bot = self.bot

        @bot.event
        async def on_message(message: discord.Message):
            # Ignorer tout ce qui ne vient pas de Disboard
            if message.author.id != DISBOARD_BOT_ID:
                return

            if message.embeds:
                embed = message.embeds[0]
                description = (embed.description or "").lower()
                if "bump done" in description or "serveur mis en avant" in description:
                    if message.guild:
                        next_bump = _record_bump_and_schedule_next(message.guild.id)
                        logger.info(
                            f"Bump Disboard confirmé sur {message.guild.name}. "
                            f"Prochain bump : {next_bump.isoformat()}"
                        )
                        # Confirmer le prochain horaire dans le même canal
                        try:
                            next_str = next_bump.strftime("%H:%M UTC")
                            delay_total = int((next_bump - datetime.now(timezone.utc)).total_seconds())
                            delay_h = delay_total // 3600
                            delay_m = (delay_total % 3600) // 60
                            await message.channel.send(
                                f"✅ Bump enregistré ! Prochain rappel automatique à **{next_str}** "
                                f"(dans {delay_h}h {delay_m}min).",
                                delete_after=120)
                        except Exception as e:
                            logger.error(f"Erreur confirmation bump: {e}")

    # ---------- Commande /bump ----------

    async def callback(self, interaction: discord.Interaction):
        guild_id = interaction.guild_id
        now = datetime.now(timezone.utc)
        last_bump = _get_last_bump(guild_id)
        next_bump = _get_next_bump(guild_id)

        if last_bump:
            elapsed = now - last_bump
            cooldown = timedelta(hours=BUMP_MIN_HOURS)

            if elapsed < cooldown:
                remaining = cooldown - elapsed
                next_str = next_bump.strftime("%H:%M UTC") if next_bump else "inconnue"
                embed = discord.Embed(
                    title="⏳ Cooldown actif",
                    description=f"Le serveur a déjà été bump récemment.\n\n"
                                f"Prochain bump disponible dans **{_format_remaining(remaining)}**.\n"
                                f"Prochain rappel automatique prévu à **{next_str}**.",
                    color=0xe74c3c)
                embed.set_footer(text="Disboard impose un délai de 2h entre chaque bump.")
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return

        # Disponible : planifier le prochain bump
        next_bump = _record_bump_and_schedule_next(guild_id)
        next_str = next_bump.strftime("%H:%M UTC")
        delay_total = int((next_bump - now).total_seconds())
        delay_h = delay_total // 3600
        delay_m = (delay_total % 3600) // 60

        embed = discord.Embed(
            title="🔔 C'est l'heure de bump !",
            description="Le serveur peut être mis en avant sur **Disboard** !\n\n"
                        "Utilisez la commande `/bump` du bot **DISBOARD** pour promouvoir le serveur.",
            color=0x2ecc71)
        embed.add_field(
            name="Comment faire ?",
            value="Tapez `/bump` et sélectionnez la commande du bot **DISBOARD** dans la liste.",
            inline=False)
        embed.add_field(
            name="⏰ Prochain rappel automatique",
            value=f"Le bot rappellera automatiquement à **{next_str}** (dans {delay_h}h {delay_m}min).",
            inline=False)
        embed.set_footer(text=f"Bumped par {interaction.user.display_name}")

        await interaction.response.send_message(embed=embed, ephemeral=True)
