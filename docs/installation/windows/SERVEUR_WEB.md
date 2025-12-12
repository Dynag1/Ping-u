# 🪟 Ping ü - Installation Windows (Mode Serveur Web)

Guide d'installation et d'utilisation de Ping ü en mode serveur web (headless) sur Windows.

---

## 📋 Sommaire

1. [Qu'est-ce que le mode serveur web ?](#quest-ce-que-le-mode-serveur-web)
2. [Prérequis](#prérequis)
3. [Installation](#installation)
4. [Démarrage du serveur](#démarrage-du-serveur)
5. [Interface web d'administration](#interface-web-dadministration)
6. [Gestion des hôtes](#gestion-des-hôtes)
7. [Configuration des alertes](#configuration-des-alertes)
8. [Démarrage automatique](#démarrage-automatique)
9. [Sécurité et pare-feu](#sécurité-et-pare-feu)
10. [Dépannage](#dépannage)

---

## 💡 Qu'est-ce que le mode serveur web ?

Le **mode serveur web** (ou mode headless) permet d'utiliser Ping ü **sans interface graphique**. L'application tourne en arrière-plan et est contrôlable via un **navigateur web**.

### Avantages

| ✅ Avantage | Description |
|-------------|-------------|
| **Accès distant** | Contrôlez depuis n'importe quel appareil |
| **Ressources** | Moins de RAM/CPU qu'en mode graphique |
| **Serveur** | Idéal pour un PC toujours allumé |
| **Multi-utilisateurs** | Plusieurs personnes peuvent accéder |

### Cas d'utilisation

- Serveur de monitoring 24/7
- PC sans écran connecté
- Accès depuis smartphone/tablette
- Monitoring centralisé multi-sites

---

## 🔧 Prérequis

| Élément | Requis |
|---------|--------|
| Système | Windows 10/11 (64 bits) |
| RAM | 2 Go minimum |
| Espace disque | 200 Mo |
| Réseau | Port 9090 disponible |
| Navigateur | Chrome, Firefox, Edge (moderne) |

---

## 📦 Installation

### Option 1 : Installateur

1. Exécutez `PingU_Setup.exe`
2. Suivez l'assistant d'installation
3. Les scripts `start_headless.bat` et `stop_headless.bat` sont inclus

### Option 2 : Code source

```powershell
git clone https://github.com/votre-repo/ping-u.git
cd ping-u
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

---

## ▶️ Démarrage du serveur

### Méthode 1 : Scripts (Recommandé)

```batch
REM Démarrer le serveur
start_headless.bat

REM Arrêter le serveur
stop_headless.bat
```

![Démarrage headless](../screenshots/windows_web_01_start.png)
*Démarrage du serveur en mode headless*

### Méthode 2 : Ligne de commande

```powershell
# Démarrer
python Pingu.py --headless

# Ou
python Pingu.py -start

# Arrêter
python Pingu.py -stop
```

### Vérifier que le serveur tourne

```powershell
# Vérifier le processus
tasklist | findstr python

# Vérifier le port
netstat -ano | findstr :9090
```

### Logs du serveur

```powershell
# Voir les logs en temps réel
powershell -command "Get-Content logs\app.log -Wait -Tail 20"

# Logs headless spécifiques
type pingu_headless.log
```

---

## 🖥️ Interface web d'administration

### Accès à l'interface

| Type d'accès | URL |
|--------------|-----|
| **Local** | http://localhost:9090/admin |
| **Réseau** | http://[IP_DU_PC]:9090/admin |

### Connexion

![Page de connexion](../screenshots/windows_web_02_login.png)
*Page de connexion à l'interface web*

| Champ | Valeur par défaut |
|-------|-------------------|
| Utilisateur | `admin` |
| Mot de passe | `a` |

⚠️ **IMPORTANT** : Changez ces identifiants immédiatement après la première connexion !

### Vue d'ensemble de l'interface

![Interface admin](../screenshots/windows_web_03_dashboard.png)
*Tableau de bord de l'interface web*

| Zone | Description |
|------|-------------|
| **En-tête** | Nom du site, bouton déconnexion, thème |
| **Tableau** | Liste des hôtes avec statut en temps réel |
| **Panneau latéral** | Actions et paramètres |
| **Pied de page** | Version et licence |

---

## ➕ Gestion des hôtes

### Ajouter un hôte

1. Cliquez sur **"Ajouter un hôte"** dans le panneau latéral
2. Remplissez le formulaire :
   - **IP** : Adresse IP de l'hôte
   - **Nom** : Nom descriptif (optionnel)
   - **Port** : Port à surveiller (optionnel)
3. Cliquez sur **"Ajouter"**

![Ajout hôte](../screenshots/windows_web_04_add_host.png)
*Formulaire d'ajout d'hôte*

### Scanner une plage d'adresses

1. Section **"Scanner une plage"**
2. Entrez :
   - **IP de départ** : ex. `192.168.1.1`
   - **Nombre d'hôtes** : ex. `254`
   - **Filtre** : Alive, Tout, ou Site
3. Cliquez sur **"Scanner"**
4. Attendez la fin du scan (progression affichée)

![Scan réseau](../screenshots/windows_web_05_scan.png)
*Scan d'une plage réseau*

### Supprimer un hôte

1. Cliquez sur l'**icône poubelle** 🗑️ sur la ligne de l'hôte
2. Confirmez la suppression

### Exclure un hôte du monitoring

1. Cliquez sur l'**icône d'exclusion** ❌ sur la ligne
2. L'hôte reste dans la liste mais n'est plus pingé

---

## ▶️ Démarrer/Arrêter le monitoring

### Depuis l'interface web

1. Dans le panneau **"Monitoring"**
2. Configurez :
   - **Délai** : Intervalle entre les pings (secondes)
   - **Nb HS** : Nombre d'échecs avant alerte
3. Cliquez sur **"Démarrer"** (bouton vert)

![Contrôle monitoring](../screenshots/windows_web_06_monitoring.png)
*Contrôle du monitoring*

### Statut du monitoring

| Indicateur | Signification |
|------------|---------------|
| 🟢 Vert "Démarrer" | Monitoring arrêté |
| 🔴 Rouge "Arrêter" | Monitoring actif |
| Badge | Nombre d'hôtes surveillés |

---

## 🔔 Configuration des alertes

### Accès aux paramètres

Cliquez sur **"Paramètres"** dans le panneau latéral.

### Alertes disponibles

![Configuration alertes](../screenshots/windows_web_07_alerts.png)
*Configuration des alertes*

| Type | Description | Licence |
|------|-------------|---------|
| **Popup Web** | Notification navigateur | ❌ Non |
| **Email** | Envoi SMTP | ✅ Oui |
| **Telegram** | Bot Telegram | ✅ Oui |
| **Mail Récap** | Email programmé | ✅ Oui |

### Configurer les emails

1. Onglet **"Email"**
2. Remplissez :
   ```
   Serveur SMTP : smtp.gmail.com
   Port : 587
   Email : votre@email.com
   Mot de passe : [mot de passe d'application]
   Destinataires : dest1@email.com, dest2@email.com
   ```
3. Cliquez **"Tester"** puis **"Sauvegarder"**

### Configurer Telegram

1. Créez un bot via **@BotFather**
2. Onglet **"Telegram"**
3. Entrez le **Token** et **Chat ID**
4. Cliquez **"Tester"** puis **"Sauvegarder"**

---

## 🔐 Changer les identifiants

⚠️ **Obligatoire pour la sécurité !**

1. Cliquez sur **"Changer identifiants"** (en haut à droite)
2. Entrez :
   - Nouveau nom d'utilisateur
   - Nouveau mot de passe (2 fois)
3. Cliquez **"Enregistrer"**

![Changement identifiants](../screenshots/windows_web_08_credentials.png)
*Changement des identifiants*

---

## 🔄 Démarrage automatique

### Option 1 : Planificateur de tâches Windows

1. Ouvrez le **Planificateur de tâches** (`taskschd.msc`)
2. **Action** → **Créer une tâche de base**
3. Configurez :
   - **Nom** : `Ping U Headless`
   - **Déclencheur** : Au démarrage de l'ordinateur
   - **Action** : Démarrer un programme
   - **Programme** : `C:\chemin\vers\start_headless.bat`
4. Cochez **"Exécuter avec les autorisations maximales"**

![Planificateur tâches](../screenshots/windows_web_09_scheduler.png)
*Configuration du planificateur de tâches*

### Option 2 : Dossier Démarrage

1. Appuyez sur `Win + R`
2. Tapez `shell:startup`
3. Créez un **raccourci** vers `start_headless.bat`

### Option 3 : Service Windows (avancé)

Utilisez **NSSM** (Non-Sucking Service Manager) :

```powershell
# Télécharger NSSM
# Puis dans un terminal admin :
nssm install PingU "C:\chemin\vers\python.exe" "C:\chemin\vers\Pingu.py --headless"
nssm start PingU
```

---

## 🔒 Sécurité et pare-feu

### Ouvrir le port 9090

```powershell
# En tant qu'administrateur
netsh advfirewall firewall add rule name="Ping U Web" dir=in action=allow protocol=TCP localport=9090
```

### Accès depuis le réseau local

1. Récupérez l'IP du PC : `ipconfig`
2. Accédez depuis un autre appareil : `http://[IP]:9090/admin`

### Accès depuis Internet (avancé)

1. Configurez une **redirection de port** sur votre box :
   - Port externe : 9090
   - Port interne : 9090
   - IP interne : IP du PC
2. Accédez via : `http://[IP_PUBLIQUE]:9090/admin`

⚠️ **Sécurité** :
- Utilisez un mot de passe **fort**
- Envisagez un **reverse proxy** avec HTTPS
- Limitez les accès par **IP** si possible

---

## 📊 Export/Import

### Exporter la liste (CSV)

1. **"Actions"** → **"Exporter CSV"**
2. Le fichier est téléchargé

### Importer une liste

1. **"Actions"** → **"Importer"**
2. Sélectionnez un fichier `.pin` ou `.csv`
3. Les hôtes sont ajoutés

---

## 🐛 Dépannage

### Le serveur ne démarre pas

```powershell
# Vérifier si le port est utilisé
netstat -ano | findstr :9090

# Si occupé, trouver et tuer le processus
taskkill /PID [PID] /F

# Vérifier les logs
type logs\app.log
```

### Impossible de se connecter

| Problème | Solution |
|----------|----------|
| Page inaccessible | Vérifiez que le serveur tourne |
| Erreur 403 | Vérifiez les identifiants |
| Timeout | Vérifiez le pare-feu |

### Mot de passe oublié

1. Arrêtez le serveur : `stop_headless.bat`
2. Supprimez `web_users.json`
3. Redémarrez : `start_headless.bat`
4. Identifiants réinitialisés : `admin` / `a`

### Le monitoring ne démarre pas via l'interface web

1. Vérifiez qu'il y a des hôtes dans la liste
2. Consultez les logs : `logs/app.log`
3. Redémarrez le serveur

### Notifications web ne fonctionnent pas

1. Autorisez les notifications dans votre navigateur
2. Vérifiez que la page est en HTTPS ou localhost

---

## 📁 Fichiers importants

| Fichier | Description |
|---------|-------------|
| `web_users.json` | Identifiants web |
| `logs/app.log` | Logs de l'application |
| `bd/autosave.pin` | Sauvegarde automatique |
| `tab*` | Fichiers de configuration |
| `pingu_headless.pid` | PID du processus |

---

## 📞 Support

- **Logs** : `logs/app.log`
- **Documentation** : https://prog.dynag.co
- **GitHub** : Signaler un problème

---

**🎉 Bon monitoring !**

