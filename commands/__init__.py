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
from .top_mj import TopMjCommand  # ⭐ NOUVELLE COMMANDE

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

# Import conditionnel pour la commande boutique (maintenant OM_PRICE par défaut)
try:
    from .boutique import BoutiqueCommand
    BOUTIQUE_AVAILABLE = True
    print("✅ Module boutique OM_PRICE chargé avec succès")
except ImportError as e:
    print(f"⚠️ Module boutique OM_PRICE non disponible: {e}")
    print("   • Vérifiez que le dossier commands/boutique/ existe")
    print("   • Vérifiez que tous les fichiers _v2.py sont présents")
    print("   • Vérifiez que aiohttp est installé: pip install aiohttp")
    BOUTIQUE_AVAILABLE = False

# Import conditionnel pour la commande de recherche
try:
    from .boutique import SearchCommand
    SEARCH_COMMAND_AVAILABLE = True
    print("✅ Commande de recherche chargée avec succès")
except ImportError:
    SEARCH_COMMAND_AVAILABLE = False
    print("⚠️ Commande de recherche non disponible")

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
    TopMjCommand,  # ⭐ AJOUT DE LA NOUVELLE COMMANDE
    MesQuetesCommand,
    PnjGeneratorCommand,
    ConfigChannelsCommand,
    StatsLogsCommand,  # NOUVEAU - Commande pour les stats de logs
]

# Ajouter les commandes optionnelles si disponibles
if TEST_LOGS_AVAILABLE:
    ALL_COMMANDS.append(TestLogsCommand)
    print("✅ Commande test-logs ajoutée")

if BOUTIQUE_AVAILABLE:
    ALL_COMMANDS.append(BoutiqueCommand)
    print("✅ Commande boutique OM_PRICE ajoutée")

if SEARCH_COMMAND_AVAILABLE:
    ALL_COMMANDS.append(SearchCommand)
    print("✅ Commande de recherche ajoutée")

print(f"📋 Total: {len(ALL_COMMANDS)} commandes chargées")

__all__ = ['ALL_COMMANDS']