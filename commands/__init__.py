"""Module des commandes Discord pour le bot Faerûn."""

# ============================================================================
# COMMANDES SIMPLES
# ============================================================================
from .test import TestCommand
from .info import InfoCommand

# ============================================================================
# COMMANDES CALENDRIER FAERÛN
# ============================================================================
from .faerun_date import FaerunCommand
from .faerun_festival import FaerunFestivalCommand
from .faerun_complet import FaerunCompletCommand
from .faerun_jdr import FaerunJdrCommand
from .faerun_help import HelpCommand

# ============================================================================
# COMMANDES MENTIONS ET STATISTIQUES
# ============================================================================
from .mention_someone import MentionSomeoneCommand
from .mention_list import MentionListCommand
from .recap_mj import RecapMjCommand
from .top_mj import TopMjCommand
from .stats_logs import StatsLogsCommand
from .topjoueurs import TopJoueursCommand

# ============================================================================
# COMMANDES QUÊTES
# ============================================================================
from .mes_quetes import MesQuetesCommand

# ============================================================================
# GÉNÉRATEUR PNJ
# ============================================================================
from .pnj_generator import PnjGeneratorCommand

# ============================================================================
# CONFIGURATION ET ADMINISTRATION
# ============================================================================
from .config_channels import ConfigChannelsCommand

# ============================================================================
# IMPORTS CONDITIONNELS
# ============================================================================

# Test Logs
try:
    from .test_logs import TestLogsCommand
    TEST_LOGS_AVAILABLE = True
except ImportError:
    TEST_LOGS_AVAILABLE = False
    print("⚠️ test_logs.py non trouvé - commande /test-logs non disponible")

# Boutique (OM_PRICE)
try:
    from .boutique import BoutiqueCommand, SearchCommand
    BOUTIQUE_AVAILABLE = True
    SEARCH_COMMAND_AVAILABLE = True
    print("✅ Module boutique OM_PRICE chargé avec succès")
except ImportError as e:
    BOUTIQUE_AVAILABLE = False
    SEARCH_COMMAND_AVAILABLE = False
    print(f"⚠️ Module boutique non disponible: {e}")

# Parchemin (Dev3.0)
try:
    from .parchemin import ParcheminCommand
    PARCHEMIN_AVAILABLE = True
    print("✅ Module parchemin chargé avec succès (Dev3.0)")
except ImportError as e:
    PARCHEMIN_AVAILABLE = False
    print(f"⚠️ Module parchemin non disponible: {e}")

# ============================================================================
# LISTE DE TOUTES LES COMMANDES
# ============================================================================

ALL_COMMANDS = [
    # Simples
    TestCommand,
    InfoCommand,
    # Calendrier Faerûn
    FaerunCommand,
    FaerunFestivalCommand,
    FaerunCompletCommand,
    FaerunJdrCommand,
    HelpCommand,
    # Mentions et stats
    MentionSomeoneCommand,
    MentionListCommand,
    RecapMjCommand,
    TopMjCommand,
    StatsLogsCommand,
    TopJoueursCommand,
    # Quêtes
    MesQuetesCommand,
    # Générateur PNJ
    PnjGeneratorCommand,
    # Administration
    ConfigChannelsCommand,
]

# Ajouter les commandes optionnelles
if TEST_LOGS_AVAILABLE:
    ALL_COMMANDS.append(TestLogsCommand)

if BOUTIQUE_AVAILABLE:
    ALL_COMMANDS.append(BoutiqueCommand)

if SEARCH_COMMAND_AVAILABLE:
    ALL_COMMANDS.append(SearchCommand)

if PARCHEMIN_AVAILABLE:
    ALL_COMMANDS.append(ParcheminCommand)

# ============================================================================
# LOGS DE CHARGEMENT
# ============================================================================

print(f"📋 Total: {len(ALL_COMMANDS)} commandes chargées")

__all__ = ['ALL_COMMANDS']