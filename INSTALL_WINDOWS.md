# 🪟 Installation et Utilisation - Windows

Guide complet pour installer et utiliser Ping ü sur Windows.

---

## 📋 Table des matières

1. [Installation](#installation)
2. [Premier lancement](#premier-lancement)
3. [Mode Headless](#mode-headless)
4. [Interface Web](#interface-web)
5. [Configuration](#configuration)
6. [Dépannage](#dépannage)

---

## 🚀 Installation

### Prérequis

- Windows 10/11
- Python 3.9+ (si utilisation du code source)
- 4 Go RAM minimum

### Option 1 : Exécutable (Recommandé)

1. Téléchargez `Ping_u.exe` depuis les releases
2. Double-cliquez sur l'exécutable
3. ✅ C'est tout !

### Option 2 : Code source

```powershell
# Cloner le dépôt
git clone [URL_DU_REPO]
cd ping-u

# Créer un environnement virtuel
python -m venv .venv
.venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt

# Lancer l'application
python Pingu.py
```

---

## 🎯 Premier lancement

### Mode Interface Graphique (par défaut)

1. Lancez `Ping_u.exe` ou `python Pingu.py`
2. L'interface Qt s'ouvre
3. Ajoutez des hôtes à surveiller
4. Cliquez sur "Start" pour démarrer le monitoring

### Fonctionnalités principales

- ✅ **Monitoring ping** en temps réel
- ✅ **Alertes** (popup, email, Telegram)
- ✅ **Export/Import** CSV et Excel
- ✅ **SNMP** (température, débits réseau)
- ✅ **Interface web** pour accès distant

---

## 🌐 Mode Headless

Le mode headless permet de lancer l'application sans interface graphique, idéal pour un serveur ou un PC toujours allumé.

### Démarrage

```batch
REM Méthode 1: Via le script (recommandé)
start_headless.bat

REM Méthode 2: Commande directe
.venv\Scripts\activate
python Pingu.py --headless
```

### Arrêt

```batch
REM Méthode 1: Via le script
stop_headless.bat

REM Méthode 2: Commande directe
python Pingu.py -stop
```

### Logs

```batch
REM Voir les logs
type pingu_headless.log

REM Logs applicatifs détaillés
type logs\app.log
```

---

## 🖥️ Interface Web

L'interface web est accessible quand le mode headless est actif (ou via Menu > Fonctions > Serveur Web > Démarrer en mode GUI).

### Accès

**Local** : http://localhost:9090/admin  
**Réseau** : http://[VOTRE_IP]:9090/admin

**Identifiants par défaut** : `admin` / `admin`  
⚠️ **Changez-les immédiatement** via l'interface web !

### Fonctionnalités web

- ✅ Ajouter/supprimer des hôtes
- ✅ Démarrer/arrêter le monitoring
- ✅ Voir les statistiques en temps réel
- ✅ Configurer les alertes
- ✅ Export/Import CSV
- ✅ Changer les identifiants

### Notifications navigateur

L'interface web enverra des notifications popup (navigateur) quand :
- ✅ Un scan d'hôtes est terminé
- ✅ Des hôtes passent HS/OK (si configuré)

---

## ⚙️ Configuration

### Paramètres de monitoring

**Via l'interface graphique** :
- Délai entre pings : 10 secondes par défaut
- Nombre de pings avant alerte HS : 3 par défaut
- Alertes : Popup, Email, Telegram

**Via l'interface web** :
- Onglet "Paramètres" → Configurer tous les paramètres

### Configuration Email (SMTP)

1. Ouvrez l'interface web : http://localhost:9090/admin
2. Onglet "Email"
3. Remplissez :
   - Serveur SMTP : `smtp.gmail.com` (exemple)
   - Port : `587`
   - Email : votre@email.com
   - Mot de passe : mot de passe d'application
   - Destinataires : email1@test.com, email2@test.com

### Configuration Telegram

1. Créez un bot via @BotFather sur Telegram
2. Récupérez le token
3. Dans l'interface web → Onglet "Telegram"
4. Collez le token et votre Chat ID

### SNMP (optionnel)

Pour afficher température et débits réseau :
- Assurez-vous que SNMP est activé sur vos équipements
- Community string : généralement `public`
- Port : 161 (UDP)

---

## 🔒 Pare-feu Windows

Si l'interface web n'est pas accessible depuis un autre PC :

```powershell
# Autoriser le port 9090 (en tant qu'administrateur)
netsh advfirewall firewall add rule name="Ping U Web" dir=in action=allow protocol=TCP localport=9090
```

---

## 🐛 Dépannage

### L'application ne démarre pas

```powershell
# Vérifier Python
python --version

# Réinstaller les dépendances
pip install --upgrade -r requirements.txt
```

### L'interface web ne s'ouvre pas

```powershell
# Vérifier que le port 9090 est libre
netstat -ano | findstr :9090

# Si occupé, tuer le processus
taskkill /PID [PID] /F
```

### Erreurs dans les logs

```powershell
# Voir les 50 dernières lignes
powershell -command "Get-Content logs\app.log -Tail 50"

# Chercher une erreur spécifique
findstr /i "error" logs\app.log
```

### Le monitoring ne démarre pas

1. Vérifiez que des hôtes sont ajoutés
2. Vérifiez les logs : `type logs\app.log`
3. Redémarrez l'application

### SNMP ne fonctionne pas

SNMP est optionnel. Si vous ne l'utilisez pas :
- Le monitoring ping fonctionnera normalement
- Vous n'aurez pas : température, débits réseau

Pour activer SNMP :
- Activez SNMP sur vos équipements
- Vérifiez la connectivité SNMP

---

## 📊 Utilisation avancée

### Démarrage automatique Windows

**Méthode 1 : Planificateur de tâches**

1. Ouvrir le Planificateur de tâches Windows
2. Créer une tâche de base
3. Déclencheur : À l'ouverture de session
4. Action : Démarrer un programme
5. Programme : `C:\chemin\vers\ping-u\start_headless.bat`

**Méthode 2 : Dossier Démarrage**

1. `Win + R` → `shell:startup`
2. Créer un raccourci vers `start_headless.bat`
3. Redémarrer Windows

### Export automatique CSV

Via l'interface web : "Actions" → "Exporter CSV"

Les données incluent :
- IP, Nom, MAC
- Statut (OK/HS)
- Latence
- Température (si SNMP)

### Sauvegarde des données

Les fichiers importants à sauvegarder :
- `tab*` : Fichiers de configuration
- `web_users.json` : Identifiants web
- `bd/*.pin` : Sauvegardes des hôtes

---

## 🔄 Mise à jour

```powershell
# Via Git
git pull
pip install --upgrade -r requirements.txt

# Redémarrer l'application
stop_headless.bat
start_headless.bat
```

---

## 📞 Support

- **Logs** : `logs\app.log`
- **Documentation** : README.md
- **GitHub Issues** : Signaler un problème

---

## ✨ Astuces

### Surveillance réseau externe

Pour surveiller depuis l'extérieur (Internet) :

1. Configurez la redirection de port sur votre box :
   - Port externe : 9090
   - Port interne : 9090
   - IP : IP de votre PC
2. Accédez via : `http://[VOTRE_IP_PUBLIQUE]:9090/admin`
3. ⚠️ Utilisez un mot de passe fort !

### Multiples instances

Vous pouvez lancer plusieurs instances avec différents ports :

```powershell
# Modifier dans Pingu.py :
# port=9090  →  port=9091
python Pingu.py --headless
```

---

**🎉 Vous êtes prêt ! Bon monitoring !**

