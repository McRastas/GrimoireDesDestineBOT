# Bot Discord Faerûn 🏰

Un bot Discord spécialisé pour les campagnes de Donjons & Dragons dans l'univers des Royaumes Oubliés (Forgotten Realms), avec conversion du calendrier réel vers le calendrier de Harptos de Faerûn.

## 🌟 Fonctionnalités

### 📅 Calendrier de Faerûn
- **Conversion automatique** du calendrier grégorien vers le calendrier de Harptos
- **Affichage des festivals** de Faerûn (Midwinter, Greengrass, Midsummer, etc.)
- **Calcul des saisons** et semaines faerûniennes
- **Support des années bissextiles** avec Shieldmeet

### 🎯 Gestion des Quêtes
- **Détection intelligente des dates** avec support de multiples formats
- **Logique d'année automatique** pour les dates sans année
- **Classification par urgence** : aujourd'hui, demain, cette semaine, plus tard
- **Liens cliquables** vers les messages originaux

### 📊 Système de Mentions et Récompenses
- **Suivi des mentions** dans le canal #recompenses
- **Statistiques détaillées** avec liens vers les messages
- **Classements** et analyses de participation
- **Gestion des récompenses multi-joueurs**

### 🎭 Générateur de PNJ
- **Création aléatoire** de personnages non-joueurs
- **10 types de PNJ** : marchands, nobles, gardes, aubergistes, etc.
- **Personnalisation** par race et genre
- **Détails complets** : apparence, personnalité, secrets

## 🛠️ Commandes disponibles

### 📅 Calendrier Faerûn
| Commande | Description | Exemple |
|----------|-------------|---------|
| `/faerun` | Date Faerûnienne actuelle | Simple et rapide |
| `/faeruncomplet` | Informations complètes (date, saison, semaine, année DR) | Vue détaillée |
| `/faerunfestival` | Prochain festival de Faerûn | Planification d'événements |
| `/faerunjdr [date]` | Convertit une date (JJ-MM-AAAA) en calendrier Faerûn | `/faerunjdr 15-02-2023` |

### 🎯 Gestion des Quêtes
| Commande | Description | Exemple |
|----------|-------------|---------|
| `/mesquetes [membre]` | Liste les quêtes futures d'un joueur avec détection intelligente des dates | `/mesquetes @Aventurier` |

**Formats de dates supportés :**
- `28/06`, `28-06`, `28.06` (année automatique)
- `28/06/2025`, `28-06-2025` (année explicite)
- `28 juin`, `28 june 2025` (formats textuels)
- `le 28/06`, `28/06 à 14h30` (formats naturels)

### 📊 Mentions et Statistiques
| Commande | Description | Exemple |
|----------|-------------|---------|
| `/mentionsomeone [membre]` | Compte et liste les mentions dans #recompenses avec liens | `/mentionsomeone @Joueur` |
| `/mentionlist` | Statistiques de mentions pour tous les actifs du salon | Classement global |
| `/recapmj [membre]` | Messages multi-mentions d'un MJ avec détails | `/recapmj @MJ` |

### 🎭 Générateur de Contenu
| Commande | Description | Options |
|----------|-------------|---------|
| `/pnj-generator` | Génère un PNJ aléatoire | Type, genre, race personnalisables |

### ⚙️ Utilitaires
| Commande | Description |
|----------|-------------|
| `/test` | Test de fonctionnement du bot |
| `/info` | Informations sur le bot (serveurs, utilisateurs, commandes) |

## 🚀 Installation

