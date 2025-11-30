# 🔄 Guide de Synchronisation Raspberry Pi

## 🎯 Problèmes à Résoudre

1. ❌ Erreur SMTP : "please run connect() first"
2. ❌ Page email récapitulatif manquante
3. ❌ Hôtes DOWN non ajoutés avec "Tous les hôtes"

## 📦 Fichiers à Synchroniser

Les fichiers suivants ont été modifiés et doivent être synchronisés sur votre Raspberry Pi :

### Fichiers modifiés :
1. ✅ `src/thread_mail.py` - Correction SMTP et désactivation GPG sur Linux
2. ✅ `src/email_sender.py` - **NOUVEAU FICHIER** - Module d'envoi d'emails
3. ✅ `src/web/templates/admin.html` - Ajout section email récapitulatif + modification noms
4. ✅ `src/threadAjIp.py` - Correction ajout hôtes DOWN
5. ✅ `Pingu.py` - Désactivation GPG sur Linux
6. ✅ `src/web_server.py` - Nouveaux endpoints API

---

## 🚀 Méthode de Synchronisation

### Méthode 1 : Via SCP (Recommandé)

#### Sur votre PC Windows :

```bash
# 1. Créer une archive avec tous les fichiers
# (Faire ceci dans le dossier Ping ü)

tar -czf ping_update.tar.gz \
    src/thread_mail.py \
    src/email_sender.py \
    src/web/templates/admin.html \
    src/threadAjIp.py \
    src/web_server.py \
    Pingu.py

# 2. Copier l'archive sur le Raspberry Pi
scp ping_update.tar.gz pi@ADRESSE_IP_RASPBERRY:~/

# Exemple : scp ping_update.tar.gz pi@192.168.1.100:~/
```

#### Sur le Raspberry Pi :

```bash
# 1. Se connecter au Raspberry
ssh pi@ADRESSE_IP_RASPBERRY

# 2. Arrêter l'application
cd ~/Ping_u  # ou le chemin où est installé Ping ü
python Pingu.py -stop

# 3. Extraire les fichiers
tar -xzf ~/ping_update.tar.gz

# 4. Redémarrer l'application
python Pingu.py -start

# 5. Vérifier les logs
tail -f logs/app.log
```

---

### Méthode 2 : Via WinSCP (Interface Graphique)

1. **Téléchargez WinSCP** : https://winscp.net/
2. **Connectez-vous à votre Raspberry Pi** :
   - Protocole : SCP
   - Hôte : Adresse IP du Raspberry
   - Port : 22
   - Utilisateur : pi
   - Mot de passe : votre mot de passe

3. **Copiez les fichiers un par un** :
   - À gauche : Votre PC Windows
   - À droite : Votre Raspberry Pi
   - Naviguez vers le dossier Ping ü des deux côtés
   - Glissez-déposez chaque fichier

4. **Sur le Raspberry Pi** (via SSH) :
   ```bash
   cd ~/Ping_u
   python Pingu.py -stop
   python Pingu.py -start
   ```

---

### Méthode 3 : Copie Manuelle des Fichiers

#### 1. Sur votre PC, créez un fichier ZIP avec :
```
ping_update.zip
├── src/
│   ├── thread_mail.py
│   ├── email_sender.py
│   ├── threadAjIp.py
│   ├── web_server.py
│   └── web/
│       └── templates/
│           └── admin.html
└── Pingu.py
```

#### 2. Transférez le ZIP sur le Raspberry via :
- Clé USB
- Partage réseau
- Email
- etc.

#### 3. Sur le Raspberry :
```bash
# Extraire et copier
cd ~/
unzip ping_update.zip
cp -r src/* ~/Ping_u/src/
cp Pingu.py ~/Ping_u/

# Redémarrer
cd ~/Ping_u
python Pingu.py -stop
python Pingu.py -start
```

---

## ✅ Vérification de la Synchronisation

### Script de Vérification

Exécutez ce script sur le Raspberry Pi pour vérifier que tout est à jour :

```bash
cd ~/Ping_u  # ou votre chemin d'installation
python verif_raspberry.py
```

Le script `verif_raspberry.py` a été créé et vérifie automatiquement :
- ✅ Si thread_mail.py contient la correction SMTP
- ✅ Si email_sender.py existe
- ✅ Si admin.html contient la section mail récapitulatif
- ✅ Si la configuration SMTP est présente

---

## 🧪 Tests Après Synchronisation

### 1. Test GPG désactivé sur Linux
```bash
# Les logs devraient afficher :
grep "GPG" logs/app.log
# Résultat attendu : "GPG non disponible: GPG désactivé sur Linux"
```

### 2. Test Email d'Alerte
1. Accédez à l'interface admin : `http://IP_RASPBERRY:9090/admin`
2. Éteignez un hôte surveillé
3. Vérifiez les logs :
   ```bash
   tail -f logs/app.log
   ```
