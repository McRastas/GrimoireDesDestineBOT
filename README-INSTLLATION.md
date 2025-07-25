# 🐳 Installation Docker - Bot Discord Faerûn

Installation rapide avec Docker en utilisant le clone automatique du repository GitHub.

## 📋 Prérequis

- Docker et Docker Compose installés
- Token Discord et Client ID de votre bot

## 🚀 Installation

### 1. Créer les fichiers Docker

Créez un dossier pour votre bot et ajoutez ces 3 fichiers :

#### `Dockerfile`
```dockerfile
FROM python:3.11-slim

LABEL maintainer="votre-email@example.com"
LABEL description="Bot Discord Faerûn - Calendrier D&D"

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Installation de git + gcc
RUN apt-get update && apt-get install -y \
    git \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Clone automatique du repository
RUN git clone https://github.com/McRastas/GrimoireDesDestineBOT.git . && \
    rm -rf .git

# Installation des dépendances Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Créer utilisateur non-root
RUN groupadd -r botuser && useradd --no-log-init -r -g botuser botuser
RUN chown -R botuser:botuser /app
USER botuser

EXPOSE 8080
CMD ["python", "main.py"]
```

#### `docker-compose.yml`
```yaml
services:
  faerun-bot:
    build: .
    container_name: faerun-bot
    restart: unless-stopped
    env_file:
      - .env
    ports:
      - "8080:8080"
    volumes:
      - ./logs:/app/logs
    healthcheck:
      test: ["CMD", "python", "-c", "import sys; sys.exit(0)"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

#### `.env`
```env
# Discord (OBLIGATOIRE - remplacez par vos vraies valeurs)
DISCORD_TOKEN=votre_token_discord_ici
CLIENT_ID=votre_client_id_ici

# Serveur Discord (OPTIONNEL)
GUILD_ID=votre_guild_id_pour_sync_rapide
ADMIN_ROLE_NAME=Façonneur

# Configuration des canaux (RECOMMANDÉ)
CHANNELS_CONFIG={"recompenses":{"name":"recompenses"},"quetes":{"name":"départ-à-l-aventure"},"logs":{"name":"bot-logs"},"admin":{"name":"bot-admin"}}

# Web Server (OPTIONNEL)
FLASK_HOST=0.0.0.0
FLASK_PORT=8080
```

### 2. Configuration

Éditez le fichier `.env` et remplacez :
- `votre_token_discord_ici` → Votre token Discord
- `votre_client_id_ici` → Votre Client ID Discord

### 3. Démarrage

```bash
# Construire et démarrer le bot
docker compose up -d

# Voir les logs
docker compose logs -f

# Arrêter le bot
docker compose down
```

## 🔄 Commandes utiles

```bash
# Voir le statut
docker compose ps

# Redémarrer
docker compose restart

# Mise à jour (récupère la dernière version GitHub)
docker compose down
docker compose build --no-cache
docker compose up -d

# Voir les logs en temps réel
docker compose logs -f

# Nettoyer et reconstruire
docker compose down
docker system prune -f
docker compose build --no-cache
docker compose up -d
```

## 🎯 Structure finale

Votre dossier doit contenir :
```
votre-dossier-bot/
├── Dockerfile
├── docker-compose.yml
└── .env
```

Le code du bot sera automatiquement téléchargé depuis GitHub lors de la construction de l'image.
