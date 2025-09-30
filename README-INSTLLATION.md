# 🐳 Installation Docker - Bot Discord Faerûn

Installation rapide avec Docker en utilisant le clone automatique du repository GitHub avec mise à jour automatique au démarrage.

## 📋 Prérequis

- Docker et Docker Compose installés
- Token Discord de votre bot
- (Optionnel) Accès à un Google Sheets public pour la boutique d'objets magiques

## 🚀 Installation

### 1. Créer les fichiers Docker

Créez un dossier pour votre bot et ajoutez ces 3 fichiers :

#### `Dockerfile`
```dockerfile
FROM python:3.13-slim

LABEL maintainer="votre-email@example.com"
LABEL description="Bot Discord Faerûn - Calendrier D&D avec logs quotidiens"

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Installation de git + gcc
RUN apt-get update && apt-get install -y \
    git \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Variable d'environnement pour la branche (peut être override)
ARG GIT_BRANCH=main
ENV GIT_BRANCH=${GIT_BRANCH}

# Clone automatique du repository en gardant .git
RUN git clone https://github.com/McRastas/GrimoireDesDestineBOT.git . && \
    git checkout ${GIT_BRANCH}

# Configuration Git pour éviter les conflits de permissions
RUN git config --global --add safe.directory /app && \
    git config --global user.email "bot@faerun.local" && \
    git config --global user.name "Faerun Bot"

# Installation des dépendances Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Créer le répertoire de logs avec les bonnes permissions
RUN mkdir -p /app/logs && \
    chmod 755 /app/logs

# Créer utilisateur non-root
RUN groupadd -r botuser && useradd --no-log-init -r -g botuser botuser

# IMPORTANT : Donner les permissions sur tout /app Y COMPRIS .git
RUN chown -R botuser:botuser /app && \
    chmod -R u+w /app/.git

# Script simple pour update au démarrage
RUN echo '#!/bin/bash\ncd /app\ngit checkout $GIT_BRANCH 2>/dev/null || true\ngit pull origin $GIT_BRANCH 2>/dev/null || true\nexec "$@"' > /usr/local/bin/start.sh && \
    chmod +x /usr/local/bin/start.sh && \
    chown botuser:botuser /usr/local/bin/start.sh

# Changer vers l'utilisateur non-root
USER botuser

# Exposer le port web et définir le volume de logs
EXPOSE 8080
VOLUME ["/app/logs"]

ENTRYPOINT ["/usr/local/bin/start.sh"]
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
    environment:
      - GIT_DISCOVERY_ACROSS_FILESYSTEM=1
      - GIT_CONFIG_GLOBAL=/app/.gitconfig
      - GIT_BRANCH=${GIT_BRANCH:-main}  # Branche par défaut
```

#### `.env`
```env
# =================================
# CONFIGURATION BOT FAERÛN
# =================================

# Discord (OBLIGATOIRE - remplacez par vos vraies valeurs)
DISCORD_TOKEN=votre_token_discord_ici
CLIENT_ID=votre_client_id_ici

# Serveur Discord (OPTIONNEL)
GUILD_ID=votre_guild_id_pour_sync_rapide
ADMIN_ROLE_NAME=Façonneur

# Configuration des canaux (RECOMMANDÉ)
CHANNELS_CONFIG={"recompenses":{"name":"recompenses"},"quetes":{"name":"départ-à-l-aventure"},"logs":{"name":"log"},"admin":{"name":"bot-admin"}}

# Web Server (OPTIONNEL)
FLASK_HOST=0.0.0.0
FLASK_PORT=8080

# ============================================================================
# CONFIGURATION GOOGLE SHEETS (OPTIONNEL - Pour la commande /boutique)
# ============================================================================

# ID du Google Sheets (extrait de l'URL)
# URL: https://docs.google.com/spreadsheets/d/ID_ICI/edit
BOUTIQUE_SHEET_ID=votre_sheet_id_ici

# Nom de la feuille dans le Google Sheets
BOUTIQUE_SHEET_NAME=Objets Magique
BOUTIQUE_SHEET_GID=0

# Configuration des colonnes - AJUSTEZ selon vos noms de colonnes
BOUTIQUE_COL_NOM_FRANCAIS=NomVF
BOUTIQUE_COL_NOM_ANGLAIS=Nom en VO
BOUTIQUE_COL_TYPE=Type
BOUTIQUE_COL_RARITY=Rareté
BOUTIQUE_COL_LIEN=Lien
BOUTIQUE_COL_SOURCE=Source
BOUTIQUE_COL_PRICE_ACHAT=OM_PRICE
BOUTIQUE_COL_PRIX=OM_PRICE

# Configuration de sélection
BOUTIQUE_MIN_ITEMS=3
BOUTIQUE_MAX_ITEMS=15
BOUTIQUE_EXCLUDED_RARITIES=Légendaire,Artefact
BOUTIQUE_RARITY_COLUMN=Rareté
BOUTIQUE_REQUIRE_PRICE=
```

### 2. Configuration

#### Configuration minimale (Discord uniquement)

Éditez le fichier `.env` et remplacez :
- `votre_token_discord_ici` → Votre token Discord
- `votre_client_id_ici` → Votre Client ID Discord

#### Configuration complète (avec Google Sheets)

Si vous voulez utiliser la commande `/boutique` pour les objets magiques, ajoutez également :
- `votre_sheet_id_ici` → L'ID de votre Google Sheets (trouvé dans l'URL)
- Ajustez les noms de colonnes selon votre feuille Google Sheets

**Pour trouver l'ID du Google Sheets :**
```
URL : https://docs.google.com/spreadsheets/d/1ABC123XYZ456/edit
ID  : 1ABC123XYZ456
```