4. Vous devriez voir :
   ```
   Envoi en clair à : votre-email@exemple.com
   Mail en clair envoyé avec succès (STARTTLS)
   ```

### 3. Test Email Récapitulatif
1. Ouvrez l'interface admin : `http://IP_RASPBERRY:9090/admin`
2. Allez dans **"Paramètres Avancés"**
3. Cliquez sur **"📊 Email Récapitulatif Périodique"**
4. ✅ La section devrait apparaître avec :
   - Heure d'envoi
   - Jours de la semaine
   - Boutons "Sauvegarder" et "Envoyer un test"

### 4. Test Ajout Hôtes DOWN
1. Dans l'interface admin
2. Section **"➕ Ajout d'Hôtes"**
3. Configurez :
   - IP : `192.168.1.200` (une IP qui n'existe pas)
   - Nombre : `5`
   - Type : **"Tous les hôtes"**
4. Cliquez sur **"Scanner"**
5. ✅ Les 5 IPs devraient apparaître dans la liste (même si DOWN)

---

## 🐛 Dépannage

### Problème : L'erreur SMTP persiste

**Vérifications** :
```bash
# 1. Vérifier que thread_mail.py a été mis à jour
grep "port_int = int(port)" src/thread_mail.py
# Devrait retourner une ligne

# 2. Vérifier les permissions
ls -l src/thread_mail.py
# Devrait être lisible (rw-r--r--)

# 3. Forcer le redémarrage
python Pingu.py -stop
sleep 5
pkill -f Pingu.py  # Au cas où
python Pingu.py -start
```

### Problème : La section email récapitulatif n'apparaît pas

**Vérifications** :
```bash
# 1. Vérifier que admin.html a été mis à jour
grep "Email Récapitulatif Périodique" src/web/templates/admin.html
# Devrait retourner une ligne

# 2. Vider le cache du navigateur
# Sur le navigateur : Ctrl+Shift+R (ou Cmd+Shift+R sur Mac)

# 3. Vérifier que le serveur web est redémarré
python Pingu.py -stop
python Pingu.py -start
```

### Problème : Les hôtes DOWN ne s'ajoutent toujours pas

**Vérifications** :
```bash
# 1. Vérifier que threadAjIp.py a été mis à jour
grep "is_all = " src/threadAjIp.py
# Devrait retourner : is_all = (tout == self.tr("Tout") or tout_lower == "all")

# 2. Vérifier les logs pendant le scan
tail -f logs/app.log
# Puis lancer un scan avec "Tous les hôtes"
```

---

## 📊 Tableau de Compatibilité

| Fonctionnalité | Avant Sync | Après Sync |
|---|---|---|
| **GPG sur Linux** | ❌ Crash | ✅ Désactivé |
| **Email d'alerte** | ❌ Erreur connexion | ✅ Fonctionne |
| **Email récap (config)** | ❌ Manquant | ✅ Disponible |
| **Email récap (envoi)** | ❌ Non fonctionnel | ✅ Fonctionne |
| **Ajout hôtes DOWN** | ❌ Ignorés | ✅ Ajoutés |
| **Modification noms** | ❌ Impossible | ✅ Possible |

---

## 🔧 Commandes Utiles

### Redémarrage complet
```bash
cd ~/Ping_u
python Pingu.py -stop
sleep 2
python Pingu.py -start
```

### Voir les logs en temps réel
```bash
tail -f logs/app.log
```

### Vérifier si le serveur web tourne
```bash
# Vérifier le processus
ps aux | grep Pingu

# Vérifier le port
netstat -tuln | grep 9090
# ou
ss -tuln | grep 9090
```

### Sauvegarder la configuration actuelle
```bash
# Avant de synchroniser, faire une sauvegarde
cd ~/Ping_u
tar -czf backup_$(date +%Y%m%d).tar.gz bd/ logs/ *.db
```

---

## 📞 Support

Si après la synchronisation vous rencontrez toujours des problèmes :

1. **Collectez les informations** :
   ```bash
   # Logs
   tail -100 logs/app.log > debug.txt
   
   # Version des fichiers
   grep "def envoie_mail" src/thread_mail.py >> debug.txt
   grep "Email Récapitulatif" src/web/templates/admin.html >> debug.txt
   
   # Configuration
   python -c "from src import db; print(db.lire_param_mail())" >> debug.txt
   ```

2. **Vérifiez** :
   - Que tous les fichiers ont bien été copiés
   - Que l'application a bien été redémarrée
   - Que le cache du navigateur a été vidé

3. **Testez** :
   - Email simple via le bouton "Tester" dans l'interface
   - Ajout d'un seul hôte DOWN manuellement
   - Accès à l'interface admin

---

**Date du guide** : 30 Novembre 2025  
**Version Ping ü** : Avec corrections SMTP, GPG et Email Récap  

🎉 **Après la synchronisation, toutes les fonctionnalités devraient fonctionner parfaitement sur votre Raspberry Pi !** 🎉

