# Ping ü 🌐

![Ping ü](https://prog.dynag.co/PyngOuin/logoP50.png "Ping ü")

[![Version](https://img.shields.io/badge/version-99.01.05-blue.svg)](https://github.com/Dynag1/ping-u)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE.txt)
[![Python](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/)
[![PySide6](https://img.shields.io/badge/PySide6-6.8-orange.svg)](https://www.qt.io/qt-for-python)

**Ping ü** est un outil professionnel de monitoring réseau permettant de surveiller vos équipements en temps réel avec des alertes multi-canaux et une interface web moderne.

## 📥 Téléchargement

[📦 Installateur Windows (.exe)](https://prog.dynag.co/Pingu/PingU_Setup.exe)

---

## ✨ Fonctionnalités principales

### 🎯 Monitoring réseau avancé
- ✅ **Ping asynchrone** : Jusqu'à 20 pings simultanés pour des performances optimales
- ✅ **Détection automatique** : Scan réseau complet avec détection des hôtes actifs
- ✅ **Latence en temps réel** : Affichage des temps de réponse avec code couleur
- ✅ **Récupération MAC** : Identification des équipements par adresse physique
- ✅ **Scan de ports** : Vérification des services disponibles

### 🎨 Interface utilisateur moderne
- ✅ **Interface graphique Qt** : Design moderne et responsive
- ✅ **Thèmes multiples** : Nord, Monokai, Catppuccin, Dracula, GitHub, Atom One, etc.
- ✅ **Tableau interactif** : Tri, filtrage et export des données
- ✅ **Code couleur intelligent** :
  - 🟢 Vert pâle : Latence < 50ms (excellent)
  - 🟠 Orange pâle : 50-100ms (bon)
  - 🔴 Rouge pâle : > 100ms (lent)
  - ⚫ Gris foncé : Hors service

### 🌐 Serveur Web intégré
- ✅ **Interface web temps réel** : Accédez à vos données depuis n'importe où
- ✅ **WebSocket** : Mises à jour instantanées sans rechargement
- ✅ **Design responsive** : Compatible mobile, tablette et desktop
- ✅ **Accès réseau** : Consultez vos statistiques à distance

### 🚨 Système d'alertes multi-canaux
- ✅ **Email** : Notifications par courrier électronique
- ✅ **Telegram** : Alertes instantanées sur votre téléphone
- ✅ **Popup** : Notifications locales sur le bureau
- ✅ **Mail récapitulatif** : Rapports programmés (quotidien, hebdomadaire)
- ✅ **Personnalisation** : Seuil de déclenchement configurable

### 📊 Monitoring SNMP avancé
- ✅ **Température** : Surveillance de la température des équipements
- ✅ **Débits réseau** : Monitoring des interfaces réseau (IN/OUT)
- ✅ **Onduleurs (UPS)** : Surveillance des onduleurs avec alertes batterie
- ✅ **Compatible** : Support des protocoles SNMP v1, v2c, v3

### 💾 Gestion des données
- ✅ **Import/Export** : Formats PIN (natif) et Excel (.xlsx)
- ✅ **Base de données** : Stockage SQLite des configurations
- ✅ **Sauvegarde automatique** : Préservation des paramètres et historique
- ✅ **Base externe** : Connexion à des bases de données distantes

### 🌍 Multilingue
- ✅ **Français** : Interface complète
- ✅ **Anglais** : Full interface support
- ✅ **Changement à la volée** : Sans redémarrage

### 🔌 Système de plugins
- ✅ **Architecture extensible** : Ajoutez vos propres fonctionnalités
- ✅ **Plugins inclus** : Snyf (découverte caméras), Temp (monitoring CPU)
- ✅ **API simple** : Développez facilement vos plugins

---

## 🚀 Installation

### Prérequis
- Windows 10/11 (64-bit)
- .NET Framework 4.7.2 ou supérieur (pour l'installateur)

### Installation via l'installateur
1. Téléchargez [PingU_Setup.exe](https://prog.dynag.co/Pingu/PingU_Setup.exe)
2. Exécutez l'installateur
3. Suivez les instructions à l'écran
4. Lancez Ping ü depuis le menu Démarrer

### Installation depuis les sources
```bash
# Cloner le repository
git clone https://github.com/Dynag1/ping-u.git
cd ping-u

# Installer les dépendances
pip install -r requirements.txt

# Lancer l'application
python Pingu.py
```

---

## 📖 Utilisation

### Démarrage rapide

#### 1. Ajouter des hôtes
- **Méthode 1** : Scan réseau
  - Entrez une IP de départ (ex: `192.168.1.1`)
  - Définissez le nombre d'hôtes à scanner
  - Sélectionnez "Tout" ou "Alive"
  - Cliquez sur "Rechercher"

- **Méthode 2** : Ajout manuel
  - Menu → Fichier → Importer
  - Chargez un fichier `.pin` ou `.xlsx`

#### 2. Démarrer le monitoring
- Cliquez sur le bouton **Start**
- Les pings commencent immédiatement
- Les latences s'affichent en temps réel

#### 3. Configurer les alertes
- Menu → Paramètres → Envoies
  - Configurez votre serveur SMTP
  - Ajoutez votre ID Telegram
- Cochez les alertes souhaitées (Mail, Telegram, Popup)
- Définissez le nombre de pings HS avant alerte

#### 4. Lancer le serveur web
- Menu → Fonction → Serveur Web → Démarrer
- Ouvrez votre navigateur : `http://localhost:9090`
- Accès réseau : `http://[votre-ip]:9090`

---

## ⚙️ Configuration

### Paramètres généraux
- **Délai entre pings** : 5-3600 secondes
- **Nombre de HS** : Seuil avant déclenchement d'alerte
- **Thème** : Personnalisation de l'interface
- **Titre** : Nom du site surveillé

### Paramètres Email
```
Serveur SMTP : smtp.gmail.com
Port : 587 (TLS) ou 465 (SSL)
Compte : votre@email.com
Mot de passe : Mot de passe d'application
```

### Paramètres Telegram
1. Créez un bot avec [@BotFather](https://t.me/botfather)
2. Récupérez votre Chat ID avec [@userinfobot](https://t.me/userinfobot)
3. Entrez l'ID dans Paramètres → Envoies

### Mail récapitulatif
- Définissez l'heure d'envoi
- Sélectionnez les jours de la semaine
- Recevez un rapport complet de l'état du réseau

---


## 🛠️ Technologies utilisées

### Backend
- **Python 3.13** : Langage principal
- **PySide6** : Framework Qt pour l'interface graphique
- **asyncio** : Gestion asynchrone des pings
- **Flask** : Serveur web
- **Flask-SocketIO** : Communication temps réel
- **pysnmp** : Protocole SNMP
- **openpyxl** : Import/Export Excel

### Frontend (Web)
- **Socket.IO** : WebSocket temps réel
- **HTML5/CSS3** : Interface web moderne
- **JavaScript** : Logique client

### Base de données
- **SQLite3** : Stockage local des configurations

### Packaging
- **PyInstaller** : Création d'exécutable standalone
- **Inno Setup** : Installateur Windows

---

## 📂 Structure du projet

```
Ping-u/
├── Pingu.py                 # Point d'entrée principal
├── requirements.txt         # Dépendances Python
├── src/
│   ├── controllers/         # Contrôleurs MVC
│   ├── core/               # Logique métier (alertes, etc.)
│   ├── utils/              # Utilitaires (logger, colors, SNMP)
│   ├── web/                # Serveur web et templates
│   ├── languages/          # Fichiers de traduction
│   ├── fcy_ping.py         # Moteur de ping asynchrone
│   ├── web_server.py       # Serveur Flask + SocketIO
│   └── var.py              # Variables globales
├── fichier/plugin/         # Plugins
├── bd/                     # Base de données
├── logs/                   # Fichiers de logs
└── dist/                   # Build de distribution
```

---

## 🐛 Résolution de problèmes

### Le serveur web ne démarre pas
```bash
# Vérifier que le port 9090 est libre
netstat -ano | findstr :9090

# Si occupé, arrêter le processus ou changer le port dans le code
```

### Les pings montrent des latences élevées
- Vérifiez votre connexion réseau
- Réduisez le nombre de pings simultanés
- Augmentez le délai entre les cycles

### Les alertes ne fonctionnent pas
- Vérifiez les paramètres SMTP/Telegram
- Consultez les logs : `logs/app.log`
- Testez la connexion réseau sortante

### Logs de débogage
```
logs/app.log       # Logs principaux de l'application
logs/stderr.log    # Erreurs système
logs/stdout.log    # Sorties standard
```

---

## 🤝 Contribution

Les contributions sont les bienvenues ! Pour contribuer :

1. **Fork** le projet
2. Créez une **branche** pour votre fonctionnalité (`git checkout -b feature/AmazingFeature`)
3. **Committez** vos changements (`git commit -m 'Add some AmazingFeature'`)
4. **Push** vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une **Pull Request**

---

## 📝 Changelog

### Version 99.01.05 (Actuelle)
- ✨ Ajout du serveur web avec interface temps réel
- ✨ Support SNMP (température, débits, UPS)
- ✨ Traductions complètes FR/EN
- ✨ Optimisation des pings (20 parallèles, timeouts améliorés)
- ✨ Nouveau système de couleurs adaptatif
- 🐛 Correction du parsing des latences Windows FR
- 🐛 Correction de l'encodage CP850
- 🔧 Refactoring architecture MVC

---

## 📄 Licence

Ce projet est sous licence [MIT](LICENSE.txt).

```
Copyright (c) 2025 Ping ü

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

---

## 👨‍💻 Auteur

**Dynag**  
🌐 Website: [https://prog.dynag.co](https://prog.dynag.co)

---

## 🙏 Remerciements

- Qt/PySide6 pour le framework GUI
- La communauté Python pour les excellentes bibliothèques
- Tous les contributeurs du projet

---

## 📞 Support

- 🐛 **Bug Reports** : [Issues](https://github.com/yourusername/ping-u/issues)
- 💬 **Discussions** : [Discussions](https://github.com/yourusername/ping-u/discussions)
- 📧 **Email** : support@dynag.co
- 🌐 **Website** : [prog.dynag.co](https://prog.dynag.co)

---

<div align="center">

**⭐ Si vous aimez ce projet, n'hésitez pas à lui donner une étoile ! ⭐**

Made with ❤️ by Dynag

</div>
