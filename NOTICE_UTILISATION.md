# Notice d'utilisation - Ping ü (Mode Headless)

Ping ü peut être utilisé de deux manières :
1. **Mode Graphique (Desktop)** : Interface classique avec fenêtre.
2. **Mode Headless (Serveur)** : Sans interface graphique, contrôlable via un navigateur web.

Ce document explique comment utiliser le **Mode Headless**, idéal pour les serveurs ou pour tourner en arrière-plan.

---

## 1. Installation

Une fois l'application installée (par défaut dans `C:\Program Files\Ping_u` sur Windows), vous trouverez des scripts pour faciliter le lancement.

## 2. Windows

### Démarrage
Pour lancer l'application en arrière-plan sans fenêtre :
1. Ouvrez le dossier d'installation.
2. Double-cliquez sur le fichier **`start_headless.bat`**.
3. Une fenêtre noire va s'ouvrir brièvement puis se fermer. L'application tourne maintenant en tâche de fond.

### Accès à l'interface
Ouvrez votre navigateur web et allez à l'adresse :
👉 **http://localhost:6666/admin**

*Si vous êtes sur un autre PC du réseau, remplacez `localhost` par l'adresse IP du PC où Ping ü est installé (ex: `http://192.168.1.15:6666/admin`).*

### Arrêt
Pour arrêter proprement l'application :
1. Double-cliquez sur le fichier **`stop_headless.bat`**.

---

## 3. Linux / Mac

### Démarrage
Depuis un terminal dans le dossier de l'application :
```bash
./start_headless.sh
```

### Arrêt
```bash
./stop_headless.sh
```

### Démarrage automatique (Service Systemd - Linux)
Pour lancer Ping ü automatiquement au démarrage du serveur :

1. Créez un fichier de service :
   ```bash
   sudo nano /etc/systemd/system/pingu.service
   ```

2. Collez le contenu suivant (adaptez le chemin) :
   ```ini
   [Unit]
   Description=Ping ü Monitoring
   After=network.target

   [Service]
   Type=simple
   WorkingDirectory=/opt/Ping_u
   ExecStart=/opt/Ping_u/Ping_u -start
   ExecStop=/opt/Ping_u/Ping_u -stop
   Restart=on-failure
   User=votre_utilisateur

   [Install]
   WantedBy=multi-user.target
   ```

3. Activez le service :
   ```bash
   sudo systemctl enable pingu
   sudo systemctl start pingu
   ```

---

## 4. Interface Web

### Connexion
* **Utilisateur par défaut** : `admin`
* **Mot de passe par défaut** : `a`

⚠️ **Important** : Changez ces identifiants dès la première connexion via le bouton "Changer identifiants" en haut à droite.

### Fonctionnalités
L'interface web permet de tout gérer comme sur l'application bureau :
* **Ajout d'hôtes** : Un par un ou scan de plage IP.
* **Monitoring** : Démarrer et arrêter la surveillance.
* **Alertes** : 
    * **Popup** (Web Notification) : Gratuit.
    * **Mail / Telegram / Récap** : Nécessite une licence active.
* **Licence** : Entrez votre clé ou récupérez votre code d'activation dans l'onglet "Licence".

### Licence
Certaines fonctionnalités avancées (envoi de mails, Telegram) nécessitent une licence.
1. Allez dans **Paramètres Avancés > Licence**.
2. Copiez le **Code d'activation**.
3. Envoyez ce code pour obtenir votre clé.
4. Si la licence n'est pas active, les options payantes seront grisées.

---

## 5. Dépannage

* **L'interface ne s'ouvre pas ?** Vérifiez que le port **6666** n'est pas bloqué par un pare-feu.
* **Mot de passe perdu ?** Supprimez le fichier `web_users.json` dans le dossier d'installation pour remettre les identifiants par défaut (`admin`/`a`).
* **Logs** : En cas de problème, consultez le fichier `logs/app.log`.

