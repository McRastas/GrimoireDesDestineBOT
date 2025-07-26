from flask import Flask
from threading import Thread
from config import Config
import logging

logger = logging.getLogger(__name__)


class WebServer:

    def __init__(self):
        self.app = Flask(__name__)
        self._setup_routes()

    def _setup_routes(self):

        @self.app.route('/')
        def home():
            return {
                "status": "active",
                "message": "Bot Faerûn actif",
                "version": "1.0.0"
            }

        @self.app.route('/health')
        def health():
            return {"status": "healthy"}

    def run(self):
        self.app.run(host=Config.FLASK_HOST,
                     port=Config.FLASK_PORT,
                     debug=False)

    def start_in_thread(self):
        thread = Thread(target=self.run, daemon=True)
        thread.start()
        logger.info(
            f"Serveur web démarré sur {Config.FLASK_HOST}:{Config.FLASK_PORT}")
