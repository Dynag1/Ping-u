# 🌐 Ping ü — Monitoring réseau professionnel (Résumé fonctionnalités)

> **Surveillez vos équipements en temps réel** avec alertes multi-canaux, interface moderne et serveur web intégré.

---

## 🎯 Fonctionnalités clés (en 1 coup d’œil)

### 🖥️ Interface & UX
- **Interface Qt moderne** : responsive, thèmes (Nord, Dracula, Monokai…)
- **Tableau interactif** : tri, filtre, export (.pin, .xlsx)
- **Code couleur intelligent** :
  - 🟢 En ligne
  - ⚫ Hors service

### 🌐 Monitoring réseau
- **Ping asynchrone** : jusqu’à 20 hôtes en parallèle
- **Scan réseau automatique** : détection des hôtes actifs + MAC
- **Latence en temps réel** : affichage dynamique avec couleurs
- **Scan de ports** : vérifie les services ouverts

### 🚨 Alertes multi-canaux
- ✉️ **Email** (SMTP + rapports quotidiens/hebdomadaires)
- 📱 **Telegram** (notifications instantanées)
- 💬 **Popup local** (sur le bureau)
- ⚙️ **Seuils personnalisables** : nombre de pings HS avant alerte

### 🌍 Serveur Web intégré
- 🌐 **Accès distant** : `http://[IP]:9090`
- ⚡ **WebSocket** : mises à jour en temps réel (sans rechargement)
- 📱 **Responsive** : compatible mobile, tablette, desktop

### 📊 Monitoring SNMP avancé
- 🌡️ **Température** des équipements
- 📈 **Débits réseau** (IN/OUT)
- 🔋 **Onduleurs (UPS)** : alertes batterie
- 🔄 Compatible SNMP v1, v2c, v3

### 💾 Gestion & Extensibilité
- 📤 **Import/Export** : formats PIN et Excel
- 🗃️ **Base SQLite** : stockage local des configs + historique
- 🧩 **Plugins** : architecture extensible (ex. : Snyf, Temp)
- 🌐 **Multilingue** : FR / EN (changement à la volée)

---

## 🚀 Installation rapide

### ✅ Windows
1. Téléchargez : [PingU_Setup.exe](https://prog.dynag.co/Pingu/PingU_Setup.exe)
2. Exécutez → Suivez les étapes → Lancez depuis Démarrer

### 🐍 Depuis les sources (tous OS)
```bash
git clone https://github.com/Dynag1/ping-u.git
cd ping-u
pip install -r requirements.txt
python Pingu.py
```
> **Prérequis** :
> - Python `3.13` ou supérieur
> - PySide6 `6.8` ou supérieur

---
## Licences

- Pour débloquer toutes les fonctionnalités, vous aurez besoin d'une licence, vous pouvez la demander ici : [https://li.dynag.co](https://li.dynag.co)
---

## 🛠️ Technologies

- **Python 3.13** + **PySide6** (GUI)
- **asyncio** (ping asynchrone)
- **Flask + SocketIO** (serveur web)
- **pysnmp** (monitoring SNMP)
- **SQLite** (stockage local)

---

## 🐛 Support & Contribution

- 🐞 [Issues](https://github.com/Dynag1/ping-u/issues)
- 💬 [Discussions](https://github.com/Dynag1/ping-u/discussions)
- 📧 [support@dynag.co](mailto:support@dynag.co)
- 🤝 [Contribuer](https://github.com/Dynag1/ping-u) → Fork → Pull Request

---

## 📄 Licence

[Lire la licence](LICENSE.txt)

---

## ⭐ Donnez une étoile si vous aimez !

> Made with ❤️ by [Dynag](https://prog.dynag.co)
