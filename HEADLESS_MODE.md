# Mode Headless - Ping ü

## 📋 Description

Le mode headless permet de lancer Ping ü sans interface graphique, idéal pour :
- Serveurs Linux sans environnement graphique
- Raspberry Pi
- Conteneurs Docker
- Services en arrière-plan
- Déploiements distants

L'application reste entièrement contrôlable via l'interface web admin.

---

## ⚙️ Prérequis

Avant de démarrer en mode headless :

1. **Environnement virtuel** : L'environnement virtuel `.venv` doit être créé et contenir toutes les dépendances
   ```bash
   python -m venv .venv
   .venv/Scripts/activate  # Windows
   source .venv/bin/activate  # Linux/Mac
   pip install -r requirements.txt
   ```

2. **Port 9090** : Le port 9090 doit être libre (interface web admin)

---

## 🚀 Démarrage

### Linux / Mac

```bash
# Méthode 1: Via le script (recommandé)
chmod +x start_headless.sh stop_headless.sh
./start_headless.sh

# Méthode 2: Commande directe
python3 Pingu.py -start

# Méthode 3: En arrière-plan avec logs
nohup python3 Pingu.py -start > pingu_headless.log 2>&1 &
```

### Windows

```batch
REM Méthode 1: Via le script (recommandé)
REM Active automatiquement l'environnement virtuel .venv
start_headless.bat

REM Méthode 2: Commande directe (nécessite .venv actif)
.venv\Scripts\activate
python Pingu.py -start

REM Méthode 3: En arrière-plan (nécessite .venv actif)
.venv\Scripts\activate
start /B pythonw Pingu.py -start
```

> **💡 Astuce Windows** : Utilisez toujours `start_headless.bat` pour un démarrage sans souci. Le script active automatiquement l'environnement virtuel et gère les erreurs.

---

## 🛑 Arrêt

### Linux / Mac

```bash
# Méthode 1: Via le script
./stop_headless.sh

# Méthode 2: Commande directe
python3 Pingu.py -stop

# Méthode 3: Signal (si PID connu)
kill -SIGTERM $(cat pingu_headless.pid)
```

### Windows

```batch
REM Méthode 1: Via le script
stop_headless.bat

REM Méthode 2: Commande directe
python Pingu.py -stop
```

---

## 🌐 Accès à l'interface web

Une fois l'application démarrée :

- **URL locale** : `http://localhost:9090/admin`
- **URL réseau** : `http://<ip-du-serveur>:9090/admin`

**Identifiants par défaut** :
- Utilisateur : `admin`
- Mot de passe : `a`

⚠️ **Important** : Changez ces identifiants après la première connexion !

---

## 📊 Fonctionnalités disponibles

En mode headless, toutes les fonctionnalités sont accessibles via l'interface web :

✅ Ajout/suppression d'hôtes  
✅ Démarrage/arrêt du monitoring  
✅ Configuration des alertes  
✅ Export/import CSV  
✅ Gestion des paramètres  
✅ Changement des identifiants  

---

## 📝 Logs

### Linux / Mac
```bash
# Voir les logs en temps réel
tail -f pingu_headless.log

# Voir les logs applicatifs
tail -f logs/app.log
```

### Windows
```batch
REM Voir les logs
type pingu_headless.log

REM Voir les logs applicatifs
type logs\app.log
```

---

## 🔧 Service systemd (Linux)

Pour lancer automatiquement au démarrage sur Linux :

### 1. Créer le fichier service

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
User=votre_utilisateur
WorkingDirectory=/chemin/vers/ping-u
ExecStart=/usr/bin/python3 /chemin/vers/ping-u/Pingu.py -start
ExecStop=/usr/bin/python3 /chemin/vers/ping-u/Pingu.py -stop
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 3. Activer et démarrer le service

```bash
# Recharger systemd
sudo systemctl daemon-reload

# Activer au démarrage
sudo systemctl enable pingu.service

# Démarrer le service
sudo systemctl start pingu.service

# Vérifier le statut
sudo systemctl status pingu.service

# Voir les logs
sudo journalctl -u pingu.service -f
```

### 4. Commandes utiles

```bash
# Arrêter le service
sudo systemctl stop pingu.service

# Redémarrer le service
sudo systemctl restart pingu.service

# Désactiver le démarrage automatique
sudo systemctl disable pingu.service
```

