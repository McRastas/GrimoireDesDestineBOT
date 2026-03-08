"""Commande /pj_dispo — Affiche les PJ disponibles dans une range de niveau."""

import discord
from discord import app_commands
from typing import Optional
import logging
import aiohttp
import csv
import io
from datetime import datetime, timedelta

from .base import BaseCommand

logger = logging.getLogger(__name__)

SHEET_ID = "1QPLhU1I594hKQdvg4LhrL6Tui6pko01hiRO0DUnvk2U"
SHEET_GID = "0"

# Indices des colonnes (0-based)
COL_NOM_PJ = 1       # B
COL_JOUEUR = 2       # C
COL_NIVEAU = 14      # O
COL_DERNIERE_MAJ = 17  # R


class PjDispoCommand(BaseCommand):
    """Commande pour lister les PJ disponibles selon leur niveau et inactivité."""

    @property
    def name(self) -> str:
        return "pj_dispo"

    @property
    def description(self) -> str:
        return "Liste les PJ disponibles dans une range de niveau"

    def register(self, tree: app_commands.CommandTree):

        @tree.command(name=self.name, description=self.description)
        @app_commands.describe(
            niveaux="Range de niveau (ex: 3-8, min 1 max 20)",
            jours="Filtrer les PJ n'ayant pas joué depuis X jours (optionnel)"
        )
        async def pj_dispo_command(
            interaction: discord.Interaction,
            niveaux: str,
            jours: Optional[int] = None
        ):
            await self.callback(interaction, niveaux, jours)

    async def callback(
        self,
        interaction: discord.Interaction,
        niveaux: str,
        jours: Optional[int] = None
    ):
        await interaction.response.defer()

        # --- Validation de la range de niveau ---
        try:
            parts = niveaux.strip().split("-")
            if len(parts) != 2:
                raise ValueError
            lvl_min, lvl_max = int(parts[0]), int(parts[1])
            if not (1 <= lvl_min <= 20 and 1 <= lvl_max <= 20 and lvl_min <= lvl_max):
                raise ValueError
        except ValueError:
            await interaction.followup.send(
                "❌ Format invalide. Utilise une range comme `3-8` (niveaux 1 à 20).",
                ephemeral=True
            )
            return

        # --- Récupération du Google Sheet ---
        url = (
            f"https://docs.google.com/spreadsheets/d/{SHEET_ID}"
            f"/gviz/tq?tqx=out:csv&gid={SHEET_GID}"
        )
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status != 200:
                        raise ConnectionError(f"HTTP {resp.status}")
                    text = await resp.text()
        except Exception as e:
            logger.error(f"Erreur accès Google Sheet pj_dispo: {e}")
            await interaction.followup.send(
                "❌ Impossible d'accéder au sheet. Vérifie qu'il est bien public.",
                ephemeral=True
            )
            return

        # --- Parsing et filtrage ---
        cutoff = datetime.now() - timedelta(days=jours) if jours else None
        results = []
        errors = []

        reader = csv.reader(io.StringIO(text))
        rows = list(reader)

        for i, row in enumerate(rows[1:], start=2):  # skip header, 1-based row num
            # Colonnes suffisantes ?
            if len(row) <= COL_DERNIERE_MAJ:
                continue

            nom_pj = row[COL_NOM_PJ].strip()
            joueur = row[COL_JOUEUR].strip()

            if not nom_pj:
                continue

            # Niveau
            try:
                niveau = int(row[COL_NIVEAU].strip())
            except (ValueError, IndexError):
                continue

            if not (lvl_min <= niveau <= lvl_max):
                continue

            # Filtre par jours d'inactivité
            date_str = row[COL_DERNIERE_MAJ].strip()
            if cutoff:
                if not date_str:
                    continue  # pas de date = on ignore
                try:
                    derniere_maj = datetime.strptime(date_str, "%d/%m/%Y")
                    if derniere_maj >= cutoff:
                        continue  # a joué récemment
                except ValueError:
                    errors.append(f"Ligne {i} — date invalide: `{date_str}`")
                    continue

            results.append({
                "nom": nom_pj,
                "joueur": joueur,
                "niveau": niveau,
                "date": date_str or "—"
            })

        # --- Construction de la réponse ---
        if not results:
            titre = f"Aucun PJ trouvé — Niveaux {lvl_min} à {lvl_max}"
            desc = ""
            if jours:
                desc = f"Aucun PJ de niveau {lvl_min}-{lvl_max} inactif depuis plus de {jours} jour(s)."
            else:
                desc = f"Aucun PJ de niveau {lvl_min} à {lvl_max} dans le sheet."
            embed = discord.Embed(title=titre, description=desc, color=discord.Color.orange())
            await interaction.followup.send(embed=embed)
            return

        # Trier par niveau puis par nom
        results.sort(key=lambda x: (x["niveau"], x["nom"]))

        titre = f"PJ disponibles — Niveaux {lvl_min} à {lvl_max}"
        if jours:
            titre += f" — Inactifs depuis {jours}j+"

        lines = []
        for pj in results:
            lines.append(
                f"**{pj['nom']}** (_{pj['joueur']}_) — Niv. **{pj['niveau']}** | Dernière MAJ : {pj['date']}"
            )

        description = "\n".join(lines)

        # Discord limite les embeds à 4096 chars
        if len(description) > 4000:
            description = description[:3990] + "\n…*(liste tronquée)*"

        embed = discord.Embed(
            title=titre,
            description=description,
            color=discord.Color.green()
        )
        embed.set_footer(text=f"{len(results)} PJ trouvé(s)")

        if errors:
            embed.add_field(
                name="⚠️ Lignes ignorées",
                value="\n".join(errors[:5]),
                inline=False
            )

        await interaction.followup.send(embed=embed)
