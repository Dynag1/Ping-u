# 🪟 Ping ü - Installation Windows (Mode Application)

Guide d'installation et d'utilisation de Ping ü en mode application de bureau sur Windows.

---

## 📋 Sommaire

1. [Prérequis](#prérequis)
2. [Installation](#installation)
3. [Premier lancement](#premier-lancement)
4. [Interface principale](#interface-principale)
5. [Ajouter des hôtes](#ajouter-des-hôtes)
6. [Démarrer le monitoring](#démarrer-le-monitoring)
7. [Configurer les alertes](#configurer-les-alertes)
8. [Exporter/Importer](#exporterimporter)
9. [Dépannage](#dépannage)

---

## 🔧 Prérequis

| Élément | Requis |
|---------|--------|
| Système | Windows 10/11 (64 bits) |
| RAM | 4 Go minimum |
| Espace disque | 200 Mo |
| Réseau | Connexion réseau active |

---

## 📦 Installation

### Option 1 : Installateur (Recommandé)

1. **Téléchargez** `PingU_Setup.exe` depuis le dossier `installer/`
2. **Exécutez** l'installateur en double-cliquant
3. **Suivez** les étapes de l'assistant d'installation
4. **Terminez** - Un raccourci sera créé sur le bureau

![Installation Windows](../screenshots/windows_install_01.png)
*Écran d'installation de Ping ü*

### Option 2 : Portable (sans installation)

1. **Téléchargez** le dossier `dist/Ping_u/`
2. **Copiez** le dossier où vous le souhaitez
3. **Lancez** `Ping_u.exe`

### Option 3 : Code source (développeurs)

```powershell
# Cloner le dépôt
git clone https://github.com/votre-repo/ping-u.git
cd ping-u

# Créer un environnement virtuel
python -m venv .venv
.\.venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt

# Lancer l'application
python Pingu.py
```

---

## 🚀 Premier lancement

1. **Double-cliquez** sur `Ping_u.exe` ou le raccourci créé
2. L'**interface graphique** s'ouvre

![Premier lancement](../screenshots/windows_app_01_main.png)
*Interface principale de Ping ü*

### Description de l'interface

| Zone | Description |
|------|-------------|
| **Barre de menu** | Accès aux fonctions (Fichier, Paramètres, etc.) |
| **Zone d'ajout** | Ajouter des hôtes manuellement ou par scan |
| **Tableau principal** | Liste des hôtes surveillés |
| **Barre d'état** | Informations sur la licence et version |

---

## ➕ Ajouter des hôtes

### Méthode 1 : Ajout manuel

1. Entrez l'**adresse IP** dans le champ "IP"
2. Définissez le **nombre d'hôtes** (1 pour un seul)
3. Cliquez sur **"Ajouter"**

![Ajout manuel](../screenshots/windows_app_02_add.png)
*Ajout d'un hôte*

### Méthode 2 : Scan de plage

1. Entrez l'**IP de départ** (ex: `192.168.1.1`)
2. Définissez le **nombre d'hôtes** à scanner (ex: 254)
3. Sélectionnez le **filtre** :
   - `Alive` : Seulement les hôtes qui répondent
   - `Tout` : Tous les hôtes (même offline)
   - `Site` : Filtrer par site
4. Cliquez sur **"Ajouter"**

![Scan de plage](../screenshots/windows_app_03_scan.png)
*Scan d'une plage d'adresses*

### Méthode 3 : Import CSV/Excel

1. Menu **Fichier** → **Ouvrir** ou **Importer Excel**
2. Sélectionnez votre fichier
3. Les hôtes sont ajoutés au tableau

---

## ▶️ Démarrer le monitoring

1. Ajoutez des hôtes au tableau
2. Configurez les paramètres :
   - **Délai** : Intervalle entre les pings (en secondes)
   - **Nb HS** : Nombre d'échecs avant alerte
3. Cliquez sur le bouton **"Start"** (vert)

![Monitoring actif](../screenshots/windows_app_04_monitoring.png)
*Monitoring en cours - Le bouton devient rouge "Stop"*

### Lecture du tableau

| Couleur | Signification |
|---------|---------------|
| 🟢 Vert | Hôte en ligne |
| 🟡 Jaune | Latence élevée (>100ms) |
| 🟠 Orange | Latence très élevée (>200ms) |
| 🔴 Rouge | Hôte hors ligne (HS) |

### Colonnes du tableau

| Colonne | Description |
|---------|-------------|
| Id | Identifiant unique |
| IP | Adresse IP de l'hôte |
| Nom | Nom DNS ou personnalisé |
| Mac | Adresse MAC (si disponible) |
| Port | Port surveillé |
| Latence | Temps de réponse (ms) |
| Temp | Température (SNMP) |
| Suivi | Statut de suivi |
| Comm | Commentaire |
| Excl | Exclusion du monitoring |

---

## 🔔 Configurer les alertes

### Accès aux paramètres

Menu **Paramètres** → **Envoies** ou **Généraux**

### Types d'alertes disponibles

| Type | Description | Licence requise |
|------|-------------|-----------------|
| **Popup** | Notification à l'écran | ❌ Non |
| **Email** | Envoi par email SMTP | ✅ Oui |
| **Telegram** | Message via bot Telegram | ✅ Oui |
| **Mail Récap** | Email récapitulatif programmé | ✅ Oui |

![Configuration alertes](../screenshots/windows_app_05_alerts.png)
*Configuration des alertes*

### Configuration Email

1. Menu **Paramètres** → **Envoies**
2. Remplissez :
   - **Serveur SMTP** : `smtp.gmail.com`
   - **Port** : `587`
   - **Email** : votre adresse
   - **Mot de passe** : mot de passe d'application
   - **Destinataires** : emails séparés par des virgules
3. Cliquez sur **"Tester"** puis **"Sauvegarder"**

### Configuration Telegram

1. Créez un bot via **@BotFather** sur Telegram
2. Menu **Paramètres** → **Envoies**
3. Entrez le **Token** du bot
4. Entrez votre **Chat ID**
5. Cliquez sur **"Tester"** puis **"Sauvegarder"**

---

## 💾 Exporter/Importer

### Sauvegarder votre liste

1. Menu **Fichier** → **Sauvegarder**
2. Choisissez l'emplacement et le nom du fichier `.pin`
3. Cliquez sur **"Enregistrer"**

### Exporter en Excel

1. Menu **Fichier** → **Exporter Excel**
2. Choisissez l'emplacement
3. Le fichier `.xlsx` est créé

### Ouvrir une sauvegarde

1. Menu **Fichier** → **Ouvrir**
2. Sélectionnez un fichier `.pin`

---

## 🌐 Serveur Web intégré

L'application peut aussi démarrer un serveur web pour un accès distant.

1. Menu **Fonctions** → **Serveur Web** → **Démarrer le serveur**
2. Accédez à : `http://localhost:9090/admin`
3. **Identifiants par défaut** : `admin` / `a`

![Serveur web](../screenshots/windows_app_06_webserver.png)
*Démarrage du serveur web intégré*

---

## 🐛 Dépannage

### L'application ne démarre pas

```powershell
# Vérifier les logs
type "%LOCALAPPDATA%\Ping ü\logs\app.log"

# Ou depuis le dossier d'installation
type logs\app.log
```

### Les pings ne fonctionnent pas

1. Vérifiez que le **pare-feu Windows** autorise ICMP
2. Exécutez en **administrateur** si nécessaire

### Erreur de licence

1. Menu **Paramètres** → **Licence**
2. Copiez le **Code d'activation**
3. Demandez une clé de licence

### Réinitialiser l'application

1. Supprimez le dossier de données :
   ```
   %LOCALAPPDATA%\Ping ü
   ```
2. Relancez l'application

---

## 📞 Support

- **Logs** : `logs/app.log`
- **Documentation** : Menu **Aide** → **Notice**
- **Site web** : https://prog.dynag.co

---

**🎉 Bon monitoring !**

