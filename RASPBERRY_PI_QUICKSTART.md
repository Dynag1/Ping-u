# 🍓 Guide Rapide - Ping ü sur Raspberry Pi

## 🚀 Installation en 3 étapes

### Étape 1 : Transférer les fichiers

```bash
# Sur votre PC, transférer vers le Raspberry Pi
scp -r ping-u/ dynag@nextcloudpi:~/

# Ou via git
git clone [URL_DU_REPO] ~/ping-u
cd ~/ping-u
```

### Étape 2 : Installation des dépendances

```bash
cd ~/ping-u

# Installer Python 3 et pip (si nécessaire)
sudo apt update
sudo apt install -y python3 python3-pip python3-venv

# Installer les dépendances
pip3 install -r requirements.txt
```

### Étape 3 : Correction automatique

```bash
# Rendre le script exécutable
chmod +x fix_raspberry.sh start_headless.sh stop_headless.sh

# Exécuter la correction (configure les permissions ping + crée les fichiers)
./fix_raspberry.sh
```

✅ **C'est tout !** L'application est prête à démarrer.

---

## 🎯 Démarrage

```bash
cd ~/ping-u

# Démarrer l'application
./start_headless.sh

# Vérifier que tout fonctionne
tail -f pingu_headless.log
```

L'interface web est accessible à : `http://[IP_RASPBERRY]:5000`

**Identifiants par défaut** : `admin` / `admin`

---

## ⚠️ Problèmes et Solutions

### Problème 1 : "[Errno 1] Operation not permitted"

**Cause** : Les permissions ping ne sont pas configurées

**Solution** :
```bash
sudo sysctl -w net.ipv4.ping_group_range="0 2147483647"
echo "net.ipv4.ping_group_range=0 2147483647" | sudo tee -a /etc/sysctl.conf
```

### Problème 2 : "Fichier tab non trouvé" / "Fichier tabG non trouvé"

**Cause** : Fichiers de configuration manquants

**Solution** :
```bash
python3 init_raspberry.py
```

### Problème 3 : "write() before start_response" (erreur Flask)

**Cause** : Bug dans une ancienne version

**Solution** : Mettre à jour vers la dernière version du code (ce bug a été corrigé)

### Problème 4 : Import error "No module named 'PySide6'"

**Cause** : Dépendances non installées

**Solution** :
```bash
pip3 install -r requirements.txt
# ou spécifiquement
pip3 install PySide6 flask flask-socketio flask-cors
```

---

## 🔄 Utilisation

### Démarrer/Arrêter

```bash
# Démarrer
./start_headless.sh

# Arrêter
./stop_headless.sh

# Vérifier le statut
ps aux | grep Pingu
```

### Voir les logs

```bash
# Logs temps réel
tail -f pingu_headless.log

# Logs applicatifs
tail -f logs/app.log

# Erreurs uniquement
grep -i error pingu_headless.log
```

### Redémarrer après modification

```bash
./stop_headless.sh
./start_headless.sh
tail -f pingu_headless.log
```

---

## 🚀 Démarrage automatique au boot

### Méthode 1 : systemd (recommandé)

```bash
# Créer le fichier service
sudo nano /etc/systemd/system/pingu.service
```

Contenu du fichier :

```ini
[Unit]
Description=Ping ü - Monitoring Réseau
After=network.target

[Service]
Type=simple
User=dynag
WorkingDirectory=/home/dynag/ping-u
ExecStart=/usr/bin/python3 /home/dynag/ping-u/Pingu.py -start
ExecStop=/usr/bin/python3 /home/dynag/ping-u/Pingu.py -stop
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Activer le service :

```bash
sudo systemctl daemon-reload
sudo systemctl enable pingu.service
sudo systemctl start pingu.service
sudo systemctl status pingu.service
```

### Méthode 2 : crontab

```bash
# Éditer crontab
crontab -e

# Ajouter cette ligne
@reboot cd /home/dynag/ping-u && ./start_headless.sh
```

---

## 🔍 Diagnostics

### Vérifier que tout fonctionne

```bash
# 1. Ping fonctionne ?
ping -c 1 8.8.8.8

