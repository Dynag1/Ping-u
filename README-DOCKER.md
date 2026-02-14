# 🐳 Guide d'Installation Docker pour Ping ü

Ce guide explique comment installer et exécuter **Ping ü** sur un serveur Linux (ou Raspberry Pi) vierge, en utilisant Docker.

## 📋 Prérequis

*   **Git** installé (`sudo apt install git`)
*   **Docker** et **Docker Compose** installés.

## 🚀 Installation Rapide

### 1. Cloner le dépôt

Récupérez le code source de l'application :

```bash
git clone https://github.com/Dynag1/ping-u.git
cd ping-u
```

### 2. Lancer l'application

Démarrez le conteneur en arrière-plan avec Docker Compose :

```bash
docker-compose up -d
```

> **Note :** La première exécution peut prendre quelques minutes le temps de télécharger l'image Python et d'installer les dépendances.

### 3. Accéder à l'interface

Une fois le conteneur démarré, ouvrez votre navigateur web et accédez à :

*   **URL :** `http://<IP-DE-VOTRE-SERVEUR>:9090/admin`
*   **Identifiant par défaut :** `admin`
*   **Mot de passe par défaut :** `a`

## 🛠️ Commandes Utiles

*   **Voir les logs :**
    ```bash
    docker-compose logs -f
    ```

*   **Arrêter l'application :**
    ```bash
    docker-compose down
    ```

*   **Mettre à jour l'application :**
    ```bash
    git pull
    docker-compose down
    docker-compose up -d --build
    ```

## 📂 Structure des Données

Les données importantes sont stockées dans des dossiers locaux (créés automatiquement) pour ne pas être perdues en cas de redémarrage du conteneur :

*   `./bd` : Base de données et fichiers de configuration
*   `./config` : Fichiers de configuration utilisateur
*   `./logs` : Journaux de l'application