### Prérequis
- **Python 3.11+**
- Un bot Discord créé sur le [Discord Developer Portal](https://discord.com/developers/applications)
- Permissions Discord appropriées pour le bot

### Configuration rapide

1. **Cloner le repository**
```bash
git clone <votre-repo>
cd faerun-discord-bot
```

2. **Installer les dépendances**
```bash
pip install -r requirements.txt
# ou avec uv
uv pip install -r requirements.txt
```

3. **Variables d'environnement**
Créez un fichier `.env` avec :
```env
DISCORD_TOKEN=votre_token_discord_ici
CLIENT_ID=votre_client_id_ici
GUILD_ID=id_de_votre_serveur_discord  # Optionnel pour sync rapide
ADMIN_ROLE_NAME=Façonneur              # Rôle admin (par défaut)
```

4. **Lancer le bot**
```bash
python main.py
```

## ⚙️ Configuration avancée

### Structure du projet (nouvelle architecture modulaire)
```
faerun-discord-bot/
├── main.py                    # Point d'entrée
├── faerunbot.py               # Classe principale du bot
├── config.py                  # Configuration et variables
├── calendar_faerun.py         # Logique calendrier Faerûn
├── webserver.py               # Serveur web optionnel
├── utils/
│   └── permissions.py         # Gestion des permissions
├── commands/                  # Modules de commandes (architecture modulaire)
│   ├── __init__.py
│   ├── base.py               # Classe de base pour toutes les commandes
│   ├── faerun_date.py        # Commande /faerun
│   ├── faerun_festival.py    # Commande /faerunfestival
│   ├── faerun_complet.py     # Commande /faeruncomplet
│   ├── faerun_jdr.py         # Commande /faerunjdr
│   ├── mention_someone.py    # Commande /mentionsomeone
│   ├── mention_list.py       # Commande /mentionlist
│   ├── recap_mj.py           # Commande /recapmj
│   ├── mes_quetes.py         # Commande /mesquetes
│   ├── pnj_generator.py      # Générateur PNJ
│   ├── info.py               # Informations bot
│   └── test.py               # Commande test
└── requirements.txt
```

### Calendrier de Harptos

Le bot utilise le calendrier officiel de Faerûn basé sur [faerun-date](https://github.com/Cantilux/faerun-date/tree/master) :

**Mois (30 jours chacun) :**
1. **Hammer** (Hiver) - *Le Marteau*
2. **Alturiak** (Hiver) - *La Griffe de l'Hiver*
3. **Ches** (Hiver) - *Les Couchers du Soleil*
4. **Tarsakh** (Printemps) - *Les Tempêtes*
5. **Mirtul** (Printemps) - *Le Dégel*
6. **Kythorn** (Printemps) - *L'Heure des Fleurs*
7. **Flamerule** (Été) - *Le Temps des Flammes*
8. **Eleasis** (Été) - *Les Hautes Chaleurs*
9. **Eleint** (Été) - *Les Précipitations*
10. **Marpenoth** (Automne) - *Le Fanage des Feuilles*
11. **Uktar** (Automne) - *Le Pourrissement*
12. **Nightal** (Automne) - *Le Soleil Descendant*

**Festivals spéciaux :**
- **Midwinter** (après Hammer) - Plein Hiver
- **Greengrass** (après Tarsakh) - Herbe Verte
- **Midsummer** (après Flamerule) - Solstice d'Été
- **Highharvestide** (après Eleint) - Jour des Hautes Moissons
- **Feast of the Moon** (après Marpenoth) - Fête de la Lune
- **Shieldmeet** (années bissextiles, après Midsummer) - Rencontre des Boucliers

## 🔧 Commandes d'administration

Le bot inclut des commandes spéciales pour les administrateurs (rôle configuré) :

- `!sync_bot` : Synchronise les commandes slash sur le serveur
- `!debug_bot` : Affiche les informations de debug du bot
- `!reload_commands` : Recharge les commandes à chaud sans redémarrer

**Permissions requises :** Rôle "Façonneur" (configurable) ou Administrateur du serveur

## 🎯 Canaux spécialisés

Le bot est optimisé pour certains canaux Discord :
- **`#recompenses`** : Suivi des mentions et récompenses de joueurs
- **`#départ-à-l-aventure`** : Planification des quêtes et sessions

## 📱 Déploiement

### Replit (recommandé pour débutants)
Le projet est pré-configuré pour Replit :
- Configuration automatique Python 3.11
- Variables d'environnement intégrées
- Déploiement possible sur Google Cloud Run

### Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

### Serveur Linux (systemd)
```bash
# Copier le service
sudo cp faerun-bot.service /etc/systemd/system/
sudo systemctl enable faerun-bot
sudo systemctl start faerun-bot
sudo systemctl status faerun-bot
```

## 🐛 Dépannage

### Problèmes courants

**❌ Le bot ne répond pas aux commandes**
- Vérifiez que `DISCORD_TOKEN` est correct et valide
- Utilisez `!sync_bot` pour synchroniser les commandes slash
- Vérifiez les permissions du bot sur le serveur (lecture messages, slash commands)

**❌ Erreurs de calendrier ou dates**
- Le bot utilise UTC par défaut
- Format de date requis : `JJ-MM-AAAA` pour `/faerunjdr`
- Les autres commandes supportent de multiples formats automatiquement

**❌ Commandes manquantes ou non synchronisées**
- Utilisez `!debug_bot` pour voir l'état du bot
- Rechargez avec `!reload_commands` si nécessaire
- Vérifiez que vous avez le rôle admin configuré

**❌ Erreurs de permissions**
- Vérifiez que le rôle `ADMIN_ROLE_NAME` existe sur le serveur
- Les administrateurs du serveur ont automatiquement accès

### Logs et debugging
Le bot utilise le logging Python standard. Pour plus de détails :
```python
# Dans config.py, modifiez le niveau
LOG_LEVEL = logging.DEBUG  # Pour plus de détails
```

## 🤝 Contribution

### Ajouter une nouvelle commande

Grâce à l'architecture modulaire, ajouter une commande est simple :

1. **Créer un fichier** dans `commands/` (ex: `ma_commande.py`)
2. **Hériter de BaseCommand** et implémenter les méthodes requises
3. **Ajouter à** `commands/__init__.py`

```python
# commands/ma_commande.py
"""
Commande Discord : /macommande

DESCRIPTION:
    Description de ce que fait la commande

FONCTIONNEMENT:
    - Comment elle fonctionne
    - Paramètres acceptés
    - Logique métier

UTILISATION:
    /macommande parametre:valeur
"""

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
        await interaction.response.send_message("Hello World!", ephemeral=True)
```

### Standards de contribution
1. **Fork** le projet
2. **Créez une branche** feature (`git checkout -b feature/AmazingFeature`)
3. **Documentez** votre commande avec le format de cartouche
4. **Testez** votre commande localement
5. **Commit** vos changements (`git commit -m 'Add AmazingFeature'`)
6. **Push** vers la branche (`git push origin feature/AmazingFeature`)
7. **Ouvrez une Pull Request**

## 📄 Licence

Ce projet est sous licence MIT. Voir `LICENSE` pour plus de détails.

## 📚 Ressources

### Documentation technique
- [Discord.py Documentation](https://discordpy.readthedocs.io/) - API Discord Python
- [Discord Developer Portal](https://discord.com/developers/docs/) - Documentation officielle Discord

### Univers D&D / Faerûn
- [Forgotten Realms Wiki](https://forgottenrealms.fandom.com/) - Wiki officiel des Royaumes Oubliés
- [Calendrier de Harptos](https://forgottenrealms.fandom.com/wiki/Calendar_of_Harptos) - Documentation du calendrier

### Ressources de développement
- [faerun-date](https://github.com/Cantilux/faerun-date/tree/master) - Logique de conversion du calendrier utilisée

## 🙏 Remerciements

- **[Cantilux/faerun-date](https://github.com/Cantilux/faerun-date/tree/master)** pour la logique de conversion du calendrier Faerûn
- **Communauté D&D** pour les retours et suggestions d'amélioration
- **Discord.py** pour l'excellente bibliothèque Python

## 🎮 Fonctionnalités à venir

- [ ] Commande `/lance` - Lanceur de dés avancé avec support D&D 5e
- [ ] Commande `/meteo` - Météo Faerûnienne selon les saisons
- [ ] Système de backup automatique des données importantes
- [ ] Interface web pour la gestion des PNJ et quêtes
- [ ] Support multi-langues (français/anglais)

---

*Créé avec ❤️ pour les aventuriers des Royaumes Oubliés*

**Version :** 1.0.0 | **Python :** 3.11+ | **Discord.py :** 2.5.2+