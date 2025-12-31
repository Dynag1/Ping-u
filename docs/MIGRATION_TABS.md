# Migration des fichiers tab vers bd/tabs/

## Vue d'ensemble

Les fichiers de configuration binaires `tab`, `tab4`, `tabG` et `tabr` ont été déplacés de la racine du projet vers le sous-dossier `bd/tabs/` pour une meilleure organisation.

## Changements effectués

### 1. Structure des dossiers

**Avant** :
```
/
├── tab
├── tab4
├── tabG
├── tabr
├── bd/
└── src/
```

**Après** :
```
/
├── bd/
│   └── tabs/
│       ├── tab
│       ├── tab4
│       ├── tabG
│       └── tabr
└── src/
```

### 2. Fichiers modifiés

#### Code source

1. **`src/db.py`**
   - `fichierini = "tabG"` → `fichierini = "bd/tabs/tabG"`
   - `fichierini = "tab4"` → `fichierini = "bd/tabs/tab4"`
   - `fichierini = "tab"` → `fichierini = "bd/tabs/tab"`
   - `fichierini = "tabr"` → `fichierini = "bd/tabs/tabr"`
   - `open("tab4")` → `open("bd/tabs/tab4")`
   - `open("tab")` → `open("bd/tabs/tab")`
   - `open("tabr")` → `open("bd/tabs/tabr")`

2. **`src/lic_secure.py`**
   - `fichier = "tabG"` → `fichier = "bd/tabs/tabG"`

3. **`init_raspberry.py`**
   - Ajout de la création du dossier `bd/tabs`
   - Mise à jour de tous les chemins vers `bd/tabs/tab`, `bd/tabs/tab4`, `bd/tabs/tabG`, `bd/tabs/tabr`

4. **`installer_ubuntu/opt/pingu/src/db.py`**
   - Mêmes modifications que `src/db.py`

5. **`installer_ubuntu/opt/pingu/src/lic_secure.py`**
   - Mêmes modifications que `src/lic_secure.py`

#### Configuration

6. **`.gitignore`**
   - `tab` → `bd/tabs/tab`
   - `tab4` → `bd/tabs/tab4`
   - `tabG` → `bd/tabs/tabG`
   - `tabr` → `bd/tabs/tabr`

## Description des fichiers

### `tab` - Paramètres mail
Format: Liste `[serveur, port, expediteur, mot_de_passe]`

Contient les paramètres de configuration email pour les alertes.

### `tab4` - Paramètres de monitoring  
Format: Liste `[delais, nbr_hs, popup, mail, telegram, mail_recap, db_externe, temp_alert, temp_seuil, temp_seuil_warning]`

Contient :
- `delais` : Délai entre les pings (secondes)
- `nbr_hs` : Nombre d'échecs avant alerte
- `popup` : Activation des popups
- `mail` : Activation des alertes mail
- `telegram` : Activation des alertes Telegram
- `mail_recap` : Activation du mail récapitulatif
- `db_externe` : Utilisation d'une base de données externe
- `temp_alert` : Alertes température activées
- `temp_seuil` : Seuil température critique (°C)
- `temp_seuil_warning` : Seuil température warning (°C)

### `tabG` - Paramètres généraux
Format: Liste `[nom_site, langue, theme, titre_avance]` + optionnel `[licence]`

Contient :
- `nom_site` : Nom du site de monitoring
- `langue` : Code langue ('fr', 'en')
- `theme` : Thème interface ('light', 'dark')
- `titre_avance` : Titre de la section paramètres avancés
- `licence` : Clé de licence (optionnel)

### `tabr` - Paramètres mail récapitulatif
Format: Liste de destinataires

Contient la liste des adresses email pour le mail récapitulatif.

## Migration automatique

Pour les utilisateurs existants, les fichiers tab à la racine seront automatiquement déplacés vers `bd/tabs/` lors du prochain lancement de l'application si le dossier est absent.

## Compatibilité

✅ **Compatibilité ascendante** : Le code est compatible avec les anciennes et nouvelles structures
✅ **Pas d'action manuelle requise** : Le déplacement est automatique
✅ **Données préservées** : Aucune perte de configuration

## Commandes manuelles (si nécessaire)

Si vous devez effectuer la migration manuellement :

```bash
# Créer le dossier bd/tabs
mkdir -p bd/tabs

# Déplacer les fichiers
mv tab tab4 tabG tabr bd/tabs/ 2>/dev/null || true
```

## Avantages

1. **Organisation** : Fichiers de configuration regroupés dans un dossier dédié
2. **Clarté** : Séparation claire entre code et configuration
3. **Maintenance** : Plus facile de gérer les backups des configurations
4. **Cohérence** : Structure similaire au dossier `bd/` pour les bases de données

## Date de migration

**2025-12-31** - Version 99.03.05

---

**Note** : Tous les fichiers tab sont au format Python pickle (binaire). Ne PAS les éditer manuellement - utilisez l'interface graphique ou web de l'application.
