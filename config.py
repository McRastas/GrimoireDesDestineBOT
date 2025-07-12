import os


class Config:
    # Token Discord obligatoire
    DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
    CLIENT_ID = os.getenv('CLIENT_ID')

    # Paramètres du serveur Flask
    FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
    FLASK_PORT = int(os.getenv('FLASK_PORT', 8080))

    # ID de la guild pour la synchro rapide des slash commands (optionnel)
    GUILD_ID = None
    try:
        guild_id_str = os.getenv('GUILD_ID')
        if guild_id_str:
            GUILD_ID = int(guild_id_str)
            print(f"GUILD_ID chargé : {GUILD_ID}")
        else:
            print("GUILD_ID non défini - synchronisation globale utilisée")
    except (ValueError, TypeError) as e:
        print(f"Erreur lors du parsing de GUILD_ID : {e}")
        GUILD_ID = None

    # Configuration du rôle admin - NOUVEAU
    ADMIN_ROLE_NAME = os.getenv('ADMIN_ROLE_NAME', 'Façonneur')

    # Paramètres internes pour Faerûn
    DR_YEAR_OFFSET = 628
    DELETE_AFTER = 30  # Durée avant suppression des messages (secondes)

    @classmethod
    def validate(cls):
        """Valide la configuration et affiche des informations de débogage."""
        if not cls.DISCORD_TOKEN:
            raise ValueError(
                "DISCORD_TOKEN manquant dans les variables d'environnement")

        if not cls.CLIENT_ID:
            print(
                "⚠️  CLIENT_ID non défini - la commande !sync_bot ne fonctionnera pas correctement"
            )
        else:
            print(f"CLIENT_ID chargé : {cls.CLIENT_ID}")

        print(f"Configuration validée:")
        print(
            f"  - DISCORD_TOKEN: {'✓ Présent' if cls.DISCORD_TOKEN else '✗ Manquant'}"
        )
        print(
            f"  - CLIENT_ID: {'✓ Présent' if cls.CLIENT_ID else '✗ Manquant'}")
        print(
            f"  - GUILD_ID: {cls.GUILD_ID if cls.GUILD_ID else '✗ Non défini'}"
        )
        print(f"  - ADMIN_ROLE_NAME: {cls.ADMIN_ROLE_NAME}")

        return True
