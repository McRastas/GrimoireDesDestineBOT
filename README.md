# Bot Discord Faerûn 🏰

Un bot Discord spécialisé pour vos campagnes de Donjons & Dragons dans l'univers des Royaumes Oubliés (Forgotten Realms). Transformez votre serveur Discord en véritable table de jeu avec le calendrier de Harptos, la gestion des quêtes et bien plus !

## 🌟 Ce que fait le bot

- 📅 **Calendrier Faerûnien** - Convertit les dates réelles en calendrier de Harptos avec festivals
- 🎯 **Gestion des quêtes** - Trouve automatiquement vos prochaines sessions dans vos messages
- 📊 **Suivi des récompenses** - Compte vos mentions dans le canal récompenses
- 🎭 **Générateur de PNJ** - Crée des personnages non-joueurs détaillés instantanément
- ❓ **Guide interactif** - Aide personnalisée selon vos permissions

## 🛠️ Toutes les commandes

### 📅 Calendrier de Faerûn

**`/faerun`** - Date Faerûnienne d'aujourd'hui
> Affiche la date actuelle dans le calendrier de Harptos avec saison et semaine

**`/faeruncomplet`** - Informations complètes
> Date, saison, semaine, année DR - toutes les infos d'un coup

**`/faerunfestival`** - Prochain festival
> Découvrez le prochain festival de Faerûn (Midwinter, Greengrass, etc.)

**`/faerunjdr 25-12-2024`** - Convertir une date
> Transforme n'importe quelle date en équivalent Faerûnien

### 🎯 Vos quêtes et sessions

**`/mesquetes`** - Mes prochaines quêtes
> Liste vos quêtes futures avec détection automatique des dates

**`/mesquetes @Joueur`** - Quêtes d'un autre joueur
> Voir les quêtes d'un coéquipier

**Formats de dates détectés automatiquement :**
- `28/06`, `28-06`, `28.06` (année automatique)
- `28/06/2025`, `28-06-2025` (année complète)
- `28 juin`, `28 june 2025` (en toutes lettres)
- `le 28/06`, `28/06 à 14h30` (langage naturel)

### 📊 Vos récompenses et mentions

**`/mentionsomeone`** - Mes mentions
> Compte combien de fois vous avez été mentionné dans #récompenses (30 derniers jours)

**`/mentionsomeone @Joueur`** - Mentions d'un joueur
> Voir les mentions et récompenses d'un autre joueur

**`/mentionlist`** - Classement du canal
> Statistiques de mentions pour tous les actifs de ce canal

**`/recapmj @MJ`** - Sessions de récompenses d'un MJ
> Voir tous les messages où le MJ a récompensé plusieurs joueurs à la fois

### 🎭 Création de personnages

**`/pnj-generator`** - PNJ aléatoire complet
> Génère un personnage non-joueur avec apparence, personnalité et secrets

**Options disponibles :**
- **Types :** Marchand, Noble, Garde, Aubergiste, Prêtre, Voleur, Artisan, Paysan, Aventurier, Mage
- **Genres :** Masculin, Féminin, Aléatoire
- **Races :** Humain, Elfe, Nain, Halfelin, Demi-Elfe, Tieffelin, Aléatoire

**Exemple :** `/pnj-generator type:marchand genre:féminin race:elfe`

### ⚙️ Utilitaires

**`/help`** - Guide d'utilisation
> Aide complète adaptée à vos permissions (plus de détails si vous êtes admin)

**`/test`** - Vérifier le bot
> S'assurer que le bot fonctionne correctement

**`/info`** - Statistiques du bot
> Nombre de serveurs, utilisateurs et commandes

## 🎲 Comment bien utiliser le bot

### Pour les joueurs

1. **Avant chaque session :** Utilisez `/faerun` pour connaître la date dans votre campagne
2. **Planification :** Tapez `/mesquetes` pour voir vos prochaines aventures
3. **Récompenses :** Vérifiez vos mentions avec `/mentionsomeone`
4. **Roleplay :** Générez des PNJ avec `/pnj-generator` pour enrichir vos interactions

### Pour les MJ

1. **Immersion :** Annoncez la date Faerûnienne avec `/faeruncomplet`
2. **Suivi des joueurs :** Utilisez `/mesquetes @Joueur` pour voir qui vient quand
3. **Récompenses :** Surveillez l'engagement avec `/mentionlist`
4. **Création :** Générez des PNJ rapidement pendant vos sessions
5. **Administration :** Des commandes spéciales sont disponibles si vous avez le rôle "Façonneur"

## 📅 Le calendrier de Faerûn expliqué

### Les 12 mois (30 jours chacun)
- **Hammer** (Hiver) - Le Marteau
- **Alturiak** (Hiver) - La Griffe de l'Hiver  
- **Ches** (Hiver) - Les Couchers du Soleil
- **Tarsakh** (Printemps) - Les Tempêtes
- **Mirtul** (Printemps) - Le Dégel
- **Kythorn** (Printemps) - L'Heure des Fleurs
- **Flamerule** (Été) - Le Temps des Flammes
- **Eleasis** (Été) - Les Hautes Chaleurs
- **Eleint** (Été) - Les Précipitations
- **Marpenoth** (Automne) - Le Fanage des Feuilles
- **Uktar** (Automne) - Le Pourrissement
- **Nightal** (Automne) - Le Soleil Descendant

### Les festivals spéciaux
- **Midwinter** - Plein Hiver (après Hammer)
- **Greengrass** - Herbe Verte (après Tarsakh)
- **Midsummer** - Solstice d'Été (après Flamerule)
- **Highharvestide** - Hautes Moissons (après Eleint)
- **Feast of the Moon** - Fête de la Lune (après Marpenoth)
- **Shieldmeet** - Rencontre des Boucliers (années bissextiles seulement)

## 💡 Astuces et conseils

### Détection automatique des dates
Le bot comprend une multitude de formats de dates dans vos messages :
- Dates françaises : `28/06`, `28 juin 2025`
- Dates anglaises : `28 june`, `june 28th`
- Formats naturels : `le 28/06 à 20h`, `demain`, `la semaine prochaine`

### Optimisation pour votre serveur
- Le bot fonctionne mieux avec des canaux dédiés (#récompenses, #départ-à-l-aventure)
- Les commandes s'adaptent automatiquement à votre configuration
- Utilisez `/help` pour voir exactement ce qui est disponible selon vos permissions

## 🎮 Exemples concrets

**Situation :** "Nous sommes le 15 février 2024, quelle date sommes-nous en Faerûn ?"
→ Tapez `/faerunjdr 15-02-2024`

**Situation :** "Quand est ma prochaine session ?"
→ Tapez `/mesquetes` (le bot analysera automatiquement vos messages)

**Situation :** "J'ai besoin d'un marchand elfe pour mon RP"
→ Tapez `/pnj-generator type:marchand race:elfe`

**Situation :** "Combien de fois ai-je été récompensé ce mois-ci ?"
→ Tapez `/mentionsomeone` dans n'importe quel canal

---

## 📞 Besoin d'aide ?

- **Guide complet :** Utilisez `/help` dans Discord
- **Test du bot :** Tapez `/test` pour vérifier que tout fonctionne
- **Installation :** Consultez `README-INSTALLATION.md` pour installer votre propre instance

*Bon jeu dans les Royaumes Oubliés ! 🐉*
