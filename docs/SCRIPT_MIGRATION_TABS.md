# Script de Migration des Fichiers Tab

## 📋 Description

Le script `migrate_tabs.sh` (situé dans `scripts/`) permet de migrer automatiquement les fichiers de configuration `tab`, `tab4`, `tabG` et `tabr` de la racine du projet vers le dossier `bd/tabs/`.

## 🚀 Utilisation

### Méthode simple

```bash
# Depuis la racine du projet
./scripts/migrate_tabs.sh
```

### Avec permissions

Si vous obtenez une erreur de permission :

```bash
# Rendre le script exécutable
chmod +x scripts/migrate_tabs.sh

# Puis l'exécuter
./scripts/migrate_tabs.sh
```

## 📦 Ce que fait le script

1. ✅ **Vérifie** si le dossier `bd/tabs/` existe
2. ✅ **Crée** le dossier `bd/tabs/` si nécessaire
3. ✅ **Sauvegarde** les fichiers existants dans `bd/tabs/` (*.backup)
4. ✅ **Déplace** les fichiers de la racine vers `bd/tabs/`
5. ✅ **Affiche** un rapport détaillé de la migration

## 📊 Exemple de sortie

```
==============================================================
  Migration des fichiers tab vers bd/tabs/
  Ping ü - Configuration Migration Script
==============================================================

📁 Vérification de la structure des dossiers...
   ✅ Le dossier bd/tabs existe déjà

🔄 Migration des fichiers de configuration...

📄 Traitement de 'tab'...
   ✅ tab → bd/tabs/tab

📄 Traitement de 'tab4'...
   ✅ tab4 → bd/tabs/tab4

📄 Traitement de 'tabG'...
   ✅ tabG → bd/tabs/tabG

📄 Traitement de 'tabr'...
   ✅ tabr → bd/tabs/tabr

==============================================================
📊 Résumé de la migration
==============================================================
  ✅ Fichiers migrés      : 4
  ⏭️  Déjà migrés          : 0
  ⏭️  Non trouvés          : 0
==============================================================
```

## 🔒 Sécurité

- Le script **NE supprime PAS** les fichiers existants dans `bd/tabs/`
- Il crée des **sauvegardes** automatiques (*.backup)
- Rapport détaillé de chaque opération

## 🆘 En cas de problème

Si la migration pose problème, restaurez vos fichiers :

```bash
# Restaurer depuis les sauvegardes
cd bd/tabs/
mv tab.backup tab
mv tab4.backup tab4
mv tabG.backup tabG
mv tabr.backup tabr
```

## 📝 Fichiers concernés

| Fichier | Description |
|---------|-------------|
| `tab` | Paramètres mail (SMTP) |
| `tab4` | Paramètres de monitoring |
| `tabG` | Paramètres généraux |
| `tabr` | Paramètres mail récapitulatif |

## ✨ Après la migration

1. Lancez l'application pour vérifier que tout fonctionne
2. Vérifiez que vos paramètres sont bien présents
3. Si tout est OK, vous pouvez supprimer les fichiers *.backup

## 🔗 Liens utiles

- [Documentation complète de la migration](docs/MIGRATION_TABS.md)
- [Changelog](Changelog.md)

---

**Date de création** : 2025-12-31  
**Version** : 99.03.05+
