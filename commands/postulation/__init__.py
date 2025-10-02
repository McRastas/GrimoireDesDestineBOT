# commands/postulation/__init__.py
"""
Module de postulation des joueurs pour les quêtes.

Ce module permet aux joueurs de postuler à une quête en :
1. Sélectionnant l'un de leurs personnages actifs depuis Google Sheets
2. Rédigeant un message RP de postulation
3. Postant automatiquement la postulation dans le fil de discussion

Configuration requise dans .env :
- POSTULATION_SHEET_ID : ID du Google Sheet des personnages
- POSTULATION_SHEET_NAME : Nom de la feuille (par défaut: "Suivi des personnages")
- POSTULATION_COL_* : Configuration des colonnes du Google Sheet
- POSTULATION_USE_WEBHOOK : Utiliser webhooks pour poster comme le joueur (true/false)

Utilisation :
    /postuler - Ouvre le menu de sélection de personnage
"""

import logging
from .main_command import PostulationCommand

logger = logging.getLogger(__name__)

# Version du module
__version__ = "1.0.0"

# Auteur
__author__ = "Bot Faerûn Team"

# Export de la commande principale
__all__ = ['PostulationCommand']

logger.info(f"📦 Module postulation v{__version__} chargé")