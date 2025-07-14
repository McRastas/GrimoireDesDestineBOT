import os
import json


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

    # Configuration du rôle admin
    ADMIN_ROLE_NAME = os.getenv('ADMIN_ROLE_NAME', 'Façonneur')

    # NOUVEAU : Configuration générique des canaux
    CHANNELS_CONFIG = {}

    # Valeurs par défaut pour les canaux
    DEFAULT_CHANNELS = {
        'recompenses': 'recompenses',
        'quetes': 'départ-à-l-aventure',
        'logs': 'log',
        'admin': 'bot-admin'
    }

    @classmethod
    def _load_channels_config(cls):
        """Charge la configuration des canaux depuis les variables d'environnement."""

        # Méthode 1: Configuration JSON complète (recommandée)
        channels_json = os.getenv('CHANNELS_CONFIG')
        if channels_json:
            try:
                cls.CHANNELS_CONFIG = json.loads(channels_json)
                print(
                    f"Configuration des canaux chargée depuis JSON : {cls.CHANNELS_CONFIG}"
                )
                return
            except json.JSONDecodeError as e:
                print(f"Erreur parsing CHANNELS_CONFIG JSON : {e}")

        # Méthode 2: Variables individuelles (fallback)
        cls.CHANNELS_CONFIG = {}

        # Charger par nom
        for channel_key, default_name in cls.DEFAULT_CHANNELS.items():
            env_var_name = f'CHANNEL_{channel_key.upper()}_NAME'
            channel_name = os.getenv(env_var_name, default_name)
            cls.CHANNELS_CONFIG[channel_key] = {'name': channel_name}

        # Charger par ID (prioritaire sur le nom)
        for channel_key in cls.DEFAULT_CHANNELS.keys():
            env_var_id = f'CHANNEL_{channel_key.upper()}_ID'
            channel_id = os.getenv(env_var_id)
            if channel_id:
                try:
                    cls.CHANNELS_CONFIG[channel_key]['id'] = int(channel_id)
                except (ValueError, TypeError):
                    print(
                        f"ID de canal invalide pour {channel_key}: {channel_id}"
                    )

        print(f"Configuration des canaux chargée : {cls.CHANNELS_CONFIG}")

    @classmethod
    def get_channel_config(cls, channel_key: str) -> dict:
        """
        Récupère la configuration d'un canal spécifique.

        Args:
            channel_key: Clé du canal (ex: 'recompenses', 'quetes')

        Returns:
            dict: {'name': str, 'id': int} ou {}
        """
        return cls.CHANNELS_CONFIG.get(channel_key, {})

    @classmethod
    def get_channel(cls, guild, channel_key: str):
        """
        Récupère un canal selon sa configuration.

        Args:
            guild: Le serveur Discord
            channel_key: Clé du canal

        Returns:
            discord.TextChannel ou None
        """
        import discord

        config = cls.get_channel_config(channel_key)
        if not config:
            return None

        # Priorité à l'ID si défini
        if 'id' in config:
            return guild.get_channel(config['id'])

        # Sinon recherche par nom
        if 'name' in config:
            return discord.utils.get(guild.text_channels, name=config['name'])

        return None

    # Paramètres internes pour Faerûn
    DR_YEAR_OFFSET = 628
    DELETE_AFTER = 30

    @classmethod
    def validate(cls):
        """Valide la configuration et affiche des informations de débogage."""
        if not cls.DISCORD_TOKEN:
            raise ValueError(
                "DISCORD_TOKEN manquant dans les variables d'environnement")

        # Charger la configuration des canaux
        cls._load_channels_config()

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
        print(f"  - CANAUX CONFIGURÉS: {len(cls.CHANNELS_CONFIG)} canaux")

        for key, config in cls.CHANNELS_CONFIG.items():
            id_info = f" (ID: {config.get('id')})" if config.get('id') else ""
            print(f"    └─ {key}: {config.get('name', 'Non défini')}{id_info}")

        return True
