# 📚 Documentation Ping ü

Bienvenue dans la documentation de **Ping ü** - Application de monitoring réseau.

---

## 📁 Structure de la documentation

```
docs/
├── README.md                    # Ce fichier
├── installation/
│   ├── windows/
│   │   ├── APPLICATION.md       # Windows - Mode application bureau
│   │   └── SERVEUR_WEB.md       # Windows - Mode serveur web (headless)
│   └── linux/
│       ├── APPLICATION.md       # Linux - Mode application bureau
│       └── SERVEUR_WEB.md       # Linux - Mode serveur web (headless)
└── screenshots/
    └── README.md                # Guide des captures d'écran
```

---

## 🎯 Quel guide choisir ?

### Par système d'exploitation

| Système | Guide |
|---------|-------|
| Windows 10/11 | [windows/](installation/windows/) |
| Linux (Ubuntu, Debian, Fedora) | [linux/](installation/linux/) |
| Raspberry Pi | [linux/SERVEUR_WEB.md](installation/linux/SERVEUR_WEB.md) |

### Par mode d'utilisation

| Mode | Description | Guides |
|------|-------------|--------|
| **Application** | Interface graphique classique | [Windows](installation/windows/APPLICATION.md) • [Linux](installation/linux/APPLICATION.md) |
| **Serveur Web** | Sans interface, accès via navigateur | [Windows](installation/windows/SERVEUR_WEB.md) • [Linux](installation/linux/SERVEUR_WEB.md) |

---

## 🆚 Comparatif des modes

| Caractéristique | Mode Application | Mode Serveur Web |
|-----------------|------------------|------------------|
| Interface | Fenêtre graphique Qt | Navigateur web |
| Ressources | ~200 Mo RAM | ~100 Mo RAM |
| Accès distant | Non (sauf serveur web intégré) | Oui |
| Multi-utilisateurs | Non | Oui |
| Idéal pour | Utilisation quotidienne | Serveur 24/7 |
| Démarrage auto | Manuel | Service systemd |

---

## 🚀 Guides rapides

### Windows - Application

```batch
REM Installer et lancer
PingU_Setup.exe
REM Double-clic sur Ping_u.exe
```

### Windows - Serveur Web

```batch
REM Démarrer le serveur
start_headless.bat
REM Accéder : http://localhost:9090/admin
```

### Linux - Application

```bash
python3 Pingu.py
```

### Linux - Serveur Web

```bash
./start_headless.sh
# Accéder : http://localhost:9090/admin
```

---

## 📖 Table des matières par guide

### Windows Application
- Installation (installateur, portable, code source)
- Interface principale
- Ajouter des hôtes
- Démarrer le monitoring
- Configurer les alertes
- Exporter/Importer

### Windows Serveur Web
- Démarrage du serveur
- Interface web d'administration
- Gestion des hôtes
- Démarrage automatique
- Sécurité et pare-feu

### Linux Application
- Installation et dépendances
- Configuration système (ping)
- Interface graphique
- Alertes et notifications

### Linux Serveur Web
- Installation headless
- Service systemd
- Reverse proxy Nginx
- Déploiement Docker
- Sécurisation

---

## 🔗 Liens utiles

| Ressource | URL |
|-----------|-----|
| Site officiel | https://prog.dynag.co |
| GitHub | https://github.com/votre-repo/ping-u |
| Changelog | [../Changelog.md](../Changelog.md) |
| Licence | [../LICENSE.txt](../LICENSE.txt) |

---

## 🖼️ Captures d'écran

Les captures d'écran référencées dans les guides se trouvent dans le dossier [`screenshots/`](screenshots/).

Pour générer les captures d'écran, consultez le guide : [screenshots/README.md](screenshots/README.md)

---

## 🆘 Support

En cas de problème :

1. Consultez les **logs** : `logs/app.log`
2. Vérifiez le guide de **dépannage** dans chaque documentation
3. Ouvrez une **issue** sur GitHub
4. Contactez le support : https://prog.dynag.co

---

**📝 Version de la documentation : 99.02.08**

