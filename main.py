import logging
from config import Config
from webserver import WebServer
from faerunbot import FaerunBot

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def main():
    try:
        logger.info("Démarrage de l'application Bot Faerûn")
        Config.validate()
        # web_server = WebServer()
        # web_server.start_in_thread()
        bot = FaerunBot()
        bot.run(Config.DISCORD_TOKEN)
    except ValueError as e:
        logger.error(f"Erreur de configuration: {e}")
    except KeyboardInterrupt:
        logger.info("Arrêt du bot demandé par l'utilisateur")
    except Exception as e:
        logger.error(f"Erreur critique: {e}")
        raise


if __name__ == "__main__":
    main()
