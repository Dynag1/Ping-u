# 🍓 Installation Ping ü - Raspberry Pi

Guide complet pour installer et utiliser Ping ü sur Raspberry Pi (Raspbian/Raspberry Pi OS).

---

## 📋 Table des matières

1. [Prérequis](#-prérequis)
2. [Installation rapide](#-installation-rapide)
3. [Installation détaillée](#-installation-détaillée)
4. [Configuration](#-configuration)
5. [Utilisation](#-utilisation)
6. [Service systemd](#-service-systemd)
7. [SNMP (optionnel)](#-snmp-optionnel)
8. [Dépannage](#-dépannage)
9. [Mise à jour](#-mise-à-jour)

---

## 📦 Prérequis

- Raspberry Pi 3/4/5 (ou Zero 2 W)
- Raspberry Pi OS (Bullseye ou Bookworm)
- Python 3.10 ou supérieur
- Connexion réseau

---

## 🚀 Installation rapide

```bash
# 1. Mettre à jour le système
sudo apt update && sudo apt upgrade -y

# 2. Installer les dépendances système
sudo apt install -y python3 python3-pip python3-venv git libffi-dev libssl-dev

# 3. Cloner le projet
git clone https://github.com/Dynag1/Ping-u.git ~/Ping-u
cd ~/Ping-u

# 4. Créer l'environnement virtuel
python3 -m venv .venv
source .venv/bin/activate

# 5. Installer les dépendances Python
pip install --upgrade pip
pip install Flask Flask-SocketIO Flask-Cors python-socketio python-engineio
pip install eventlet requests cryptography openpyxl xmltodict urllib3

# 6. Configurer les permissions ping
sudo sysctl -w net.ipv4.ping_group_range="0 2147483647"
echo "net.ipv4.ping_group_range=0 2147483647" | sudo tee -a /etc/sysctl.conf

# 7. Initialiser la configuration
python init_raspberry.py

# 8. Rendre les scripts exécutables
chmod +x start_headless.sh stop_headless.sh fix_raspberry.sh

# 9. Démarrer l'application
./start_headless.sh
```

**Accès web** : `http://[IP_RASPBERRY]:9090/admin`  
**Identifiants** : `admin` / `a`

---

## 📖 Installation détaillée

### Étape 1 : Mise à jour du système

```bash
sudo apt update
sudo apt upgrade -y
```

### Étape 2 : Installation des dépendances système

```bash
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    git \
    libffi-dev \
    libssl-dev \
    build-essential
```

### Étape 3 : Cloner le projet

```bash
# Via Git (recommandé)
git clone https://github.com/Dynag1/Ping-u.git ~/Ping-u

# Ou via SCP depuis Windows
# scp -r "C:\Users\...\Ping ü" user@raspberry:~/Ping-u
```

### Étape 4 : Créer l'environnement virtuel

```bash
cd ~/Ping-u
python3 -m venv .venv
source .venv/bin/activate
```

> ⚠️ **Important** : Toujours activer le venv avant d'installer des packages ou lancer l'app

### Étape 5 : Installer les dépendances Python

```bash
# Mettre à jour pip
pip install --upgrade pip

# Dépendances principales (NE PAS installer PySide6 ou qt-themes !)
pip install Flask>=2.3.0
pip install Flask-SocketIO>=5.3.0
pip install Flask-Cors>=4.0.0
pip install python-socketio>=5.8.0
pip install python-engineio>=4.5.0
pip install eventlet>=0.33.0
pip install requests>=2.31.0
pip install cryptography>=41.0.0
pip install openpyxl>=3.1.0
pip install xmltodict>=0.13.0
pip install urllib3>=2.0.0
```

Ou en une seule commande :

```bash
pip install Flask Flask-SocketIO Flask-Cors python-socketio python-engineio \
    eventlet requests cryptography openpyxl xmltodict urllib3
```

### Étape 6 : Configurer les permissions ping

```bash
# Activer le ping sans sudo
sudo sysctl -w net.ipv4.ping_group_range="0 2147483647"

# Rendre permanent
echo "net.ipv4.ping_group_range=0 2147483647" | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

### Étape 7 : Initialisation

```bash
cd ~/Ping-u

# Script d'initialisation (crée les fichiers de config)
python init_raspberry.py

# Ou script de correction complet
chmod +x fix_raspberry.sh
./fix_raspberry.sh
```

### Étape 8 : Premier lancement (test)

```bash
# Tester en mode direct (pour voir les erreurs)
python Pingu.py --headless
```

Si tout fonctionne, vous verrez :
```
[HEADLESS] Serveur web demarre sur http://0.0.0.0:9090
[HEADLESS] Application demarree en mode headless
```

Arrêtez avec `Ctrl+C`.

### Étape 9 : Lancement en arrière-plan

```bash
chmod +x start_headless.sh stop_headless.sh
./start_headless.sh
```

---

## ⚙️ Configuration

### Fichiers de configuration

| Fichier | Description |
|---------|-------------|
| `tab` | Paramètres généraux |
| `tab4` | Configuration des alertes |
| `tabG` | Paramètres graphiques |
| `web_users.json` | Utilisateurs web |
| `bd/autosave.pin` | Sauvegarde auto des hôtes |

### Créer les fichiers manuellement (si nécessaire)

```bash
cd ~/Ping-u

# Fichiers de config vides
echo "10,5,0,1,1,1,0,,0" > tab
echo "0,,,,0,,,,0,0" > tab4
echo "0,0,0,nord" > tabG

# Utilisateur web par défaut (admin/a)
echo '{"username": "admin", "password": "ca978112ca1bbdcafac231b39a23dc4da786eff8147c4e72b9807785afee48bb"}' > web_users.json
```

---

## 🌐 Utilisation

### Démarrer l'application

```bash
cd ~/Ping-u
./start_headless.sh
```

### Arrêter l'application

```bash
cd ~/Ping-u
./stop_headless.sh
```

### Accès à l'interface web

**URL** : `http://[IP_RASPBERRY]:9090/admin`

Pour trouver l'IP du Raspberry Pi :
```bash
hostname -I | awk '{print $1}'
```

**Identifiants par défaut** : `admin` / `a`  
⚠️ **Changez le mot de passe immédiatement !**

### Fonctionnalités web

- ✅ Ajouter/supprimer des hôtes
- ✅ Scanner le réseau automatiquement
- ✅ Démarrer/arrêter le monitoring
- ✅ Configurer les alertes (Email, Telegram)
- ✅ Import/Export CSV
- ✅ Statistiques en temps réel
- ✅ Température équipements (si SNMP configuré)

### Consulter les logs

```bash
# Logs en temps réel
tail -f ~/Ping-u/pingu_headless.log

# Logs applicatifs
tail -f ~/Ping-u/logs/app.log

# Erreurs uniquement
grep -i error ~/Ping-u/logs/app.log
```

---

## 🔧 Service systemd

Pour démarrer automatiquement au boot :

### 1. Créer le service

```bash
sudo nano /etc/systemd/system/pingu.service
```

### 2. Contenu du fichier

```ini
[Unit]
Description=Ping ü - Monitoring Réseau
After=network.target

[Service]
Type=simple
User=dynag
WorkingDirectory=/home/dynag/Ping-u
Environment="PATH=/home/dynag/Ping-u/.venv/bin"
ExecStart=/home/dynag/Ping-u/.venv/bin/python /home/dynag/Ping-u/Pingu.py --headless
ExecStop=/home/dynag/Ping-u/.venv/bin/python /home/dynag/Ping-u/Pingu.py -stop
Restart=on-failure
RestartSec=10
StandardOutput=append:/home/dynag/Ping-u/pingu_headless.log
StandardError=append:/home/dynag/Ping-u/pingu_headless.log

[Install]
WantedBy=multi-user.target
```

> ⚠️ Remplacez `dynag` par votre nom d'utilisateur

### 3. Activer et démarrer

```bash
# Recharger systemd
sudo systemctl daemon-reload

# Activer au démarrage
sudo systemctl enable pingu.service

# Démarrer
sudo systemctl start pingu.service

# Vérifier le statut
sudo systemctl status pingu.service

# Voir les logs
sudo journalctl -u pingu.service -f
```

### 4. Commandes utiles

```bash
# Arrêter
sudo systemctl stop pingu.service

# Redémarrer
sudo systemctl restart pingu.service

# Désactiver
sudo systemctl disable pingu.service
```

---

## 🌡️ SNMP (optionnel)

SNMP permet d'afficher la température et les débits réseau des équipements compatibles.

### Installation

```bash
cd ~/Ping-u
source .venv/bin/activate

# Installer pysnmp-lextudio (fork maintenu)
pip install pysnmp-lextudio pyasn1 pyasn1-modules pycryptodomex

# Redémarrer l'application
./stop_headless.sh
./start_headless.sh
```

### Outils de test SNMP

```bash
# Installer les outils SNMP
sudo apt install -y snmp snmp-mibs-downloader

# Tester un équipement
snmpwalk -v2c -c public 192.168.1.1 system
```

### Configuration équipements

Vos équipements doivent avoir :
- SNMP activé (version 2c recommandée)
- Community string : `public`
- Port : 161 (UDP)

> **Note** : SNMP est **optionnel**. Sans SNMP, le monitoring ping fonctionne normalement.

---

## 🐛 Dépannage

### Erreur : "No module named 'flask'"

```bash
cd ~/Ping-u
source .venv/bin/activate
pip install Flask Flask-SocketIO Flask-Cors
```

### Erreur : "No module named 'cryptography'"

```bash
source .venv/bin/activate
pip install cryptography
```

### Erreur : "Operation not permitted" (ping)

```bash
sudo sysctl -w net.ipv4.ping_group_range="0 2147483647"
echo "net.ipv4.ping_group_range=0 2147483647" | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

### Erreur : "Port 9090 déjà utilisé"

```bash
# Trouver le processus
sudo lsof -i :9090

# Tuer le processus
sudo kill -9 $(sudo lsof -t -i:9090)

# Nettoyer
rm -f ~/Ping-u/pingu_headless.pid
```

### L'application ne démarre pas

```bash
# Tester en mode direct pour voir les erreurs
cd ~/Ping-u
source .venv/bin/activate
python Pingu.py --headless
```

### Diagnostic complet

```bash
# 1. Python OK ?
python3 --version

# 2. Venv activé ?
which python
# Doit afficher: /home/.../Ping-u/.venv/bin/python

# 3. Modules installés ?
pip list | grep -i flask

# 4. Ping fonctionne ?
ping -c 1 8.8.8.8

# 5. Port 9090 libre ?
ss -tlnp | grep 9090

# 6. API répond ?
curl http://localhost:9090/api/status

# 7. Processus actif ?
ps aux | grep Pingu
```

### Forcer l'arrêt

```bash
pkill -f "Pingu.py"
rm -f ~/Ping-u/pingu_headless.pid
```

### Réinstallation propre

```bash
cd ~/Ping-u

# Sauvegarder
mkdir -p ~/backup_pingu
cp -r tab* web_users.json bd/ ~/backup_pingu/

# Supprimer le venv
rm -rf .venv

# Recréer
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install Flask Flask-SocketIO Flask-Cors python-socketio python-engineio \
    eventlet requests cryptography openpyxl xmltodict urllib3

# Restaurer config
cp ~/backup_pingu/* .

# Relancer
./start_headless.sh
```

---

## 🔄 Mise à jour

```bash
cd ~/Ping-u

# Arrêter l'application
./stop_headless.sh

# Sauvegarder la config
cp -r tab* web_users.json bd/ ~/backup_pingu/

# Mettre à jour le code
git pull

# Mettre à jour les dépendances
source .venv/bin/activate
pip install --upgrade Flask Flask-SocketIO Flask-Cors eventlet requests cryptography

# Relancer
./start_headless.sh

# Ou avec systemd
sudo systemctl restart pingu.service
```

---

## 🔒 Sécurité

### Checklist

- [ ] Changer le mot de passe par défaut (`admin`/`a`)
- [ ] Configurer le pare-feu
- [ ] Utiliser HTTPS (reverse proxy nginx)
- [ ] Sauvegardes régulières

### Pare-feu

```bash
# Autoriser le port 9090
sudo ufw allow 9090/tcp
sudo ufw enable
sudo ufw status
```

### Reverse Proxy HTTPS (Nginx)

```bash
sudo apt install nginx

sudo nano /etc/nginx/sites-available/pingu
```

```nginx
server {
    listen 80;
    server_name monitoring.local;

    location / {
        proxy_pass http://localhost:9090;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/pingu /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## 💡 Astuces

### IP fixe

```bash
sudo nano /etc/dhcpcd.conf
```

Ajouter :
```
interface eth0
static ip_address=192.168.1.100/24
static routers=192.168.1.1
static domain_name_servers=192.168.1.1 8.8.8.8
```

### Connexion SSH

```bash
# Depuis votre PC
ssh user@[IP_RASPBERRY]

# Copier des fichiers
scp fichier.txt user@[IP_RASPBERRY]:~/Ping-u/
```

### Sauvegarde automatique (cron)

```bash
crontab -e
```

Ajouter :
```
0 2 * * * tar -czf ~/backups/pingu_$(date +\%Y\%m\%d).tar.gz ~/Ping-u/tab* ~/Ping-u/web_users.json ~/Ping-u/bd/
```

### Monitoring ressources

```bash
# CPU/RAM du processus
top -p $(cat ~/Ping-u/pingu_headless.pid)

# Température Raspberry Pi
vcgencmd measure_temp

# Espace disque
df -h
```

---

## 📞 Support

- **Logs** : `~/Ping-u/logs/app.log`
- **Documentation** : README.md
- **GitHub Issues** : Signaler un problème

---

**🎉 Votre Raspberry Pi est prêt à surveiller votre réseau 24/7 !**
