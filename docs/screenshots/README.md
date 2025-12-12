# 🖼️ Guide des captures d'écran

Ce dossier contient les captures d'écran utilisées dans la documentation.

---

## 📁 Organisation des fichiers

### Nomenclature

Les fichiers suivent la convention : `{os}_{mode}_{numero}_{description}.png`

| Préfixe | Système |
|---------|---------|
| `windows_` | Windows |
| `linux_` | Linux |

| Mode | Description |
|------|-------------|
| `app_` | Mode application |
| `web_` | Mode serveur web |
| `install_` | Installation |

### Exemples

```
windows_app_01_main.png        # Windows, application, interface principale
windows_web_03_dashboard.png   # Windows, web, tableau de bord
linux_app_02_add.png          # Linux, application, ajout d'hôte
```

---

## 📋 Liste des captures requises

### Windows - Application

| Fichier | Description |
|---------|-------------|
| `windows_install_01.png` | Écran d'installation (assistant) |
| `windows_app_01_main.png` | Interface principale |
| `windows_app_02_add.png` | Formulaire d'ajout d'hôte |
| `windows_app_03_scan.png` | Scan de plage d'adresses |
| `windows_app_04_monitoring.png` | Monitoring actif (tableau coloré) |
| `windows_app_05_alerts.png` | Configuration des alertes |
| `windows_app_06_webserver.png` | Menu serveur web intégré |

### Windows - Serveur Web

| Fichier | Description |
|---------|-------------|
| `windows_web_01_start.png` | Démarrage headless (terminal) |
| `windows_web_02_login.png` | Page de connexion web |
| `windows_web_03_dashboard.png` | Tableau de bord admin |
| `windows_web_04_add_host.png` | Formulaire ajout hôte (web) |
| `windows_web_05_scan.png` | Scan réseau (web) |
| `windows_web_06_monitoring.png` | Contrôle du monitoring |
| `windows_web_07_alerts.png` | Configuration alertes (web) |
| `windows_web_08_credentials.png` | Changement identifiants |
| `windows_web_09_scheduler.png` | Planificateur de tâches |

### Linux - Application

| Fichier | Description |
|---------|-------------|
| `linux_app_01_main.png` | Interface principale KDE/GNOME |
| `linux_app_02_add.png` | Ajout d'hôte |
| `linux_app_03_monitoring.png` | Monitoring actif |
| `linux_app_04_alerts.png` | Configuration alertes |

### Linux - Serveur Web

| Fichier | Description |
|---------|-------------|
| `linux_web_01_start.png` | Terminal avec démarrage |
| `linux_web_02_login.png` | Page de connexion |
| `linux_web_03_dashboard.png` | Dashboard admin |

---

## 🛠️ Comment créer les captures d'écran

### Windows

1. **Application** : Lancez `Ping_u.exe`
2. **Outil** : `Win + Shift + S` (Capture d'écran Windows)
3. **Format** : PNG, 1280x720 minimum
4. **Sauvegardez** dans ce dossier avec le bon nom

### Linux

```bash
# Avec gnome-screenshot
gnome-screenshot -w -f linux_app_01_main.png

# Avec scrot
scrot -s linux_app_01_main.png

# Avec flameshot
flameshot gui
```

### Interface Web

1. Ouvrez Chrome/Firefox
2. Accédez à http://localhost:9090/admin
3. `F12` → Device toolbar → Résolution 1280x720
4. Capturez avec l'outil intégré ou extension

---

## 📐 Spécifications des images

| Paramètre | Valeur |
|-----------|--------|
| Format | PNG |
| Résolution minimale | 1280 x 720 |
| Résolution recommandée | 1920 x 1080 |
| Compression | Optimisée pour le web |
| Taille max | 500 Ko par image |

### Optimisation

```bash
# Avec ImageMagick
convert input.png -resize 1280x720 -quality 85 output.png

# Avec pngquant
pngquant --quality=65-80 input.png -o output.png

# En lot
for f in *.png; do pngquant --quality=65-80 "$f" -o "optimized_$f"; done
```

---

## 🎨 Conseils de style

### À inclure

- ✅ Interface complète visible
- ✅ Données d'exemple réalistes (pas d'IP privées sensibles)
- ✅ Éléments importants mis en évidence
- ✅ Thème clair pour une meilleure lisibilité

### À éviter

- ❌ Informations personnelles visibles
- ❌ Captures floues ou trop petites
- ❌ Fenêtres partiellement cachées
- ❌ Données de production réelles

### Données d'exemple suggérées

```
IP              Nom             Statut
192.168.1.1     Routeur         ✅ OK
192.168.1.10    Serveur-Web     ✅ OK
192.168.1.20    NAS-Synology    ⚠️ Lent
192.168.1.50    Imprimante      ❌ HS
192.168.1.100   PC-Bureau       ✅ OK
```

---

## 📝 Checklist avant commit

- [ ] Toutes les captures requises sont présentes
- [ ] Les noms de fichiers respectent la convention
- [ ] Les images sont optimisées (< 500 Ko)
- [ ] Aucune donnée sensible visible
- [ ] Les images sont en PNG
- [ ] Résolution minimale respectée

---

## 🔄 Mise à jour des captures

Lors d'une mise à jour de l'interface :

1. Identifiez les captures affectées
2. Recréez les captures concernées
3. Optimisez les nouvelles images
4. Mettez à jour le changelog si nécessaire

---

**📸 Bon travail de documentation !**

