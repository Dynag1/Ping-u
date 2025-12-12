# 🐧 Ping ü - Installation Linux (Mode Application)

Guide d'installation et d'utilisation de Ping ü en mode application graphique sur Linux.

---

## 📋 Sommaire

1. [Prérequis](#prérequis)
2. [Installation](#installation)
3. [Configuration système](#configuration-système)
4. [Premier lancement](#premier-lancement)
5. [Interface principale](#interface-principale)
6. [Ajouter des hôtes](#ajouter-des-hôtes)
7. [Démarrer le monitoring](#démarrer-le-monitoring)
8. [Configurer les alertes](#configurer-les-alertes)
9. [Dépannage](#dépannage)

---

## 🔧 Prérequis

### Système

| Élément | Requis |
|---------|--------|
| Distribution | Ubuntu 20.04+, Debian 11+, Fedora 35+ |
| RAM | 4 Go minimum |
| Python | 3.9 ou supérieur |
| Interface | X11 ou Wayland |

### Paquets requis

#### Ubuntu/Debian

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv git
sudo apt install python3-pyqt6  # Ou python3-pyside6 si disponible
```

#### Fedora/RHEL

```bash
sudo dnf install python3 python3-pip git python3-qt6
```

#### Arch Linux

```bash
sudo pacman -S python python-pip python-pyside6 git
```

---

## 📦 Installation

### Étape 1 : Cloner le projet

```bash
# Cloner le dépôt
git clone https://github.com/votre-repo/ping-u.git
cd ping-u

# Ou télécharger et extraire l'archive
wget https://url/ping-u.tar.gz
tar -xzf ping-u.tar.gz
cd ping-u
```

### Étape 2 : Créer l'environnement virtuel

```bash
# Créer l'environnement
python3 -m venv .venv

# Activer l'environnement
source .venv/bin/activate

# Vérifier l'activation
which python  # Doit afficher .venv/bin/python
```

### Étape 3 : Installer les dépendances

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## ⚙️ Configuration système

### Permissions ping (IMPORTANT)

Par défaut sur Linux, les pings ICMP nécessitent des permissions root. Pour éviter de lancer l'application en sudo :

```bash
# Méthode 1 : Autoriser ping pour tous (recommandé)
sudo sysctl -w net.ipv4.ping_group_range="0 2147483647"

# Rendre permanent
echo "net.ipv4.ping_group_range=0 2147483647" | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

```bash
# Méthode 2 : Capability sur Python (alternative)
sudo setcap cap_net_raw+ep $(which python3)
```

### Vérifier la configuration

```bash
# Test ping sans sudo
ping -c 1 8.8.8.8
```

---

## 🚀 Premier lancement

### Lancer l'application

```bash
# Activer l'environnement virtuel
source .venv/bin/activate

# Lancer
python3 Pingu.py
```

### Créer un lanceur de bureau

Créez le fichier `~/.local/share/applications/pingu.desktop` :

```ini
[Desktop Entry]
Name=Ping ü
Comment=Monitoring réseau
Exec=/chemin/vers/ping-u/.venv/bin/python /chemin/vers/ping-u/Pingu.py
Icon=/chemin/vers/ping-u/icon.ico
Terminal=false
Type=Application
Categories=Network;Utility;
```

```bash
# Rendre exécutable
chmod +x ~/.local/share/applications/pingu.desktop

# Mettre à jour le cache
update-desktop-database ~/.local/share/applications/
```

![Premier lancement](../screenshots/linux_app_01_main.png)
*Interface principale sur Linux*

---

## 🖥️ Interface principale

### Description des zones

| Zone | Description |
|------|-------------|
| **Barre de menu** | Fichier, Paramètres, Fonctions, Aide |
| **Barre d'outils** | Ajout rapide d'hôtes |
| **Tableau central** | Liste des hôtes surveillés |
| **Panneau alertes** | Configuration rapide des alertes |
| **Barre d'état** | Version et licence |

### Raccourcis clavier

| Raccourci | Action |
|-----------|--------|
| `Ctrl+S` | Sauvegarder |
| `Ctrl+O` | Ouvrir |
| `Ctrl+N` | Nouveau |
| `Ctrl+Q` | Quitter |

---

## ➕ Ajouter des hôtes

### Ajout manuel

1. Entrez l'**IP** dans le champ prévu
2. Définissez le **nombre d'hôtes** (1 pour un seul)
3. Cliquez sur **"Ajouter"**

![Ajout hôte](../screenshots/linux_app_02_add.png)
*Ajout d'un hôte*

### Scanner une plage

1. Entrez l'**IP de départ** : `192.168.1.1`
2. **Nombre d'hôtes** : `254`
3. Sélectionnez **"Alive"** pour ne garder que les hôtes actifs
4. Cliquez sur **"Ajouter"**

### Import de fichier

```bash
# Format CSV supporté
IP,Nom,Mac,Port,Commentaire
192.168.1.1,Routeur,aa:bb:cc:dd:ee:ff,80,Box internet
192.168.1.10,Serveur,11:22:33:44:55:66,22,Serveur web
```

---

## ▶️ Démarrer le monitoring

### Configuration

1. **Délai** : Intervalle entre les pings (secondes)
2. **Nb HS** : Nombre d'échecs avant alerte

### Lancement

1. Ajoutez des hôtes au tableau
2. Configurez le délai et le seuil HS
3. Cliquez sur **"Start"** (bouton vert)

![Monitoring actif](../screenshots/linux_app_03_monitoring.png)
*Monitoring en cours*

### Lecture du tableau

| Couleur | Latence | Signification |
|---------|---------|---------------|
| 🟢 Vert | < 50ms | Excellent |
| 🟡 Jaune | 50-100ms | Bon |
| 🟠 Orange | 100-200ms | Lent |
| 🔴 Rouge | > 500ms ou HS | Critique |

---

## 🔔 Configurer les alertes

### Accès

Menu **Paramètres** → **Envoies**

### Types d'alertes

| Type | Description | Licence |
|------|-------------|---------|
| Popup | Notification système | ❌ |
| Email | SMTP | ✅ |
| Telegram | Bot | ✅ |
| Récap | Email programmé | ✅ |

![Configuration alertes](../screenshots/linux_app_04_alerts.png)
*Configuration des alertes*

### Configuration Email (Gmail)

```
Serveur : smtp.gmail.com
Port : 587
Email : votre@gmail.com
Mot de passe : [Mot de passe d'application Google]
Destinataires : dest@email.com
```

### Configuration Telegram

1. Créez un bot : `@BotFather` → `/newbot`
2. Récupérez le **Token**
3. Obtenez votre **Chat ID** : `@userinfobot`
4. Entrez les informations dans les paramètres

---

## 🌐 Serveur Web intégré

L'application peut démarrer un serveur web pour accès distant.

### Démarrer le serveur

1. Menu **Fonctions** → **Serveur Web** → **Démarrer**
2. URL : http://localhost:9090/admin
3. Identifiants : `admin` / `a`

### Ouvrir le pare-feu

```bash
# UFW (Ubuntu)
sudo ufw allow 9090/tcp

# firewalld (Fedora)
sudo firewall-cmd --permanent --add-port=9090/tcp
sudo firewall-cmd --reload
```

---

## 💾 Sauvegardes

### Emplacement des données

```bash
# Données de l'application
~/ping-u/bd/           # Sauvegardes .pin
~/ping-u/logs/         # Logs
~/ping-u/tab*          # Configuration
~/ping-u/web_users.json # Identifiants web
```

### Sauvegarde manuelle

```bash
# Script de sauvegarde
tar -czf pingu_backup_$(date +%Y%m%d).tar.gz \
    bd/ tab* web_users.json
```

### Restauration

```bash
tar -xzf pingu_backup_20240101.tar.gz
```

---

## 🐛 Dépannage

### L'application ne démarre pas

```bash
# Vérifier Python
python3 --version  # Doit être >= 3.9

# Vérifier les dépendances
pip list | grep -i pyside

# Réinstaller
pip install --upgrade -r requirements.txt
```

### Erreur "Operation not permitted" sur ping

```bash
# Solution
sudo sysctl -w net.ipv4.ping_group_range="0 2147483647"
echo "net.ipv4.ping_group_range=0 2147483647" | sudo tee -a /etc/sysctl.conf
```

### Interface graphique ne s'affiche pas

```bash
# Vérifier X11/Wayland
echo $DISPLAY        # Doit afficher :0 ou similaire
echo $XDG_SESSION_TYPE  # x11 ou wayland

# Installer les dépendances Qt
sudo apt install libxcb-xinerama0 libxcb-cursor0
```

### Erreur de dépendances Qt

```bash
# Ubuntu/Debian
sudo apt install python3-pyqt6

# Ou installer via pip
pip install PySide6
```

### Logs de l'application

```bash
# Voir les dernières erreurs
tail -50 logs/app.log

# Filtrer les erreurs
grep -i error logs/app.log
```

---

## 🔄 Mise à jour

```bash
cd ~/ping-u

# Sauvegarder la config
cp -r bd/ tab* web_users.json ~/backup_pingu/

# Mettre à jour
git pull

# Réinstaller les dépendances
source .venv/bin/activate
pip install --upgrade -r requirements.txt

# Relancer
python3 Pingu.py
```

---

## 📞 Support

| Ressource | Emplacement |
|-----------|-------------|
| Logs | `logs/app.log` |
| Documentation | README.md |
| Site web | https://prog.dynag.co |

---

**🎉 Bon monitoring sur Linux !**