### 3. Démarrage

```bash
# Construire et démarrer le bot
docker compose up -d

# Voir les logs en temps réel
docker compose logs -f

# Arrêter le bot
docker compose down
```

## 🔄 Commandes Docker essentielles

### Build et gestion de l'image

```bash
# Builder l'image depuis le Dockerfile
docker build -t mon-bot-faerun .

# Builder avec une branche spécifique
docker build --build-arg GIT_BRANCH=dev -t mon-bot-faerun:dev .

# Builder sans cache (si vous avez des problèmes)
docker build --no-cache -t mon-bot-faerun .
```

### Push sur Docker Hub (optionnel)

Si vous voulez partager votre image sur Docker Hub :

```bash
# Se connecter à Docker Hub
docker login

# Taguer votre image avec votre nom d'utilisateur
docker tag mon-bot-faerun votre-username/nom-image:latest

# Pousser l'image
docker push votre-username/nom-image:latest
```

### Gestion du conteneur

```bash
# Démarrer
docker compose up -d

# Arrêter
docker compose down

# Redémarrer
docker compose restart

# Voir le statut
docker compose ps

# Voir les logs
docker compose logs -f

# Voir les logs depuis les 100 dernières lignes
docker compose logs --tail=100 -f
```

### Mise à jour du bot

Le bot se met automatiquement à jour depuis GitHub à chaque redémarrage !

```bash
# Simple redémarrage (récupère les dernières mises à jour)
docker compose restart

# OU mise à jour complète avec rebuild
docker compose down
docker compose build --pull  # Récupère les dernières dépendances
docker compose up -d

# OU rebuild local complet
docker compose down
docker compose build --no-cache
docker compose up -d
```

### Debugging

```bash
# Entrer dans le conteneur pour débugger
docker exec -it faerun-bot /bin/bash

# Voir l'utilisation des ressources
docker stats faerun-bot

# Inspecter le conteneur
docker inspect faerun-bot

# Voir les logs d'erreur uniquement
docker compose logs | grep -i error
```

### Nettoyage

```bash
# Nettoyer les conteneurs arrêtés
docker container prune

# Nettoyer les images non utilisées
docker image prune

# Nettoyer tout (ATTENTION: supprime tout ce qui n'est pas utilisé)
docker system prune -a

# Nettoyer et reconstruire complètement
docker compose down
docker system prune -f
docker compose build --no-cache
docker compose up -d
```

## 📁 Structure finale

Votre dossier doit contenir :
```
votre-dossier-bot/
├── Dockerfile
├── docker-compose.yml
├── .env
└── logs/                    # Créé automatiquement
    └── bot_YYYY-MM-DD.log   # Logs quotidiens du bot
```

Le code du bot sera automatiquement téléchargé depuis GitHub lors de la construction de l'image et mis à jour à chaque redémarrage.

## 🎯 Fonctionnalités avancées

### Changer de branche Git

Pour utiliser une branche de développement :

```bash
# Dans .env, ajoutez :
GIT_BRANCH=dev

# Puis rebuild
docker compose down
docker compose build --no-cache
docker compose up -d
```

### Logs quotidiens

Les logs du bot sont automatiquement sauvegardés dans `./logs/` avec rotation quotidienne :
- Format : `bot_2025-09-30.log`
- Accessible depuis votre machine hôte
- Persistant même si le conteneur est supprimé

### Surveillance en temps réel

```bash
# Terminal 1 : Logs du bot
docker compose logs -f

# Terminal 2 : Ressources système
watch docker stats faerun-bot

# Terminal 3 : Logs applicatifs
tail -f ./logs/bot_$(date +%Y-%m-%d).log
```

## 🔧 Résolution de problèmes

### Le bot ne démarre pas
```bash
# Vérifier les logs
docker compose logs

# Vérifier que le token Discord est correct dans .env
cat .env | grep DISCORD_TOKEN

# Reconstruire sans cache
docker compose down
docker compose build --no-cache
docker compose up -d
```

### Erreur de permissions Git
```bash
# Le script de démarrage gère automatiquement les permissions
# Si le problème persiste, rebuild l'image
docker compose build --no-cache
```

### La commande /boutique ne fonctionne pas
```bash
# Vérifier que toutes les variables Google Sheets sont définies
cat .env | grep BOUTIQUE

# Vérifier que votre Google Sheet est public
# Testez l'URL : https://docs.google.com/spreadsheets/d/VOTRE_ID/export?format=csv
```

### Les logs ne s'affichent pas
```bash
# Vérifier les permissions du dossier logs
ls -la ./logs/

# Vérifier que le volume est bien monté
docker inspect faerun-bot | grep -A 10 Mounts
```

## 📊 Monitoring de production

### Healthcheck manuel
```bash
# Le bot expose un endpoint web sur le port 8080
curl http://localhost:8080

# Vérifier que le bot Discord répond
# Utilisez /test dans Discord
```

### Logs structurés
```bash
# Filtrer par niveau de log
docker compose logs | grep ERROR
docker compose logs | grep WARNING
docker compose logs | grep INFO

# Exporter les logs
docker compose logs > bot_logs_export.txt
```

## 🆘 Besoin d'aide ?

- **Discord ne répond pas** : Vérifiez `docker compose logs` pour les erreurs de token
- **Commandes manquantes** : Assurez-vous que `GUILD_ID` est défini pour une synchro rapide
- **Boutique inactive** : Vérifiez que votre Google Sheet est public et que l'ID est correct
- **Problèmes de mise à jour** : Faites `docker compose down && docker compose build --no-cache && docker compose up -d`

---

**Bon jeu dans les Royaumes Oubliés ! 🐉**

*Version : 2.0 - Mise à jour septembre 2025*