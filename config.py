import os


class Config:
    # Token Discord obligatoire
    DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

    # Préfixe des commandes (non utilisé avec les slash commands)
    COMMAND_PREFIX = os.getenv('COMMAND_PREFIX', '!')

    # Paramètres du serveur Flask
    FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
    FLASK_PORT = int(os.getenv('FLASK_PORT', 8080))

    # ID de la guild pour la synchro rapide des slash commands (optionnel)
    try:
        GUILD_ID = int(
            os.getenv('GUILD_ID')) if os.getenv('GUILD_ID') else None
    except ValueError:
        GUILD_ID = None

    # Paramètres internes pour Faerûn
    DR_YEAR_OFFSET = 628
    DELETE_AFTER = 30  # Durée avant suppression des messages (secondes)

    @classmethod
    def validate(cls):
        if not cls.DISCORD_TOKEN:
            raise ValueError(
                "DISCORD_TOKEN manquant dans les variables d'environnement")
        return True
