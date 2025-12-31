# Installation Ubuntu pour Ping ü

Ce guide explique comment créer et installer Ping ü sur Ubuntu/Debian.

## 🚀 Installation rapide

### Option 1 : Installation via le package .deb (Recommandé)

1. **Construire le package .deb** :
   ```bash
   ./build_deb.sh
   ```

2. **Installer le package** :
   ```bash
   sudo dpkg -i installer/pingu_99.01.05_all.deb
   sudo apt-get install -f  # Installe les dépendances manquantes
   ```

3. **Lancer l'application** :
   - Depuis le menu Applications : Cherchez "Ping ü"
   - Depuis le terminal : `pingu`

### Option 2 : Installation manuelle

Si vous préférez installer manuellement sans créer de package :

```bash
# Créer le répertoire d'installation
sudo mkdir -p /opt/pingu

# Copier les fichiers
sudo cp -r . /opt/pingu/
sudo cp installer_ubuntu/opt/pingu/pingu.sh /opt/pingu/

# Installer l'icône et le fichier .desktop
sudo cp logoP.png /usr/share/pixmaps/pingu.png
sudo cp installer_ubuntu/usr/share/applications/pingu.desktop /usr/share/applications/

# Créer un environnement virtuel et installer les dépendances
cd /opt/pingu
sudo python3 -m venv .venv
sudo .venv/bin/pip install -r requirements.txt

# Créer le lien symbolique
sudo ln -s /opt/pingu/pingu.sh /usr/local/bin/pingu

# Définir les permissions
sudo chmod +x /opt/pingu/pingu.sh
sudo chmod -R 755 /opt/pingu

# Mettre à jour la base de données des applications
sudo update-desktop-database
```

---

## 📦 Structure d'installation

Après l'installation, les fichiers seront organisés comme suit :

```
/opt/pingu/                              # Application principale
├── Pingu.py                             # Point d'entrée
├── src/                                 # Code source
├── requirements.txt                     # Dépendances Python
├── .venv/                              # Environnement virtuel Python
├── bd/                                  # Bases de données
├── logs/                                # Fichiers de logs
├── fichier/plugin/                      # Plugins
└── pingu.sh                             # Script de lancement

/usr/share/applications/pingu.desktop    # Entrée dans le menu Applications
/usr/share/pixmaps/pingu.png            # Icône de l'application
/usr/local/bin/pingu                     # Lien symbolique pour lancer depuis le terminal
```

---

## 🔧 Dépendances

### Dépendances système
- Python 3.8 ou supérieur
- python3-pip
- python3-venv

### Installation des dépendances système
```bash
sudo apt-get update
sudo apt-get install python3 python3-pip python3-venv
```

### Dépendances Python
Toutes les dépendances Python sont installées automatiquement lors de l'installation :
- PySide6 (Qt pour Python)
- Flask et Flask-SocketIO (serveur web)
- asyncio
- pysnmp
- openpyxl
- Et autres (voir requirements.txt)

---

## 🗑️ Désinstallation

### Si installé via .deb
```bash
sudo apt-get remove pingu
```

### Si installé manuellement
```bash
sudo rm -rf /opt/pingu
sudo rm /usr/share/applications/pingu.desktop
sudo rm /usr/share/pixmaps/pingu.png
sudo rm /usr/local/bin/pingu
sudo update-desktop-database
```

---

## 🐛 Dépannage

### L'application n'apparaît pas dans le menu
```bash
sudo update-desktop-database
```
Déconnectez-vous puis reconnectez-vous, ou redémarrez votre session.

### Erreur de permissions
```bash
sudo chmod -R 755 /opt/pingu
sudo chmod +x /opt/pingu/pingu.sh
```

### L'environnement virtuel n'est pas créé
```bash
cd /opt/pingu
sudo python3 -m venv .venv
sudo .venv/bin/pip install -r requirements.txt
```

### Vérifier les logs
```bash
cat /opt/pingu/logs/app.log
```

---

## 📝 Notes

- L'application s'installe dans `/opt/pingu/` pour suivre les conventions Linux (FHS - Filesystem Hierarchy Standard)
- Un environnement virtuel Python est créé pour isoler les dépendances
- L'icône apparaît dans le menu Applications sous la catégorie "Réseau" ou "Utilitaires"
- Vous pouvez lancer l'application en tapant simplement `pingu` dans un terminal

---

## 🔐 Permissions

L'application nécessite des privilèges root pour certaines opérations réseau (ping, scan). Le script de lancement gère automatiquement ces permissions si nécessaire.

---

## 📞 Support

Pour plus d'informations, consultez le [README principal](README.md) ou visitez [prog.dynag.co](https://prog.dynag.co)
