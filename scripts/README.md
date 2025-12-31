# Scripts Utilitaires

Ce dossier contient les scripts utilitaires pour la maintenance, la configuration et le lancement de Ping ü.

## 📜 Scripts disponibles

### Démarrage et Arrêt

#### `start_headless.sh`
**Démarrage en mode headless (sans interface graphique)**

```bash
./scripts/start_headless.sh
```

Démarre l'application Ping ü en arrière-plan avec l'interface web accessible sur le port 9090.

Fonctionnalités :
- Détecte automatiquement l'environnement virtuel (.venv ou venv)
- Vérifie les modules Python nécessaires
- Installe automatiquement les modules manquants
- Détecte si le port 9090 est déjà utilisé
- Crée un fichier PID pour le suivi
- Logs dans `pingu_headless.log`

#### `stop_headless.sh`
**Arrêt de l'application headless**

```bash
./scripts/stop_headless.sh
```

Arrête proprement l'application en cours d'exécution :
- Via le fichier PID
- Via le port 9090
- Force l'arrêt si nécessaire

#### `run_dev.sh`
**Lancement en mode développement**

```bash
./scripts/run_dev.sh
```

Lance l'application avec l'interface graphique pour le développement.

---

### Migration et Configuration

#### `migrate_tabs.sh`
**Migration automatique des fichiers de configuration**

```bash
./scripts/migrate_tabs.sh
```

Déplace automatiquement les fichiers `tab`, `tab4`, `tabG` et `tabr` de la racine vers `bd/tabs/`.

📖 [Documentation complète](../docs/SCRIPT_MIGRATION_TABS.md)

---

### Raspberry Pi

#### `init_raspberry.py`
**Initialisation pour Raspberry Pi**

```bash
python3 scripts/init_raspberry.py
```

Crée les fichiers de configuration initiale pour une installation sur Raspberry Pi :
- Fichiers tab (paramètres mail, monitoring, etc.)
- Dossiers nécessaires
- `web_users.json` avec identifiants par défaut

#### `cleanup_raspberry.sh`
**Nettoyage de l'installation Raspberry Pi**

```bash
./scripts/cleanup_raspberry.sh
```

Nettoie les fichiers temporaires et logs sur Raspberry Pi.

#### `fix_raspberry.sh`
**Correction des problèmes Raspberry Pi**

```bash
./scripts/fix_raspberry.sh
```

Répare les problèmes courants sur Raspberry Pi :
- Permissions SNMP
- Permissions ping
- Dépendances manquantes

---

## 🚀 Utilisation rapide

### Démarrer/Arrêter l'application

```bash
# Démarrer en mode headless
./scripts/start_headless.sh

# Arrêter
./scripts/stop_headless.sh

# Lancer en mode développement
./scripts/run_dev.sh
```

### Pour une nouvelle installation Raspberry Pi

```bash
# 1. Initialiser la configuration
python3 scripts/init_raspberry.py

# 2. Corriger les permissions si nécessaire
sudo ./scripts/fix_raspberry.sh

# 3. Démarrer l'application
./scripts/start_headless.sh
```

### Pour migrer une installation existante

```bash
# Migrer les fichiers tab vers bd/tabs/
./scripts/migrate_tabs.sh
```

### Pour nettoyer

```bash
# Nettoyer les fichiers temporaires
./scripts/cleanup_raspberry.sh
```

---

## 📝 Notes

- Tous les scripts `.sh` doivent être exécutables : `chmod +x scripts/*.sh`
- Certains scripts nécessitent `sudo` pour les permissions système
- Les scripts Python utilisent Python 3

---

**Dernière mise à jour** : 2025-12-31