---

## 🐳 Docker (Optionnel)

Si vous souhaitez conteneuriser l'application :

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 9090

CMD ["python", "Pingu.py", "-start"]
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

## ⚙️ Configuration

### Fichiers importants

- `web_users.json` : Identifiants de connexion web
- `logs/app.log` : Logs applicatifs
- `pingu_headless.pid` : PID du processus
- `pingu_headless.log` : Logs du mode headless
- `bd/*.pin` : Données sauvegardées

### Variables d'environnement (optionnel)

```bash
export PINGU_PORT=9090          # Port du serveur web
export PINGU_WEB_USER=admin     # Utilisateur par défaut
export PINGU_WEB_PASS=password  # Mot de passe par défaut
```

---

## 🔒 Sécurité

### Recommandations

1. **Changez les identifiants par défaut** immédiatement
2. Utilisez un **reverse proxy** (nginx, Apache) avec HTTPS
3. Configurez un **pare-feu** pour limiter l'accès au port 9090
4. Utilisez des **mots de passe forts**
5. Activez les **logs de connexion**

### Exemple nginx avec HTTPS

```nginx
server {
    listen 443 ssl;
    server_name monitoring.example.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:9090;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## 🍓 Installation spécifique Raspberry Pi

### Problème: "[Errno 1] Operation not permitted" lors des pings

Sur Raspberry Pi, les pings ICMP nécessitent des privilèges spéciaux. Utilisez le script de correction :

```bash
# Télécharger les fichiers sur votre Raspberry Pi
cd ~/ping-u

# Rendre le script exécutable
chmod +x fix_raspberry.sh

# Exécuter le script de correction (nécessite sudo pour les permissions ping)
./fix_raspberry.sh
```

### OU Configuration manuelle

#### 1. Autoriser les pings sans root
```bash
# Configuration temporaire
sudo sysctl -w net.ipv4.ping_group_range="0 2147483647"

# Configuration permanente
echo "net.ipv4.ping_group_range=0 2147483647" | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

#### 2. Créer les fichiers de configuration
```bash
# Utiliser le script d'initialisation
python3 init_raspberry.py
```

#### 3. Vérifier que tout fonctionne
```bash
# Test de ping
ping -c 1 8.8.8.8

# Démarrer l'application
./start_headless.sh

# Vérifier les logs
tail -f pingu_headless.log
```

### Problèmes courants sur Raspberry Pi

**Fichiers "tab" et "tabG" non trouvés** :
```bash
python3 init_raspberry.py
```

**"write() before start_response" (erreur Flask)** :
Cette erreur a été corrigée dans la dernière version. Assurez-vous d'avoir la dernière version du code.

**Pas assez de mémoire** :
```bash
# Augmenter la swap si nécessaire
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile  # Augmenter CONF_SWAPSIZE à 1024
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

---

## 🐛 Dépannage

### L'application ne démarre pas

```bash
# Vérifier les dépendances
pip install -r requirements.txt

# Vérifier les logs
cat pingu_headless.log
cat logs/app.log

# Vérifier si le port est occupé
lsof -i :9090  # Linux/Mac
netstat -ano | findstr :9090  # Windows
```

### Impossible de se connecter à l'interface web

```bash
# Vérifier que l'application tourne
cat pingu_headless.pid

# Vérifier le pare-feu
sudo ufw allow 9090  # Linux
```

### L'arrêt ne fonctionne pas

```bash
# Forcer l'arrêt (Linux/Mac)
kill -9 $(cat pingu_headless.pid)
rm pingu_headless.pid

# Forcer l'arrêt (Windows)
taskkill /F /PID [PID_NUMBER]
del pingu_headless.pid
```

---

## 📞 Support

Pour plus d'informations, consultez :
- [README.md](README.md) - Documentation principale
- [logs/app.log](logs/app.log) - Logs applicatifs
- GitHub Issues - Signaler un problème

---

## ✨ Avantages du mode headless

✅ Pas besoin d'interface graphique  
✅ Consommation mémoire réduite  
✅ Idéal pour serveurs  
✅ Interface web complète  
✅ Démarrage automatique possible  
✅ Logs détaillés  
✅ Arrêt propre  

---

**Note** : Le mode headless utilise une version minimale de Qt uniquement pour la gestion des données (QStandardItemModel). Aucune fenêtre graphique n'est créée.

