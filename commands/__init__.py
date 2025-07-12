"""Module des commandes Discord pour le bot Faerûn."""

from .test import TestCommand
from .info import InfoCommand
from .faerun import FaerunCommand, FaerunFestivalCommand, FaerunCompletCommand, FaerunJdrCommand
from .mentions import MentionSomeoneCommand, MentionListCommand, RecapMjCommand
from .quetes import MesQuetesCommand
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
