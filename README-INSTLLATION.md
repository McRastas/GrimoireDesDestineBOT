# 🚀 Installation du Bot Discord Faerûn

Ce guide vous explique comment installer et déployer le Bot Faerûn sur votre serveur Linux avec deux méthodes principales.

## 📋 Prérequis

- **Serveur Linux** (Ubuntu 20.04+ / Debian 11+ / CentOS 8+ recommandé)
- **Accès root ou sudo**
- **Connexion Internet**
- **Token Discord** et **Client ID** de votre bot

### 🔑 Obtenir les Tokens Discord

1. Allez sur le [Discord Developer Portal](https://discord.com/developers/applications)
2. Créez une nouvelle application
3. Dans l'onglet "Bot" :
   - Créez un bot
   - Copiez le **Token** (gardez-le secret !)
4. Dans l'onglet "General Information" :
   - Copiez l'**Application ID** (Client ID)

---

## 🐳 Méthode 1 : Installation avec Docker (Recommandée)

Docker simplifie le déploiement et évite les conflits de dépendances.

### 📦 1. Installation de Docker

#### Ubuntu/Debian
```bash
# Mise à jour du système
sudo apt update && sudo apt upgrade -y

# Installation de Docker
sudo apt install -y apt-transport-https ca-certificates curl gnupg lsb-release
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Démarrer Docker
sudo systemctl enable docker
sudo systemctl start docker

# Ajouter votre utilisateur au groupe docker
sudo usermod -aG docker $USER
newgrp docker
```

#### CentOS/RHEL/Rocky Linux
```bash
# Installation de Docker
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo yum install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Démarrer Docker
sudo systemctl enable docker
sudo systemctl start docker

# Ajouter votre utilisateur au groupe docker
sudo usermod -aG docker $USER
newgrp docker
```

### 🔧 2. Configuration du Bot

```bash
# Créer le dossier du bot
mkdir -p ~/faerun-bot
cd ~/faerun-bot

# Télécharger les fichiers du bot (remplacez par votre méthode)
# Option A: Git
git clone https://github.com/votre-username/faerun-bot.git .

# Option B: Téléchargement direct
# wget https://github.com/votre-username/faerun-bot/archive/main.zip
# unzip main.zip && mv faerun-bot-main/* . && rm -rf faerun-bot-main main.zip
```

### 📝 3. Configuration des Variables

```bash
# Créer le fichier de configuration
cat > .env << 'EOF'
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
CHANNELS_CONFIG={"recompenses":{"name":"recompenses"},"quetes":{"name":"départ-à-l-aventure"},"logs":{"name":"bot-logs"},"admin":{"name":"bot-admin"}}

# Web Server (OPTIONNEL)
FLASK_HOST=0.0.0.0
FLASK_PORT=8080
EOF

# Éditer le fichier avec vos vraies valeurs
nano .env
```

### 🐋 4. Fichiers Docker

#### Dockerfile
```bash
cat > Dockerfile << 'EOF'
FROM python:3.11-slim

# Métadonnées
LABEL maintainer="votre-email@example.com"
LABEL description="Bot Discord Faerûn - Calendrier D&D"

# Variables d'environnement Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Répertoire de travail
WORKDIR /app

# Installation des dépendances système
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copier et installer les dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copier le code de l'application
COPY . .

# Créer un utilisateur non-root
RUN groupadd -r botuser && useradd --no-log-init -r -g botuser botuser
RUN chown -R botuser:botuser /app
USER botuser

# Port exposé (pour le serveur web optionnel)
EXPOSE 8080

# Commande de démarrage
CMD ["python", "main.py"]
EOF
```

#### docker-compose.yml
```bash
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  faerun-bot:
    build: .
    container_name: faerun-bot
    restart: unless-stopped

    # Variables d'environnement (chargées depuis .env)
    env_file:
      - .env

    # Ports (optionnel - pour le serveur web)
    ports:
      - "8080:8080"

    # Volumes pour la persistance (optionnel)
    volumes:
      - ./logs:/app/logs

    # Santé du conteneur
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:8080/health')"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

# Réseau (optionnel)
networks:
  default:
    driver: bridge
EOF
```

### 🚀 5. Déploiement avec Docker

```bash
# Construction et démarrage du bot
docker-compose up -d

# Vérifier que le bot fonctionne
docker-compose logs -f

# Commandes utiles
docker-compose ps                 # Voir le statut
docker-compose restart            # Redémarrer
docker-compose down               # Arrêter
docker-compose pull && docker-compose up -d  # Mise à jour
```

### 📊 6. Monitoring Docker

```bash
# Voir les logs en temps réel
docker-compose logs -f

# Voir les logs des dernières 100 lignes
docker-compose logs --tail=100

# Statistiques d'utilisation
docker stats faerun-bot

# Inspecter le conteneur
docker inspect faerun-bot
```

---

## 🐍 Méthode 2 : Installation Native Python

Installation directe sur le système avec Python et systemd.

### 🔧 1. Installation des Prérequis

#### Ubuntu/Debian
```bash
# Mise à jour du système
sudo apt update && sudo apt upgrade -y

# Installation de Python et outils
sudo apt install -y python3 python3-pip python3-venv git curl wget nano

# Vérifier la version Python (3.11+ recommandé)
python3 --version
```

#### CentOS/RHEL/Rocky Linux
```bash
# Mise à jour du système
sudo yum update -y

# Installation de Python et outils
sudo yum install -y python3 python3-pip git curl wget nano

# Vérifier la version Python
python3 --version
```

### 📁 2. Préparation de l'Environnement

```bash
# Créer un utilisateur dédié (sécurité)
sudo useradd -m -s /bin/bash faerunbot
sudo su - faerunbot

# Créer le dossier du bot
mkdir -p ~/faerun-bot
cd ~/faerun-bot

# Télécharger le code du bot
git clone https://github.com/votre-username/faerun-bot.git .

# Créer un environnement virtuel Python
python3 -m venv venv
source venv/bin/activate

# Installer les dépendances
pip install --upgrade pip
pip install -r requirements.txt
```

### 📝 3. Configuration

```bash
# Créer le fichier de configuration
cat > .env << 'EOF'
# =================================
# CONFIGURATION BOT FAERÛN
# =================================

# Discord (OBLIGATOIRE - remplacez par vos vraies valeurs)
DISCORD_TOKEN=votre_token_discord_ici
CLIENT_ID=votre_client_id_ici

# Serveur Discord (OPTIONNEL)
GUILD_ID=votre_guild_id_pour_sync_rapide
ADMIN_ROLE_NAME=Façonneur

# Configuration des canaux
CHANNELS_CONFIG={"recompenses":{"name":"recompenses"},"quetes":{"name":"départ-à-l-aventure"},"logs":{"name":"bot-logs"},"admin":{"name":"bot-admin"}}

# Web Server
FLASK_HOST=0.0.0.0
FLASK_PORT=8080
EOF

# Éditer avec vos vraies valeurs
nano .env

# Sécuriser le fichier de configuration
chmod 600 .env
```

### 🧪 4. Test du Bot

```bash
# Activer l'environnement virtuel
source venv/bin/activate

# Tester le bot
python main.py

# Si tout fonctionne, arrêter avec Ctrl+C
```

### ⚙️ 5. Configuration Systemd (Auto-démarrage)

```bash
# Revenir en utilisateur root/sudo
exit

# Créer le service systemd
sudo tee /etc/systemd/system/faerun-bot.service > /dev/null << 'EOF'
[Unit]
Description=Bot Discord Faerûn - Calendrier D&D
After=network.target
Wants=network.target

[Service]
Type=simple
User=faerunbot
Group=faerunbot
WorkingDirectory=/home/faerunbot/faerun-bot
Environment=PATH=/home/faerunbot/faerun-bot/venv/bin
ExecStart=/home/faerunbot/faerun-bot/venv/bin/python main.py
ExecReload=/bin/kill -HUP $MAINPID
Restart=always
RestartSec=5

# Chargement automatique du fichier .env
EnvironmentFile=/home/faerunbot/faerun-bot/.env

# Sécurité
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/home/faerunbot/faerun-bot/logs

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=faerun-bot

[Install]
WantedBy=multi-user.target
EOF

# Recharger systemd
sudo systemctl daemon-reload

# Activer le service (démarrage automatique)
sudo systemctl enable faerun-bot.service

# Démarrer le service
sudo systemctl start faerun-bot.service
```

### 📊 6. Gestion du Service

```bash
# Vérifier le statut
sudo systemctl status faerun-bot.service

# Voir les logs
sudo journalctl -u faerun-bot.service -f

# Redémarrer le bot
sudo systemctl restart faerun-bot.service

# Arrêter le bot
sudo systemctl stop faerun-bot.service

# Désactiver le démarrage automatique
sudo systemctl disable faerun-bot.service

# Voir les logs des erreurs
sudo journalctl -u faerun-bot.service --since "1 hour ago" -p err
```

### 🔄 7. Script de Mise à Jour

```bash
# Créer un script de mise à jour
sudo tee /home/faerunbot/update-bot.sh > /dev/null << 'EOF'
#!/bin/bash

echo "🔄 Mise à jour du Bot Faerûn..."

# Aller dans le dossier du bot
cd /home/faerunbot/faerun-bot

# Sauvegarder la configuration
cp .env .env.backup

# Arrêter le bot
sudo systemctl stop faerun-bot.service

# Mettre à jour le code
git pull origin main

# Activer l'environnement virtuel
source venv/bin/activate

# Mettre à jour les dépendances
pip install --upgrade -r requirements.txt

# Restaurer la configuration
cp .env.backup .env

# Redémarrer le bot
sudo systemctl start faerun-bot.service

# Vérifier le statut
sleep 5
sudo systemctl status faerun-bot.service

echo "✅ Mise à jour terminée !"
EOF

# Rendre le script exécutable
sudo chmod +x /home/faerunbot/update-bot.sh
sudo chown faerunbot:faerunbot /home/faerunbot/update-bot.sh

# Utilisation : sudo /home/faerunbot/update-bot.sh
```

---

## 🔧 Configuration Post-Installation

### 🧪 1. Tester la Configuration

Une fois le bot démarré, testez la configuration :

```bash
# Dans Discord, utilisez ces commandes :
/test
/config-channels action:test
/config-channels action:suggest
/faerun
```

### 📊 2. Monitoring et Logs

#### Pour Docker :
```bash
# Logs en temps réel
docker-compose logs -f

# Statistiques
docker stats faerun-bot
```

#### Pour Installation Native :
```bash
# Logs systemd
sudo journalctl -u faerun-bot.service -f

# Statistiques système
htop
ps aux | grep python
```

### 🔒 3. Sécurité

```bash
# Configurer le pare-feu (si nécessaire pour le serveur web)
sudo ufw allow 8080/tcp

# Vérifier les permissions
ls -la .env  # Doit être 600
sudo systemctl show faerun-bot.service -p User  # Doit être faerunbot
```

### 🔄 4. Sauvegarde

```bash
# Sauvegarder la configuration
cp .env config-backup-$(date +%Y%m%d).env

# Pour Docker : sauvegarder les volumes
docker-compose down
tar -czf faerun-backup-$(date +%Y%m%d).tar.gz .

# Pour installation native : sauvegarder le dossier
tar -czf /tmp/faerun-backup-$(date +%Y%m%d).tar.gz /home/faerunbot/faerun-bot
```

---

## 🆘 Dépannage

### ❌ Problèmes Courants

#### Le bot ne démarre pas
```bash
# Vérifier les logs
docker-compose logs  # Docker
sudo journalctl -u faerun-bot.service -n 50  # Native

# Vérifier la configuration
cat .env | grep -v "^#" | grep -v "^$"

# Tester manuellement
python main.py  # Native
docker-compose exec faerun-bot python main.py  # Docker
```

#### Erreurs de permissions
```bash
# Docker : vérifier les volumes
docker-compose down
sudo chown -R $USER:$USER .

# Native : vérifier le propriétaire
sudo chown -R faerunbot:faerunbot /home/faerunbot/faerun-bot
```

#### Bot ne répond pas aux commandes
```bash
# Synchroniser les commandes dans Discord
# Utilisez la commande : !sync_bot

# Vérifier les permissions Discord du bot
# Le bot doit avoir : "Send Messages", "Use Slash Commands"
```

### 🔍 Commandes de Diagnostic

```bash
# Vérifier la connectivité réseau
curl -I https://discord.com

# Vérifier les variables d'environnement
env | grep DISCORD
env | grep CHANNEL

# Tester la configuration des canaux
# Dans Discord : /config-channels action:test
```

---

## 📞 Support

Si vous rencontrez des problèmes :

1. **Vérifiez les logs** d'abord
2. **Testez la configuration** avec `/config-channels action:test`
3. **Consultez la documentation** Discord.py
4. **Vérifiez les permissions** du bot sur Discord

---

## 🎯 Comparaison des Méthodes

| Critère | Docker | Native Python |
|---------|--------|---------------|
| **Facilité** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Isolation** | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| **Performance** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Mise à jour** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Debugging** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Production** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

**Recommandation** : Utilisez **Docker** pour la production et **Python natif** pour le développement.

---

*🏰 Que votre bot guide les aventuriers à travers les Royaumes Oubliés !*