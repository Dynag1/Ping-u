# 🚀 Guide de Démarrage Rapide - Installateur Ubuntu

## Installation en 2 étapes

### Méthode recommandée (.deb)

```bash
# 1️⃣  Créer le package
./build_deb.sh

# 2️⃣  Installer
sudo dpkg -i installer/pingu_99.01.05_all.deb
sudo apt-get install -f
```

### Méthode alternative (script)

```bash
sudo ./install_ubuntu.sh
```

## Lancement de l'application

1. **Depuis le menu démarrer** : Cherchez "Ping ü" 🔍
2. **Depuis le terminal** : Tapez `pingu` ⌨️

## Désinstallation

```bash
# Si installé via .deb
sudo apt-get remove pingu

# Si installé via script
sudo ./uninstall_ubuntu.sh
```

---

## 📂 Fichiers créés

| Fichier | Description |
|---------|-------------|
| `build_deb.sh` | ⚙️ Construit le package .deb |
| `install_ubuntu.sh` | 📦 Installation directe |
| `uninstall_ubuntu.sh` | 🗑️ Désinstallation |
| `INSTALL_UBUNTU.md` | 📖 Guide complet |
| `installer_ubuntu/` | 📁 Structure du package |

## ✅ Résultat

- ✅ Logo dans le menu démarrer
- ✅ Fichiers dans `/opt/pingu/`
- ✅ Commande `pingu` disponible
- ✅ Installation/désinstallation propre

---

**Pour plus de détails** → [INSTALL_UBUNTU.md](INSTALL_UBUNTU.md)
