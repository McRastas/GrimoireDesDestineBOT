"""Module des commandes Discord pour le bot Faerûn."""

# Commandes simples
from .test import TestCommand
from .info import InfoCommand

# Commandes calendrier Faerûn
from .faerun_date import FaerunCommand
from .faerun_festival import FaerunFestivalCommand
from .faerun_complet import FaerunCompletCommand
from .faerun_jdr import FaerunJdrCommand

# Commandes mentions et statistiques
from .mention_someone import MentionSomeoneCommand
from .mention_list import MentionListCommand
from .recap_mj import RecapMjCommand

# Commandes quêtes
from .mes_quetes import MesQuetesCommand

# Générateur PNJ
from .pnj_generator import PnjGeneratorCommand

# Liste de toutes les commandes disponibles
ALL_COMMANDS = [
    TestCommand,
    InfoCommand,
    FaerunCommand,
    FaerunFestivalCommand,
    FaerunCompletCommand,
    FaerunJdrCommand,
    MentionSomeoneCommand,
    MentionListCommand,
    RecapMjCommand,
    MesQuetesCommand,
    PnjGeneratorCommand,
]

__all__ = ['ALL_COMMANDS']
