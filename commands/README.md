# Bot Discord Faerûn 🏰

Un bot Discord spécialisé pour les campagnes de Donjons & Dragons dans l'univers des Royaumes Oubliés (Forgotten Realms), avec conversion du calendrier réel vers le calendrier de Harptos de Faerûn.

## 🌟 Fonctionnalités

### 📅 Calendrier de Faerûn
- **Conversion automatique** du calendrier grégorien vers le calendrier de Harptos
- **Affichage des festivals** de Faerûn (Midwinter, Greengrass, Midsummer, etc.)
- **Calcul des saisons** et semaines faerûniennes
- **Support des années bissextiles** avec Shieldmeet

### 🎲 Gestion JDR
- **Suivi des quêtes** avec dates automatiques
- **Système de mentions** pour récompenses
- **Statistiques des joueurs** et participation
- **Recherche intelligente** dans les historiques

### 🛠️ Commandes disponibles

| Commande | Description |
|----------|-------------|
| `/faerun` | Affiche la date Faerûnienne actuelle |
| `/faeruncomplet` | Informations complètes (date, saison, semaine, année DR) |
| `/faerunfestival` | Prochain festival de Faerûn |
| `/faerunjdr [date]` | Convertit une date (JJ-MM-AAAA) en calendrier Faerûn |
| `/mesquetes [membre]` | Liste les quêtes futures d'un joueur |
| `/mentionsomeone [membre]` | Compte les mentions dans #recompenses (30j) |
| `/mentionlist` | Statistiques de mentions pour tous les actifs du salon |
| `/recapmj [membre]` | Messages multi-mentions d'un MJ dans #recompenses |
| `/test` | Test de fonctionnement du bot |
| `/info` | Informations sur le bot |

## 🚀 Installation

### Prérequis
- Python 3.11+
- Un bot Discord créé sur le [Discord Developer Portal](https://discord.com/developers/applications)

### Configuration

1. **Cloner le repository**
```bash
git clone <votre-repo>
cd faerun-discord-bot
```

2. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

3. **Variables d'environnement**
Créez un fichier `.env` avec :
```env
DISCORD_TOKEN=votre_token_discord
CLIENT_ID=votre_client_id
GUILD_ID=id_de_votre_serveur_discord  # Optionnel pour sync rapide
```

4. **Lancer le bot**
```bash
python main.py
```

## ⚙️ Configuration avancée

### Structure du projet
```
faerun-discord-bot/
├── main.py                 # Point d'entrée
├── faerunbot.py            # Classe principale du bot
├── config.py               # Configuration et variables
├── calendar_faerun.py      # Logique calendrier Faerûn
├── webserver.py            # Serveur web optionnel
├── commands/               # Modules de commandes
│   ├── __init__.py
│   ├── base.py            # Classe de base
│   ├── faerun.py          # Commandes calendrier
│   ├── mentions.py        # Gestion mentions/récompenses  
│   ├── quetes.py          # Gestion des quêtes
│   ├── info.py            # Informations bot
│   └── test.py            # Commande test
└── requirements.txt
```

### Calendrier de Harptos

Le bot utilise le calendrier officiel de Faerûn avec une logique de conversion basée sur [faerun-date](https://github.com/Cantilux/faerun-date/tree/master) :

**Mois (30 jours chacun) :**
1. Hammer (Hiver)
2. Alturiak (Hiver) 
3. Ches (Hiver)
4. Tarsakh (Printemps)
5. Mirtul (Printemps)
6. Kythorn (Printemps)
7. Flamerule (Été)
8. Eleasis (Été)
9. Eleint (Été)
10. Marpenoth (Automne)
11. Uktar (Automne)
12. Nightal (Automne)

**Festivals spéciaux :**
- **Midwinter** (après Hammer)
- **Greengrass** (après Tarsakh)
- **Midsummer** (après Flamerule)
- **Highharvestide** (après Eleint)
- **Feast of the Moon** (après Marpenoth)
- **Shieldmeet** (années bissextiles, après Midsummer)

**Jours de la semaine (cycle de 10 jours) :**
Sul, Far, Tar, Sar, Rai, Zor, Kyth, Hamar, Ith, Alt

## 🔧 Commandes d'administration

Le bot inclut des commandes spéciales pour les administrateurs :

- `!sync_bot` : Synchronise les commandes slash
- `!debug_bot` : Affiche les informations de debug
- `!reload_commands` : Recharge les commandes à chaud

## 🎯 Canaux spécialisés

Le bot est optimisé pour certains canaux :
- `#recompenses` : Suivi des mentions et récompenses
- `#départ-à-l-aventure` : Planification des quêtes

## 📱 Déploiement

### Replit (recommandé)
Le projet est configuré pour Replit avec :
- Configuration automatique Python 3.11
- Variables d'environnement intégrées
- Déploiement sur Google Cloud Run

### Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

### Serveur traditionnel
```bash
# Avec systemd
sudo cp faerun-bot.service /etc/systemd/system/
sudo systemctl enable faerun-bot
sudo systemctl start faerun-bot
```

## 🐛 Dépannage

### Problèmes courants

**Le bot ne répond pas aux commandes**
- Vérifiez que `DISCORD_TOKEN` est correct
- Utilisez `!sync_bot` pour synchroniser les commandes
- Vérifiez les permissions du bot sur le serveur

**Erreurs de calendrier**
- Le bot utilise UTC par défaut
- Vérifiez le format de date : JJ-MM-AAAA

**Commandes manquantes**
- Utilisez `!debug_bot` pour voir l'état
- Rechargez avec `!reload_commands`

### Logs
Le bot utilise le logging Python standard :
```python
# Dans config.py, modifiez le niveau
LOG_LEVEL = logging.DEBUG  # Pour plus de détails
```

## 🤝 Contribution

1. Fork le projet
2. Créez une branche feature (`git checkout -b feature/AmazingFeature`)
3. Commit vos changements (`git commit -m 'Add AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

### Ajouter une commande

1. Créez un fichier dans `commands/`
2. Héritez de `BaseCommand`
3. Ajoutez à `commands/__init__.py`

```python
from .base import BaseCommand
import discord

class MaCommande(BaseCommand):
    @property
    def name(self) -> str:
        return "macommande"

    @property 
    def description(self) -> str:
        return "Description de ma commande"

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message("Hello!", ephemeral=True)
```

## 📄 Licence

Ce projet est sous licence MIT. Voir `LICENSE` pour plus de détails.

## 📚 Ressources

- [Discord.py Documentation](https://discordpy.readthedocs.io/)
- [Forgotten Realms Wiki](https://forgottenrealms.fandom.com/)
- [Calendrier de Harptos](https://forgottenrealms.fandom.com/wiki/Calendar_of_Harptos)
- [faerun-date](https://github.com/Cantilux/faerun-date/tree/master) - Logique de conversion du calendrier utilisée

## 🙏 Remerciements

- [Cantilux/faerun-date](https://github.com/Cantilux/faerun-date/tree/master) pour la logique de conversion du calendrier Faerûn

---

*Créé avec ❤️ pour les aventuriers des Royaumes Oubliés*