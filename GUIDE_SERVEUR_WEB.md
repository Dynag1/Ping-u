# 🌐 Guide du Serveur Web - Ping ü

## 📋 Description

Le serveur web intégré permet d'afficher en temps réel tous les hôtes monitorés depuis n'importe quel navigateur. La page se met à jour automatiquement à chaque modification du treeview.

---

## ✨ Fonctionnalités

### Affichage en temps réel
- ✅ **IP** de chaque hôte
- ✅ **Nom** personnalisé
- ✅ **Statut** (En ligne / Hors ligne)
- ✅ **Latence** (temps de réponse)
- ✅ **Température** (via SNMP si disponible)
- ✅ **Adresse MAC**
- ✅ **Port** utilisé

### Statistiques globales
- 📊 **Total** d'hôtes monitorés
- 🟢 **Nombre d'hôtes en ligne**
- 🔴 **Nombre d'hôtes hors ligne**

### Actualisation automatique
La page se met à jour **instantanément** lors de :
- ➕ Ajout d'un nouvel hôte
- ✏️ Modification du nom d'un hôte
- 🔄 Changement de statut (online ↔ offline)
- 📊 Mise à jour de la latence
- 🌡️ Mise à jour de la température
- 🗑️ Suppression d'un hôte

---

## 🚀 Démarrage

### Étape 1 : Vérifier que Flask est installé

Les dépendances nécessaires sont déjà installées si vous avez exécuté l'installation précédente.

Si nécessaire, installez-les avec :
```bash
pip install flask flask-socketio flask-cors
```

### Étape 2 : Lancer l'application Ping ü

Lancez normalement votre application Ping ü.

### Étape 3 : Démarrer le serveur web

1. Dans la barre de menu, cliquez sur **Serveur Web**
2. Sélectionnez **Démarrer le serveur**
3. Une fenêtre s'affiche avec les URLs d'accès

```
Serveur web démarré avec succès !

Accès local: http://localhost:5000
Accès réseau: http://192.168.1.X:5000
```

### Étape 4 : Accéder à la page web

#### 🏠 Sur le même ordinateur
- **Option 1** : Menu → **Serveur Web** → **Ouvrir dans le navigateur**
- **Option 2** : Ouvrez manuellement `http://localhost:5000`

#### 🌍 Depuis un autre PC/téléphone/tablette
1. Assurez-vous que les deux appareils sont sur le **même réseau** (WiFi/Ethernet)
2. Notez l'**IP réseau** affichée lors du démarrage (ex: `192.168.1.100`)
3. Sur l'autre appareil, ouvrez un navigateur et allez à :
   ```
   http://192.168.1.X:5000
   ```
   (remplacez X par votre IP)

---

## 🎯 Utilisation

### Interface web

La page affiche :

```
┌─────────────────────────────────────────┐
│ 🌐 Monitoring IP - Ping ü   [🟢 Connecté] │
│                                         │
│ Total: 15  En ligne: 12  Hors ligne: 3 │
└─────────────────────────────────────────┘

┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ Serveur Web  │  │ Routeur      │  │ NAS          │
│ En ligne     │  │ En ligne     │  │ Hors ligne   │
│ 192.168.1.10 │  │ 192.168.1.1  │  │ 192.168.1.50 │
│ MAC: AA:BB.. │  │ MAC: 11:22.. │  │ MAC: FF:EE.. │
│ Port: 80     │  │ Port: -      │  │ Port: 5000   │
│ Latence: 2ms │  │ Latence: 1ms │  │ Latence: -   │
│ Temp: 45°C   │  │ Temp: -      │  │ Temp: 42°C   │
└──────────────┘  └──────────────┘  └──────────────┘
```

### Actions disponibles

| Menu | Action |
|------|--------|
| **Serveur Web** → Démarrer le serveur | Lance le serveur sur le port 5000 |
| **Serveur Web** → Arrêter le serveur | Arrête le serveur |
| **Serveur Web** → Ouvrir dans le navigateur | Ouvre la page dans votre navigateur par défaut |
| **Serveur Web** → Voir les URLs d'accès | Affiche les URLs local et réseau |

---

## ⚙️ Configuration du pare-feu Windows

Si vous ne pouvez pas accéder au serveur depuis un autre PC, le pare-feu Windows bloque probablement les connexions.

### Solution 1 : PowerShell (recommandé)

Ouvrez PowerShell **en administrateur** et exécutez :

```powershell
New-NetFirewallRule -DisplayName "Ping ü - Serveur Web" -Direction Inbound -Protocol TCP -LocalPort 5000 -Action Allow
```

### Solution 2 : Interface graphique