# 2. Processus actif ?
ps aux | grep Pingu

# 3. Port 5000 ouvert ?
netstat -tlnp | grep 5000
# ou
ss -tlnp | grep 5000

# 4. Logs OK ?
tail -20 pingu_headless.log

# 5. Accès web ?
curl http://localhost:5000/api/status
```

### Résolution des problèmes courants

```bash
# Port déjà utilisé
sudo lsof -i :5000
# Tuer le processus si nécessaire
sudo kill -9 [PID]

# Forcer l'arrêt
kill -9 $(cat pingu_headless.pid)
rm pingu_headless.pid

# Réinstaller les dépendances
pip3 install --upgrade --force-reinstall -r requirements.txt

# Nettoyer les fichiers temporaires
rm -f pingu_headless.pid
rm -f pingu_headless.log

# Tout réinitialiser
./stop_headless.sh
./fix_raspberry.sh
./start_headless.sh
```

---

## 📊 Configuration avancée

### Changer le port par défaut (5000 → autre)

Éditer `Pingu.py` et modifier :

```python
# Ligne ~740
web_server = WebServer(window, port=5000)  # Changer 5000
```

### Accès depuis l'extérieur (Internet)

```bash
# 1. Configurer le pare-feu
sudo ufw allow 5000

# 2. Redirection de port sur votre routeur
# Port externe: 8080 → Port interne: 5000 (IP du Raspberry)

# 3. Utiliser un reverse proxy (nginx)
sudo apt install nginx
sudo nano /etc/nginx/sites-available/pingu
```

Configuration nginx :

```nginx
server {
    listen 80;
    server_name monitoring.local;

    location / {
        proxy_pass http://localhost:5000;
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

## 📝 Fichiers importants

| Fichier | Description |
|---------|-------------|
| `tab` | Paramètres mail |
| `tabG` | Paramètres généraux (nom site, langue) |
| `tab4` | Paramètres de monitoring (délais, alertes) |
| `tabr` | Paramètres mail récapitulatif |
| `web_users.json` | Identifiants interface web |
| `pingu_headless.pid` | PID du processus |
| `pingu_headless.log` | Logs du mode headless |
| `logs/app.log` | Logs applicatifs détaillés |
| `bd/*.pin` | Sauvegardes des hôtes |

---

## 🔒 Sécurité

### Checklist de sécurité

- [ ] Changer le mot de passe par défaut (`admin` / `admin`)
- [ ] Utiliser HTTPS (reverse proxy nginx)
- [ ] Configurer le pare-feu (limiter l'accès au port 5000)
- [ ] Mettre à jour régulièrement : `pip3 install --upgrade -r requirements.txt`
- [ ] Sauvegarder les fichiers de configuration
- [ ] Surveiller les logs : `tail -f logs/app.log`

### Changer les identifiants web

Via l'interface web : `http://[IP]:5000/admin` → Onglet "Identifiants"

Ou manuellement :

```bash
python3 -c "
import json, hashlib
password = input('Nouveau mot de passe: ')
password_hash = hashlib.sha256(password.encode()).hexdigest()
data = {'username': 'admin', 'password': password_hash}
with open('web_users.json', 'w') as f:
    json.dump(data, f, indent=4)
print('✅ Mot de passe changé')
"
```

---

## 💡 Astuces

### Monitoring des performances

```bash
# Utilisation CPU/RAM
top -p $(cat pingu_headless.pid)

# Utilisation disque
du -sh ~/ping-u

# Logs par jour
ls -lh pingu_headless.log logs/app.log
```

### Sauvegarde automatique

```bash
# Créer un script de sauvegarde
nano ~/backup_pingu.sh
```

```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
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
# 0 2 * * * /home/dynag/backup_pingu.sh
```

---

## 📞 Besoin d'aide ?

- Documentation complète : [HEADLESS_MODE.md](HEADLESS_MODE.md)
- Logs détaillés : `tail -100 logs/app.log`
- GitHub Issues : [Signaler un problème]

---

**Version Raspberry Pi optimisée - Dernière mise à jour : 2025-11-30**

