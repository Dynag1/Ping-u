# 🐧 Ping ü - Installation Linux (Mode Serveur Web)

Guide complet pour déployer Ping ü en mode serveur web (headless) sur Linux.

---

## 📋 Sommaire

1. [Qu'est-ce que le mode serveur web ?](#quest-ce-que-le-mode-serveur-web)
2. [Prérequis](#prérequis)
3. [Installation](#installation)
4. [Configuration système](#configuration-système)
5. [Démarrage du serveur](#démarrage-du-serveur)
6. [Interface web](#interface-web)
7. [Service systemd](#service-systemd)
8. [Sécurité](#sécurité)
9. [Reverse Proxy Nginx](#reverse-proxy-nginx)
10. [Docker](#docker)
11. [Dépannage](#dépannage)

---

## 💡 Qu'est-ce que le mode serveur web ?

Le **mode serveur web** (headless) permet d'exécuter Ping ü **sans interface graphique**. Parfait pour :

| Cas d'usage | Avantage |
|-------------|----------|
| Serveur sans écran | Pas besoin de X11 |
| Raspberry Pi | Faibles ressources |
| VPS/Cloud | Accès web uniquement |
| Monitoring 24/7 | Service automatique |

---

## 🔧 Prérequis

### Système

| Élément | Requis |
|---------|--------|
| Distribution | Ubuntu 20.04+, Debian 11+, Fedora 35+, Raspberry Pi OS |
| RAM | 512 Mo minimum |
| Python | 3.9 ou supérieur |
| Port | 9090 disponible |

### Installation des paquets

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv git curl

# Fedora/RHEL
sudo dnf install python3 python3-pip git curl

# Arch Linux
sudo pacman -S python python-pip git curl
```

---

## 📦 Installation

### Étape 1 : Télécharger le projet

```bash
# Cloner
git clone https://github.com/votre-repo/ping-u.git
cd ping-u

# Ou télécharger
wget https://url/ping-u.tar.gz
tar -xzf ping-u.tar.gz
cd ping-u
```

### Étape 2 : Environnement virtuel

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Étape 3 : Rendre les scripts exécutables

```bash
chmod +x start_headless.sh stop_headless.sh
chmod +x cleanup_raspberry.sh  # Si Raspberry Pi
```

---

## ⚙️ Configuration système

### Permissions ping (OBLIGATOIRE)

```bash
# Autoriser les pings sans sudo
sudo sysctl -w net.ipv4.ping_group_range="0 2147483647"

# Rendre permanent
echo "net.ipv4.ping_group_range=0 2147483647" | sudo tee -a /etc/sysctl.conf
sudo sysctl -p

# Vérifier
ping -c 1 8.8.8.8  # Doit fonctionner sans sudo
```

### Ouvrir le pare-feu

```bash
# UFW (Ubuntu/Debian)
sudo ufw allow 9090/tcp
sudo ufw status

# firewalld (Fedora/RHEL)
sudo firewall-cmd --permanent --add-port=9090/tcp
sudo firewall-cmd --reload

# iptables (manuel)
sudo iptables -A INPUT -p tcp --dport 9090 -j ACCEPT
```

---

## ▶️ Démarrage du serveur

### Méthode 1 : Script (Recommandé)

```bash
# Démarrer
./start_headless.sh

# Arrêter
./stop_headless.sh
```

![Démarrage serveur](../screenshots/linux_web_01_start.png)
*Démarrage du serveur en mode headless*

### Méthode 2 : Commande directe

```bash
# Premier plan (pour debug)
python3 Pingu.py --headless

# Arrière-plan avec logs
nohup python3 Pingu.py --headless > pingu_headless.log 2>&1 &

# Arrêter
python3 Pingu.py -stop
```

### Méthode 3 : Screen/Tmux

```bash
# Avec screen
screen -S pingu
python3 Pingu.py --headless
# Ctrl+A puis D pour détacher

# Réattacher
screen -r pingu
```

### Vérifier le serveur

```bash
# Processus actif ?
ps aux | grep Pingu

# Port ouvert ?
ss -tlnp | grep 9090

# Logs
tail -f logs/app.log
```

---

## 🖥️ Interface web

### Accès

| Type | URL |
|------|-----|
| Local | http://localhost:9090/admin |
| Réseau | http://[IP_SERVEUR]:9090/admin |

### Trouver l'IP du serveur

```bash
# IP locale
hostname -I | awk '{print $1}'

# Ou
ip addr show | grep "inet " | grep -v 127.0.0.1
```

### Connexion

![Page de connexion](../screenshots/linux_web_02_login.png)
*Page de connexion*

| Champ | Valeur par défaut |
|-------|-------------------|
| Utilisateur | `admin` |
| Mot de passe | `a` |

⚠️ **Changez immédiatement ces identifiants !**

### Tableau de bord

![Dashboard](../screenshots/linux_web_03_dashboard.png)
*Interface d'administration web*

---

## 🔧 Service systemd

### Créer le fichier service

```bash
sudo nano /etc/systemd/system/pingu.service
```

### Contenu du fichier

```ini
[Unit]
Description=Ping ü - Monitoring Réseau
After=network.target
Wants=network-online.target

[Service]
Type=simple
User=votre_utilisateur
WorkingDirectory=/home/votre_utilisateur/ping-u
Environment="PATH=/home/votre_utilisateur/ping-u/.venv/bin"
ExecStart=/home/votre_utilisateur/ping-u/.venv/bin/python /home/votre_utilisateur/ping-u/Pingu.py --headless
ExecStop=/home/votre_utilisateur/ping-u/.venv/bin/python /home/votre_utilisateur/ping-u/Pingu.py -stop
Restart=on-failure
RestartSec=10
StandardOutput=append:/home/votre_utilisateur/ping-u/pingu_headless.log
StandardError=append:/home/votre_utilisateur/ping-u/pingu_headless.log

[Install]
WantedBy=multi-user.target
```

⚠️ **Remplacez** `votre_utilisateur` par votre nom d'utilisateur réel.

### Activer le service

```bash
# Recharger systemd
sudo systemctl daemon-reload

# Activer au démarrage
sudo systemctl enable pingu.service

# Démarrer maintenant
sudo systemctl start pingu.service

# Vérifier le statut
sudo systemctl status pingu.service
```

### Commandes utiles

```bash
# Arrêter
sudo systemctl stop pingu.service

# Redémarrer
sudo systemctl restart pingu.service

# Voir les logs
sudo journalctl -u pingu.service -f

# Logs des dernières 24h
sudo journalctl -u pingu.service --since "24 hours ago"
```

---

## 🔐 Sécurité

### Changer les identifiants

1. Connectez-vous à l'interface web
2. Cliquez sur **"Changer identifiants"**
3. Définissez un mot de passe **fort**

### Réinitialiser les identifiants

```bash
# Si mot de passe oublié
rm web_users.json
sudo systemctl restart pingu.service
# Identifiants réinitialisés : admin / a
```

### Limiter l'accès par IP (pare-feu)

```bash
# UFW : autoriser seulement le réseau local
sudo ufw allow from 192.168.1.0/24 to any port 9090
sudo ufw deny 9090  # Bloquer les autres

# iptables
sudo iptables -A INPUT -p tcp -s 192.168.1.0/24 --dport 9090 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 9090 -j DROP
```

---

## 🌐 Reverse Proxy Nginx

### Installation Nginx

```bash
sudo apt install nginx
```

### Configuration

```bash
sudo nano /etc/nginx/sites-available/pingu
```

```nginx
server {
    listen 80;
    server_name monitoring.votredomaine.com;  # Ou IP

    location / {
        proxy_pass http://127.0.0.1:9090;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;  # WebSocket timeout
    }
}
```

### Activer le site

```bash
sudo ln -s /etc/nginx/sites-available/pingu /etc/nginx/sites-enabled/
sudo nginx -t  # Tester la config
sudo systemctl restart nginx
```

### Ajouter HTTPS avec Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d monitoring.votredomaine.com
```

---

## 🐳 Docker

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    iputils-ping \
    && rm -rf /var/lib/apt/lists/*

# Copier les requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier l'application
COPY . .

# Port web
EXPOSE 9090

# Volumes pour la persistance
VOLUME ["/app/bd", "/app/logs"]

# Lancement
CMD ["python", "Pingu.py", "--headless"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  pingu:
    build: .
    container_name: pingu
    restart: unless-stopped
    ports:
      - "9090:9090"
    volumes:
      - ./bd:/app/bd
      - ./logs:/app/logs
      - ./web_users.json:/app/web_users.json
    cap_add:
      - NET_RAW  # Pour les pings ICMP
```

### Commandes Docker

```bash
# Construire
docker-compose build

# Lancer
docker-compose up -d

# Logs
docker-compose logs -f

# Arrêter
docker-compose down
```

---

## 📊 Monitoring du serveur

### Vérifier l'état

```bash
# CPU/RAM du processus
ps aux | grep Pingu

# Utilisation détaillée
top -p $(cat pingu_headless.pid)

# Espace disque
du -sh ~/ping-u
du -sh ~/ping-u/logs
```

### Logs

```bash
# Logs temps réel
tail -f logs/app.log

# Erreurs uniquement
grep -i error logs/app.log

# Logs du jour
grep "$(date +%Y-%m-%d)" logs/app.log
```

### Rotation des logs

```bash
# Créer la config logrotate
sudo nano /etc/logrotate.d/pingu
```

```
/home/votre_utilisateur/ping-u/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 644 votre_utilisateur votre_utilisateur
}
```

---

## 🐛 Dépannage

### Le serveur ne démarre pas

```bash
# Vérifier les erreurs
cat logs/app.log | tail -50

# Port déjà utilisé ?
ss -tlnp | grep 9090

# Libérer le port
sudo kill $(sudo lsof -t -i:9090)
```

### Erreur "Operation not permitted"

```bash
sudo sysctl -w net.ipv4.ping_group_range="0 2147483647"
```

### Interface web inaccessible

```bash
# Serveur actif ?
curl http://localhost:9090/api/status

# Pare-feu ?
sudo ufw status
sudo firewall-cmd --list-ports

# Logs réseau
sudo tcpdump -i any port 9090
```

### Service systemd ne démarre pas

```bash
# Voir les erreurs
sudo journalctl -u pingu.service -n 50 --no-pager

# Tester manuellement
sudo -u votre_utilisateur /home/votre_utilisateur/ping-u/.venv/bin/python /home/votre_utilisateur/ping-u/Pingu.py --headless
```

### Raspberry Pi : script de nettoyage

```bash
# Si le port reste bloqué
./cleanup_raspberry.sh
```

---

## 📁 Fichiers importants

| Fichier | Description |
|---------|-------------|
| `pingu_headless.pid` | PID du processus |
| `pingu_headless.log` | Logs du mode headless |
| `logs/app.log` | Logs applicatifs |
| `web_users.json` | Identifiants web |
| `bd/autosave.pin` | Sauvegarde auto des hôtes |
| `tab*` | Configuration |

---

## 🔄 Mise à jour

```bash
# Arrêter le service
sudo systemctl stop pingu.service

# Sauvegarder
cp -r bd/ web_users.json tab* ~/backup_pingu/

# Mettre à jour
cd ~/ping-u
git pull
source .venv/bin/activate
pip install --upgrade -r requirements.txt

# Redémarrer
sudo systemctl start pingu.service
```

---

## 📞 Support

| Ressource | Emplacement |
|-----------|-------------|
| Logs | `logs/app.log` |
| Statut service | `sudo systemctl status pingu` |
| Documentation | README.md |
| Site web | https://prog.dynag.co |

---

**🎉 Bon monitoring sur Linux !**

