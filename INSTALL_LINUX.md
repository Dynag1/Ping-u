# 🐧 Installation et Utilisation - Linux

Guide complet pour installer et utiliser Ping ü sur Linux (Ubuntu, Debian, Fedora, etc.).

---

## 📋 Table des matières

1. [Installation](#installation)
2. [Premier lancement](#premier-lancement)
3. [Mode Headless](#mode-headless)
4. [Interface Web](#interface-web)
5. [Configuration](#configuration)
6. [Service systemd](#service-systemd)
7. [Dépannage](#dépannage)

---

## 🚀 Installation

### Prérequis

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv git

# Fedora/RHEL
sudo dnf install python3 python3-pip git

# Arch Linux
sudo pacman -S python python-pip git
```

### Installation

```bash
# Cloner le dépôt
git clone [URL_DU_REPO]
cd ping-u

# Créer un environnement virtuel (optionnel mais recommandé)
python3 -m venv .venv
source .venv/bin/activate

# Installer les dépendances
pip3 install -r requirements.txt
```

---

## 🎯 Premier lancement

### Mode Interface Graphique

```bash
python3 Pingu.py
```

L'interface Qt s'ouvre avec toutes les fonctionnalités :
- Monitoring ping temps réel
- Alertes configurables
- Export/Import CSV et Excel
- SNMP (température, débits)

---

## 🌐 Mode Headless

Mode sans interface graphique, parfait pour un serveur.

### Démarrage

```bash
# Méthode 1: Via le script (recommandé)
chmod +x start_headless.sh stop_headless.sh
./start_headless.sh

# Méthode 2: Commande directe
python3 Pingu.py --headless

# Méthode 3: En arrière-plan avec logs
nohup python3 Pingu.py --headless > pingu_headless.log 2>&1 &
```

### Arrêt

```bash
# Méthode 1: Via le script
./stop_headless.sh

# Méthode 2: Commande directe
python3 Pingu.py -stop

# Méthode 3: Signal
kill -SIGTERM $(cat pingu_headless.pid)
```

### Logs

```bash
# Logs temps réel
tail -f pingu_headless.log

# Logs applicatifs détaillés
tail -f logs/app.log

# Erreurs uniquement
grep -i error logs/app.log
```

---

## 🖥️ Interface Web

Accessible quand le mode headless est actif.

### Accès

**Local** : http://localhost:9090/admin  
**Réseau** : http://[VOTRE_IP]:9090/admin

**Identifiants par défaut** : `admin` / `admin`  
⚠️ **Changez-les immédiatement !**

### Fonctionnalités

- ✅ Gestion complète des hôtes
- ✅ Monitoring en temps réel
- ✅ Configuration des alertes
- ✅ Export/Import CSV
- ✅ Statistiques live
- ✅ Notifications navigateur

---

## ⚙️ Configuration

### Permissions ping

Sur Linux, les pings ICMP nécessitent des permissions spéciales :

```bash
# Méthode 1: Autoriser tous les utilisateurs (recommandé)
sudo sysctl -w net.ipv4.ping_group_range="0 2147483647"

# Rendre permanent
echo "net.ipv4.ping_group_range=0 2147483647" | sudo tee -a /etc/sysctl.conf
sudo sysctl -p

# Méthode 2: Capacités Linux
sudo setcap cap_net_raw+ep $(which python3)
```

### Configuration Email

Via l'interface web : http://localhost:9090/admin → Onglet "Email"

**Exemple Gmail** :
- Serveur : `smtp.gmail.com`
- Port : `587`
- Email : votre@gmail.com
- Mot de passe : Mot de passe d'application Google

### Configuration Telegram

1. Créez un bot : @BotFather sur Telegram
2. Interface web → Onglet "Telegram"
3. Collez Token et Chat ID

### SNMP (optionnel)

```bash
# Installer snmp-tools pour tests
sudo apt install snmp snmp-mibs-downloader

# Tester un équipement
snmpwalk -v2c -c public 192.168.1.1 system
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
User=VOTRE_UTILISATEUR
WorkingDirectory=/chemin/vers/ping-u
ExecStart=/usr/bin/python3 /chemin/vers/ping-u/Pingu.py --headless
ExecStop=/usr/bin/python3 /chemin/vers/ping-u/Pingu.py -stop
Restart=on-failure
RestartSec=10
StandardOutput=append:/chemin/vers/ping-u/pingu_headless.log
StandardError=append:/chemin/vers/ping-u/pingu_headless.log

[Install]
WantedBy=multi-user.target
```

⚠️ **Remplacez** :
- `VOTRE_UTILISATEUR` par votre nom d'utilisateur
- `/chemin/vers/ping-u` par le chemin réel

### 3. Activer et démarrer

```bash
# Recharger systemd
sudo systemctl daemon-reload

# Activer au démarrage
sudo systemctl enable pingu.service

# Démarrer maintenant
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

# Désactiver le démarrage auto
sudo systemctl disable pingu.service

# Voir les logs des 24h
sudo journalctl -u pingu.service --since "24 hours ago"
```

---

## 🔒 Pare-feu

### UFW (Ubuntu/Debian)

```bash
# Autoriser le port 9090
sudo ufw allow 9090/tcp

# Vérifier
sudo ufw status
```

### firewalld (Fedora/RHEL)

```bash
# Autoriser le port
sudo firewall-cmd --permanent --add-port=9090/tcp
sudo firewall-cmd --reload

# Vérifier
sudo firewall-cmd --list-ports
```

---

## 🐛 Dépannage

### Erreur "Operation not permitted" lors des pings

```bash
# Solution
sudo sysctl -w net.ipv4.ping_group_range="0 2147483647"
echo "net.ipv4.ping_group_range=0 2147483647" | sudo tee -a /etc/sysctl.conf
```

### L'application ne démarre pas

```bash
# Vérifier Python
python3 --version

# Réinstaller les dépendances
pip3 install --upgrade -r requirements.txt

# Vérifier les logs
tail -50 logs/app.log
```

### Port 9090 déjà utilisé

```bash
# Trouver le processus
sudo lsof -i :9090

# Tuer le processus
sudo kill -9 [PID]

# Ou changer le port dans Pingu.py
```

### SNMP ne fonctionne pas

```bash
# Installer pysnmp-lextudio
pip3 uninstall -y pysnmp
pip3 install pysnmp-lextudio pyasn1 pyasn1-modules pycryptodomex

# Redémarrer
./stop_headless.sh
./start_headless.sh
```

### Vérifier que tout fonctionne

```bash
# 1. Ping système
ping -c 1 8.8.8.8

# 2. Processus actif
ps aux | grep Pingu

# 3. Port ouvert
ss -tlnp | grep 9090

# 4. API web
curl http://localhost:9090/api/status
```

---

## 📊 Utilisation avancée

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
# Créer un script de sauvegarde
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

# Ajouter à crontab (tous les jours à 2h)
crontab -e
# Ajouter: 0 2 * * * /home/VOTRE_USER/backup_pingu.sh
```

### Monitoring des performances

```bash
# CPU/RAM
top -p $(cat pingu_headless.pid)

# Utilisation disque
du -sh ~/ping-u

# Logs par jour
ls -lh pingu_headless.log logs/app.log
```

---

## 🔄 Mise à jour

```bash
cd ~/ping-u

# Sauvegarder la config
cp tab* web_users.json ~/backup/

# Mise à jour
git pull
pip3 install --upgrade -r requirements.txt

# Redémarrer
./stop_headless.sh
./start_headless.sh

# Ou avec systemd
sudo systemctl restart pingu.service
```

---

## 🐳 Docker (optionnel)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 9090

CMD ["python", "Pingu.py", "--headless"]
```

```bash
# Build
docker build -t pingu .

# Run
docker run -d -p 9090:9090 --name pingu pingu

# Logs
docker logs -f pingu

# Stop
docker stop pingu
```

---

## 📞 Support

- **Logs** : `logs/app.log`
- **Documentation** : README.md
- **GitHub Issues** : Signaler un problème

---

**🎉 Bon monitoring !**

