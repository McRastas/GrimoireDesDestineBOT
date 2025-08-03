"""Module des commandes Discord pour le bot Faerûn."""

# Commandes simples
from .test import TestCommand
from .info import InfoCommand

# Commandes calendrier Faerûn
from .faerun_date import FaerunCommand
from .faerun_festival import FaerunFestivalCommand
from .faerun_complet import FaerunCompletCommand
from .faerun_jdr import FaerunJdrCommand
from .faerun_help import HelpCommand

# Commandes mentions et statistiques
from .mention_someone import MentionSomeoneCommand
from .mention_list import MentionListCommand
from .recap_mj import RecapMjCommand

# Commandes quêtes
from .mes_quetes import MesQuetesCommand

# Générateur PNJ
from .pnj_generator import PnjGeneratorCommand

# Configuration et administration
from .config_channels import ConfigChannelsCommand
from .stats_logs import StatsLogsCommand  # NOUVEAU

# Import conditionnel pour les nouvelles commandes
try:
    from .test_logs import TestLogsCommand
    TEST_LOGS_AVAILABLE = True
except ImportError:
    print("⚠️ test_logs.py non trouvé - commande /test-logs non disponible")
    TEST_LOGS_AVAILABLE = False

# Import conditionnel pour la commande boutique
from .boutique.main_command_v2 import BoutiqueCommandV2

# Liste de toutes les commandes disponibles
ALL_COMMANDS = [
    TestCommand,
    InfoCommand,
    FaerunCommand,
    FaerunFestivalCommand,
    FaerunCompletCommand,
    FaerunJdrCommand,
    HelpCommand,
    MentionSomeoneCommand,
    MentionListCommand,
    RecapMjCommand,
    MesQuetesCommand,
    PnjGeneratorCommand,
    ConfigChannelsCommand,
    StatsLogsCommand,  # NOUVEAU - Commande pour les stats de logs
]
# Ajouter les commandes optionnelles si disponibles
if TEST_LOGS_AVAILABLE:
    ALL_COMMANDS.append(TestLogsCommand)


__all__ = ['ALL_COMMANDS']