1. Ouvrez **Panneau de configuration** → **Pare-feu Windows Defender**
2. Cliquez sur **Paramètres avancés**
3. Sélectionnez **Règles de trafic entrant**
4. Cliquez sur **Nouvelle règle...**
5. Choisissez **Port** → **Suivant**
6. Sélectionnez **TCP** et port spécifique : **5000** → **Suivant**
7. Sélectionnez **Autoriser la connexion** → **Suivant**
8. Laissez tous les profils cochés → **Suivant**
9. Nom : `Ping ü - Serveur Web` → **Terminer**

---

## 🔧 Résolution des problèmes

### ❌ Le serveur ne démarre pas

**Erreur** : "Le port 5000 est déjà utilisé"

**Solution** :
- Un autre programme utilise le port 5000
- Fermez les autres applications (navigateurs, serveurs web)
- Redémarrez l'application Ping ü

---

### ❌ Impossible d'accéder depuis un autre PC

**Causes possibles** :

1. **Les appareils ne sont pas sur le même réseau**
   - Vérifiez que les deux appareils sont connectés au même WiFi/réseau

2. **Pare-feu Windows bloque les connexions**
   - Suivez la section "Configuration du pare-feu" ci-dessus

3. **Mauvaise adresse IP**
   - Vérifiez l'IP dans : **Serveur Web** → **Voir les URLs d'accès**
   - L'IP peut changer si vous vous reconnectez au réseau

4. **Le serveur n'est pas démarré**
   - Assurez-vous que le serveur est bien démarré dans Ping ü

---

### ❌ La page ne se met pas à jour

**Solutions** :

1. **Actualisez la page** (F5)
2. **Vérifiez la console du navigateur** (F12) pour voir les erreurs
3. **Redémarrez le serveur web** :
   - Menu → **Serveur Web** → **Arrêter le serveur**
   - Menu → **Serveur Web** → **Démarrer le serveur**

---

### ❌ Le badge affiche "Déconnecté"

**Cause** : La connexion WebSocket est perdue

**Solutions** :
1. Actualisez la page (F5) - la reconnexion est automatique
2. Vérifiez que le serveur est toujours en cours d'exécution
3. Vérifiez votre connexion réseau

---

## 📱 Compatibilité

### Navigateurs supportés
- ✅ Chrome / Edge (recommandé)
- ✅ Firefox
- ✅ Safari
- ✅ Opera

### Appareils
- ✅ PC Windows, Mac, Linux
- ✅ Smartphones (iOS, Android)
- ✅ Tablettes
- ✅ Tout appareil avec un navigateur moderne

---

## 🔒 Sécurité

### Points importants

⚠️ **Le serveur est accessible à tous sur votre réseau local**
- Pas d'authentification par mot de passe
- Utilisez uniquement sur un réseau de confiance
- Ne pas exposer sur Internet

### Recommandations
- ✅ Utiliser uniquement sur réseau local/privé
- ✅ Désactiver le serveur quand il n'est pas utilisé
- ✅ Vérifier les appareils connectés à votre réseau

---

## 💡 Astuces

### Raccourci navigateur
Ajoutez l'URL en favori/marque-page pour un accès rapide

### Affichage permanent
Utilisez un vieux PC, tablette ou Raspberry Pi dédié pour afficher la page en permanence

### Mode plein écran
Appuyez sur **F11** dans le navigateur pour un affichage plein écran

### Actualisation automatique
La page s'actualise automatiquement - pas besoin de recharger manuellement !

---

## 📊 Informations techniques

| Paramètre | Valeur |
|-----------|--------|
| **Port** | 5000 |
| **Protocole** | HTTP + WebSocket |
| **Framework** | Flask + Socket.IO |
| **Actualisation** | Temps réel via WebSocket |
| **Interface** | 0.0.0.0 (toutes les interfaces) |

---

## 🆘 Support

En cas de problème :

1. **Consultez les logs** : Menu → **Logs** → **Voir les logs**
2. **Vérifiez la console** : Dans le navigateur, appuyez sur F12
3. **Redémarrez** : Fermez et relancez l'application Ping ü

---

## ✅ Checklist de démarrage rapide

- [ ] Flask est installé (`pip install flask flask-socketio flask-cors`)
- [ ] Ping ü est lancé
- [ ] Le serveur web est démarré (Menu → Serveur Web → Démarrer)
- [ ] J'ai noté les URLs d'accès
- [ ] J'ai testé l'accès local (`http://localhost:5000`)
- [ ] J'ai configuré le pare-feu (si accès réseau nécessaire)
- [ ] J'ai testé l'accès depuis un autre appareil

---

**Profitez de votre monitoring en temps réel ! 🎉**

