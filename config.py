import os
import json

# Support automatique des fichiers .env
try:
    from dotenv import load_dotenv
    load_dotenv()  # Charge automatiquement .env si présent
    print("✓ Fichier .env chargé")
except ImportError:
    print(
        "ℹ️ python-dotenv non installé - utilisation des variables d'environnement système"
    )


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
            print(f"✓ GUILD_ID chargé : {GUILD_ID}")
        else:
            print("ℹ️ GUILD_ID non défini - synchronisation globale utilisée")
    except (ValueError, TypeError) as e:
        print(f"⚠️ Erreur lors du parsing de GUILD_ID : {e}")
        GUILD_ID = None

    # Configuration du rôle admin
    ADMIN_ROLE_NAME = os.getenv('ADMIN_ROLE_NAME', 'Façonneur')

    # Configuration générique des canaux
    CHANNELS_CONFIG = {}

    # Valeurs par défaut pour les canaux
    DEFAULT_CHANNELS = {
        'recompenses': 'recompenses',
        'quetes': 'départ-à-l-aventure',
        'logs': 'bot-logs',
        'admin': 'bot-admin',
        'bump': 'bump'
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
                    f"✓ Configuration des canaux chargée depuis JSON : {cls.CHANNELS_CONFIG}"
                )
                return
            except json.JSONDecodeError as e:
                print(f"⚠️ Erreur parsing CHANNELS_CONFIG JSON : {e}")

        # Méthode 2: Variables individuelles (fallback)
        print(
            "ℹ️ Configuration JSON non trouvée, utilisation des variables individuelles..."
        )
        cls.CHANNELS_CONFIG = {}

        # Charger par nom
        for channel_key, default_name in cls.DEFAULT_CHANNELS.items():
            env_var_name = f'CHANNEL_{channel_key.upper()}_NAME'
            channel_name = os.getenv(env_var_name)
            if channel_name:
                cls.CHANNELS_CONFIG[channel_key] = {'name': channel_name}
                print(f"✓ {channel_key} configuré par nom: {channel_name}")

        # Charger par ID (prioritaire sur le nom)
        for channel_key in cls.DEFAULT_CHANNELS.keys():
            env_var_id = f'CHANNEL_{channel_key.upper()}_ID'
            channel_id = os.getenv(env_var_id)
            if channel_id:
                try:
                    if channel_key not in cls.CHANNELS_CONFIG:
                        cls.CHANNELS_CONFIG[channel_key] = {}
                    cls.CHANNELS_CONFIG[channel_key]['id'] = int(channel_id)
                    print(f"✓ {channel_key} configuré par ID: {channel_id}")
                except (ValueError, TypeError):
                    print(
                        f"⚠️ ID de canal invalide pour {channel_key}: {channel_id}"
                    )

        if cls.CHANNELS_CONFIG:
            print(
                f"✓ Configuration des canaux finalisée : {cls.CHANNELS_CONFIG}"
            )
        else:
            print(
                "⚠️ Aucun canal configuré - utilisez CHANNELS_CONFIG ou CHANNEL_*_NAME/ID"
            )

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
            channel = guild.get_channel(config['id'])
            if channel:
                return channel
            else:
                print(
                    f"⚠️ Canal avec ID {config['id']} introuvable pour {channel_key}"
                )

        # Sinon recherche par nom
        if 'name' in config:
            channel = discord.utils.get(guild.text_channels,
                                        name=config['name'])
            if channel:
                return channel
            else:
                print(
                    f"⚠️ Canal avec nom '{config['name']}' introuvable pour {channel_key}"
                )

        return None

    # Paramètres internes pour Faerûn
    DR_YEAR_OFFSET = 628
    DELETE_AFTER = 30

    @classmethod
    def validate(cls):
        """Valide la configuration et affiche des informations de débogage."""
        print("\n" + "=" * 50)
        print("🔧 VALIDATION DE LA CONFIGURATION")
        print("=" * 50)

        # Validation du token Discord
        if not cls.DISCORD_TOKEN:
            raise ValueError(
                "❌ DISCORD_TOKEN manquant dans les variables d'environnement")
        else:
            print("✓ DISCORD_TOKEN: Présent")

        # Charger la configuration des canaux
        cls._load_channels_config()

        if not cls.CLIENT_ID:
            print(
                "⚠️ CLIENT_ID non défini - la commande !sync_bot ne fonctionnera pas correctement"
            )
        else:
            print(f"✓ CLIENT_ID: {cls.CLIENT_ID}")

        print(f"✓ ADMIN_ROLE_NAME: {cls.ADMIN_ROLE_NAME}")
        print(f"✓ FLASK_HOST: {cls.FLASK_HOST}")
        print(f"✓ FLASK_PORT: {cls.FLASK_PORT}")

        if cls.GUILD_ID:
            print(f"✓ GUILD_ID: {cls.GUILD_ID} (sync rapide)")
        else:
            print("ℹ️ GUILD_ID: Non défini (sync global)")

        print(f"✓ CANAUX CONFIGURÉS: {len(cls.CHANNELS_CONFIG)} canaux")
        for key, config in cls.CHANNELS_CONFIG.items():
            id_info = f" (ID: {config.get('id')})" if config.get('id') else ""
            name_info = f"#{config.get('name')}" if config.get(
                'name') else "Nom non défini"
            print(f"  └─ {key}: {name_info}{id_info}")

        print("=" * 50)
        print("✅ Configuration validée avec succès !")
        print("=" * 50 + "\n")

        return True

    @classmethod
    def get_env_template(cls):
        """Retourne un template de fichier .env pour référence."""
        return """# =================================
# CONFIGURATION BOT FAERÛN
# =================================

# Discord (OBLIGATOIRE)
DISCORD_TOKEN=votre_token_discord_ici
CLIENT_ID=votre_client_id_ici

# Serveur (OPTIONNEL)
GUILD_ID=123456789
ADMIN_ROLE_NAME=Façonneur

# Web Server (OPTIONNEL)  
FLASK_HOST=0.0.0.0
FLASK_PORT=8080

# Canaux - Méthode JSON (RECOMMANDÉ)
CHANNELS_CONFIG={"recompenses":{"name":"recompenses"},"quetes":{"name":"départ-à-l-aventure"},"logs":{"name":"bot-logs"},"admin":{"name":"bot-admin"}}

# OU Canaux - Variables individuelles (ALTERNATIVE)
# CHANNEL_RECOMPENSES_NAME=recompenses
# CHANNEL_QUETES_NAME=départ-à-l-aventure
# CHANNEL_LOGS_NAME=bot-logs
# CHANNEL_ADMIN_NAME=bot-admin
# CHANNEL_BUMP_NAME=bump

# Suivi des personnages — /pj_dispo (OPTIONNEL)
# PJ_DISPO_SHEET_ID=1QPLhU1I594hKQdvg4LhrL6Tui6pko01hiRO0DUnvk2U
# PJ_DISPO_SHEET_GID=0
# PJ_DISPO_SHEET_NAME=        # Nom de l'onglet (prioritaire sur GID si défini)
# Colonnes (index 0-based, A=0, B=1, C=2…)
# PJ_DISPO_COL_NOM_PJ=1       # B — Nom du PJ
# PJ_DISPO_COL_JOUEUR=2       # C — Joueur
# PJ_DISPO_COL_NIVEAU=14      # O — Niv. PJ
# PJ_DISPO_COL_DERNIERE_MAJ=17  # R — Dernière MAJ
"""

    @classmethod
    def create_env_template(cls, filename=".env.template"):
        """Crée un fichier template .env."""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(cls.get_env_template())
        print(f"✓ Template créé: {filename}")
        print("💡 Copiez ce fichier vers .env et remplissez vos valeurs")
