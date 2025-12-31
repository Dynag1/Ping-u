# 📘 Notice d'utilisation - Ping ü

**Version** : 99.02.08

Ping ü est une application de monitoring réseau disponible en deux modes :
- **Mode Application** : Interface graphique classique
- **Mode Serveur Web** : Sans interface, contrôlable via navigateur

---

## 📚 Documentation complète

Pour des guides détaillés avec captures d'écran, consultez le dossier **`docs/`** :

| Système | Mode Application | Mode Serveur Web |
|---------|------------------|------------------|
| **Windows** | [docs/installation/windows/APPLICATION.md](docs/installation/windows/APPLICATION.md) | [docs/installation/windows/SERVEUR_WEB.md](docs/installation/windows/SERVEUR_WEB.md) |
| **Linux** | [docs/installation/linux/APPLICATION.md](docs/installation/linux/APPLICATION.md) | [docs/installation/linux/SERVEUR_WEB.md](docs/installation/linux/SERVEUR_WEB.md) |

---

## 🚀 Démarrage rapide

### Windows - Application

```batch
REM Double-cliquez sur l'exécutable
Ping_u.exe
```

### Windows - Serveur Web

```batch
REM Démarrer
start_headless.bat

REM Arrêter
stop_headless.bat

REM Accès : http://localhost:9090/admin
```

### Linux - Application

```bash
source .venv/bin/activate
python3 Pingu.py
```

### Linux - Serveur Web

```bash
# Démarrer
./start_headless.sh

# Arrêter
./stop_headless.sh

# Accès : http://localhost:9090/admin
```

---

## 🔐 Identifiants par défaut

| Champ | Valeur |
|-------|--------|
| Utilisateur | `admin` |
| Mot de passe | `a` |

⚠️ **Changez ces identifiants immédiatement** via l'interface web !

---

## 🖥️ Interface Web

**URL locale** : http://localhost:9090/admin  
**URL réseau** : http://[VOTRE_IP]:9090/admin

### Fonctionnalités

| Fonction | Description | Licence requise |
|----------|-------------|-----------------|
| Monitoring | Surveiller les hôtes | ❌ Non |
| Alertes Popup | Notifications navigateur | ❌ Non |
| Alertes Email | Envoi SMTP | ✅ Oui |
| Alertes Telegram | Bot Telegram | ✅ Oui |
| Mail Récap | Email programmé | ✅ Oui |

---

## ⚙️ Configuration système

### Linux - Permissions ping

```bash
sudo sysctl -w net.ipv4.ping_group_range="0 2147483647"
echo "net.ipv4.ping_group_range=0 2147483647" | sudo tee -a /etc/sysctl.conf
```

### Windows - Pare-feu

```powershell
netsh advfirewall firewall add rule name="Ping U Web" dir=in action=allow protocol=TCP localport=9090
```

---

## 🐛 Dépannage rapide

| Problème | Solution |
|----------|----------|
| Interface web inaccessible | Vérifiez le pare-feu (port 9090) |
| Mot de passe oublié | Supprimez `web_users.json` |
| Pings ne fonctionnent pas | Vérifiez les permissions (Linux) |
| Erreurs | Consultez `logs/app.log` |

---

## 📁 Fichiers importants

| Fichier | Description |
|---------|-------------|
| `logs/app.log` | Logs de l'application |
| `web_users.json` | Identifiants web |
| `bd/autosave.pin` | Sauvegarde automatique |
| `tab*` | Configuration |

---

## 📞 Support

- **Logs** : `logs/app.log`
- **Documentation** : [docs/](docs/)
- **Site web** : https://prog.dynag.co

---

**🎉 Bon monitoring !**

