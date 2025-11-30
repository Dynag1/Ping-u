# 🍓 Installation et Utilisation - Raspberry Pi

Guide complet pour installer et utiliser Ping ü sur Raspberry Pi (Raspbian/Raspberry Pi OS).

---

## 📋 Table des matières

1. [Installation](#installation)
2. [Configuration initiale](#configuration-initiale)
3. [Correction des erreurs communes](#correction-des-erreurs-communes)
4. [Interface Web](#interface-web)
5. [Service systemd](#service-systemd)
6. [SNMP](#snmp)
7. [Dépannage](#dépannage)

---

## 🚀 Installation

### Prérequis

```bash
# Mettre à jour le système
sudo apt update
sudo apt upgrade -y

# Installer Python et dépendances
sudo apt install -y python3 python3-pip python3-venv git
```

### Installation de Ping ü

```bash
# Cloner le dépôt (ou transférer via SCP)
git clone https://github.com/Dynag1/Ping-u.git ~/ping-u
cd ~/ping-u

# Installer les dépendances
pip3 install -r requirements.txt
```

---

## ⚙️ Configuration initiale

### Script d'initialisation automatique

Le script crée tous les fichiers de configuration nécessaires :

```bash
cd ~/ping-u
chmod +x fix_raspberry.sh start_headless.sh stop_headless.sh
./fix_raspberry.sh
```

Ce script va automatiquement :
- ✅ Configurer les permissions ping
- ✅ Créer les fichiers de configuration (tab, tabG, tab4, etc.)
- ✅ Vérifier les dépendances
- ✅ Tester le ping

### OU Configuration manuelle

Si vous préférez faire étape par étape :

```bash
# 1. Permissions ping
sudo sysctl -w net.ipv4.ping_group_range="0 2147483647"
echo "net.ipv4.ping_group_range=0 2147483647" | sudo tee -a /etc/sysctl.conf

# 2. Créer les fichiers de config
python3 init_raspberry.py

# 3. Vérifier le ping
ping -c 1 8.8.8.8
```

---

## 🔧 Correction des erreurs communes

### Erreur : "[Errno 1] Operation not permitted"

**Cause** : Permissions ping non configurées

**Solution** :
```bash
sudo sysctl -w net.ipv4.ping_group_range="0 2147483647"
echo "net.ipv4.ping_group_range=0 2147483647" | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

### Erreur : "Fichier tab non trouvé"

**Cause** : Fichiers de configuration manquants (normal en première installation)

**Solution** :
```bash
cd ~/ping-u
python3 init_raspberry.py
```

### Erreur : "write() before start_response" (Flask)

**Cause** : Bug corrigé dans les dernières versions

**Solution** : Mettre à jour le code
```bash
cd ~/ping-u
git pull
```

### Erreur : "No module named 'pythonping'"

**Solution** :
```bash
pip3 install -r requirements.txt
```

---

## Mise a jour

### Démarrage

```bash
cd ~/ping-u
git pull https://github.com/Dynag1/Ping-u.git
```

---

## 🌐 Interface Web

### Démarrage

```bash
cd ~/ping-u
./start_headless.sh
```

L'application démarre en arrière-plan sans interface graphique.

### Accès

**URL** : `http://[IP_RASPBERRY]:9090/admin`

Pour trouver l'IP de votre Raspberry Pi :
```bash
hostname -I | awk '{print $1}'
```

**Identifiants par défaut** : `admin` / `admin`  
⚠️ **Changez-les immédiatement** via l'interface web !

### Fonctionnalités

- ✅ Ajouter/supprimer des hôtes (avec scan réseau)
- ✅ Démarrer/arrêter le monitoring
- ✅ Configurer les alertes (Email, Telegram)
- ✅ Export/Import CSV
- ✅ Statistiques en temps réel
- ✅ Notifications navigateur (scan terminé, etc.)
- ✅ Température équipements (si SNMP)
- ✅ Débits réseau (si SNMP)

### Notifications

L'interface web envoie des notifications popup navigateur :
- Quand un scan d'hôtes est terminé
- Quand des hôtes changent d'état (optionnel)

Autorisez les notifications dans votre navigateur pour les recevoir.

---

## 🔧 Service systemd

Pour démarrer automatiquement au boot du Raspberry Pi :

### 1. Créer le service

```bash
sudo nano /etc/systemd/system/pingu.service
```

### 2. Contenu

```ini
[Unit]
Description=Ping ü - Monitoring Réseau
After=network.target

[Service]
Type=simple
User=pingu
WorkingDirectory=/home/pingu/ping-u
ExecStart=/usr/bin/python3 /home/pingu/ping-u/Pingu.py --headless
ExecStop=/usr/bin/python3 /home/pingu/ping-u/Pingu.py -stop
Restart=on-failure
RestartSec=10
StandardOutput=append:/home/pingu/ping-u/pingu_headless.log
StandardError=append:/home/pingu/ping-u/pingu_headless.log

[Install]
WantedBy=multi-user.target
```

⚠️ Remplacez `pingu` par votre nom d'utilisateur

### 3. Activer et démarrer

```bash
# Recharger systemd
sudo systemctl daemon-reload

# Activer au démarrage
sudo systemctl enable pingu.service

# Démarrer
sudo systemctl start pingu.service

# Vérifier
sudo systemctl status pingu.service

# Logs
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

## 🌡️ SNMP

SNMP permet d'afficher la température et les débits réseau des équipements compatibles.

### Installation

```bash
cd ~/ping-u

# Désinstaller l'ancien pysnmp (abandonné)
pip3 uninstall -y pysnmp

# Installer pysnmp-lextudio (fork maintenu)
pip3 install pysnmp-lextudio pyasn1 pyasn1-modules pycryptodomex

# Redémarrer
./stop_headless.sh
./start_headless.sh
```

### Vérification

```bash
# Installer les outils SNMP
sudo apt install snmp snmp-mibs-downloader

# Tester un équipement (exemple)
snmpwalk -v2c -c public 192.168.1.1 system
```

### Configuration des équipements

Pour que SNMP fonctionne, vos équipements doivent :

1. **Avoir SNMP activé** (version 2c recommandée)
2. **Community string** : `public` (lecture seule)
3. **Port** : 161 (UDP)

**Exemples** :
- **NAS Synology** : Panneau de configuration → Terminal & SNMP → Activer SNMP
- **Routeurs** : Interface admin → SNMP → Activer v2c
- **Switches** : Configuration web → SNMP settings

### Test Python

```bash
cd ~/ping-u
python3 -c "
from src.utils.snmp_helper import snmp_helper
import asyncio

async def test():
    # Remplacez par l'IP d'un équipement SNMP
    temp = await snmp_helper.get_temperature('192.168.1.1')
    print(f'Température: {temp}')

asyncio.run(test())
"
```

### Dépannage SNMP

**Erreur : "No module named 'pysnmp'"**
```bash
pip3 install pysnmp-lextudio
```

**Erreur : "No matching distribution found for pysnmp==6.0.0"**
```bash
pip3 uninstall -y pysnmp
pip3 install pysnmp-lextudio
```

**SNMP ne retourne rien**
- Vérifiez que SNMP est activé sur l'équipement
- Vérifiez le community string (généralement `public`)
- Testez avec `snmpwalk`
- Vérifiez le pare-feu (port UDP 161)

**Note** : SNMP est **optionnel**. Sans SNMP, le monitoring ping fonctionne normalement, vous n'aurez simplement pas la température et les débits réseau.

---

## 🔒 Pare-feu

```bash
# Autoriser le port 9090
sudo ufw allow 9090/tcp

# Vérifier
sudo ufw status
```

---

## 🐛 Dépannage

### Diagnostic complet

```bash
# 1. Ping fonctionne ?
ping -c 1 8.8.8.8

# 2. Processus actif ?
ps aux | grep Pingu

# 3. Port 9090 ouvert ?
netstat -tlnp | grep 9090
# ou
ss -tlnp | grep 9090

# 4. API web répond ?
curl http://localhost:9090/api/status

# 5. Logs OK ?
tail -20 ~/ping-u/pingu_headless.log
```

### Logs

```bash
# Logs temps réel
tail -f ~/ping-u/pingu_headless.log

# Logs applicatifs
tail -f ~/ping-u/logs/app.log

# Erreurs uniquement
grep -i error ~/ping-u/pingu_headless.log

# Logs des 50 dernières lignes
tail -50 ~/ping-u/logs/app.log
```

### Port déjà utilisé

```bash
# Trouver qui utilise le port
sudo lsof -i :9090

# Tuer le processus
sudo kill -9 [PID]
```

### Forcer l'arrêt

```bash
cd ~/ping-u
kill -9 $(cat pingu_headless.pid)
rm pingu_headless.pid
```

### Réinstallation propre

```bash
cd ~/ping-u

# Sauvegarder la config
mkdir ~/backup
cp tab* web_users.json bd/ ~/backup/

# Mise à jour
git pull
pip3 install --upgrade -r requirements.txt

# Relancer
./stop_headless.sh
./start_headless.sh
```

### Problème de mémoire

Si le Raspberry Pi manque de mémoire :

```bash
# Augmenter la swap
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile
# Changer CONF_SWAPSIZE=100 → CONF_SWAPSIZE=1024
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

---

## 📊 Utilisation avancée

### Accès depuis l'extérieur (Internet)

1. **Redirection de port** sur votre box :
   - Port externe : 9090
   - Port interne : 9090
   - IP : IP du Raspberry Pi

2. **Accès** : `http://[IP_PUBLIQUE]:9090/admin`

3. ⚠️ **Sécurité** :
   - Utilisez un mot de passe fort
   - Mettez en place un reverse proxy avec HTTPS (Nginx)
   - Limitez l'accès par IP si possible

### Reverse Proxy avec Nginx

```bash
sudo apt install nginx

sudo nano /etc/nginx/sites-available/pingu
```

Configuration :

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

Activer :

```bash
sudo ln -s /etc/nginx/sites-available/pingu /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Sauvegarde automatique

```bash
# Script de sauvegarde
nano ~/backup_pingu.sh
```

```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p ~/backups
tar -czf ~/backups/pingu_$DATE.tar.gz \
    ~/ping-u/tab* \
    ~/ping-u/web_users.json \
    ~/ping-u/bd/
echo "Sauvegarde créée: pingu_$DATE.tar.gz"
```

```bash
chmod +x ~/backup_pingu.sh

# Crontab (tous les jours à 2h)
crontab -e
# Ajouter: 0 2 * * * /home/user/backup_pingu.sh
```

### Monitoring des performances

```bash
# CPU/RAM
top -p $(cat pingu_headless.pid)

# Température du Raspberry Pi
vcgencmd measure_temp

# Utilisation disque
df -h
du -sh ~/ping-u

# Uptime
uptime
```

---

## 🔄 Mise à jour

```bash
cd ~/ping-u

# Sauvegarder
cp tab* web_users.json ~/backup/

# Mettre à jour
git pull
pip3 install --upgrade -r requirements.txt

# Redémarrer
./stop_headless.sh
./start_headless.sh

# Ou avec systemd
sudo systemctl restart pingu.service
```

---

## 📝 Checklist de sécurité

- [ ] Changer le mot de passe par défaut (`admin`/`admin`)
- [ ] Configurer le pare-feu (limiter l'accès au port 9090)
- [ ] Utiliser HTTPS (reverse proxy nginx)
- [ ] Sauvegardes régulières
- [ ] Mettre à jour régulièrement : `git pull && pip3 install --upgrade -r requirements.txt`
- [ ] Surveiller les logs : `tail -f logs/app.log`

---

## 📞 Support

- **Logs** : `~/ping-u/logs/app.log`
- **Documentation** : README.md
- **GitHub Issues** : Signaler un problème

---

## 💡 Astuces Raspberry Pi

### Optimisation des performances

```bash
# Désactiver le Bluetooth (si non utilisé)
echo "dtoverlay=disable-bt" | sudo tee -a /boot/config.txt

# Augmenter la mémoire GPU (si headless uniquement)
sudo raspi-config
# Advanced Options → Memory Split → 16
```

### IP fixe

```bash
# Editer dhcpcd.conf
sudo nano /etc/dhcpcd.conf

# Ajouter :
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
scp fichier.txt user@[IP_RASPBERRY]:~/ping-u/
```

---

**🎉 Votre Raspberry Pi est prêt à surveiller votre réseau 24/7 !**

