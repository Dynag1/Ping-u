# 🌐 Notice d'utilisation - Interface Web Ping ü

Cette notice détaille l'utilisation de l'interface web de Ping ü pour le monitoring réseau.

---

## 📍 Accès à l'interface

| Type | URL |
|------|-----|
| **Locale** | http://localhost:9090 |
| **Réseau** | http://[VOTRE_IP]:9090 |

### Identifiants par défaut

| Champ | Valeur |
|-------|--------|
| Utilisateur | `admin` |
| Mot de passe | `a` |

> ⚠️ **Changez ces identifiants dès la première connexion !**

---

## 🖥️ Pages disponibles

| Page | URL | Description |
|------|-----|-------------|
| **Monitoring** | `/` | Vue temps réel des hôtes |
| **Administration** | `/admin` | Gestion complète du système |
| **Statistiques** | `/statistics` | Historique des connexions |
| **Graphiques** | `/monitoring` | Courbes température et débit |

---

## 📊 Page Monitoring (`/`)

La page principale affiche l'état en temps réel de tous les hôtes surveillés.

### Éléments affichés

- **Cartes hôtes** : Une carte par hôte avec son statut
- **Indicateurs de latence** : Couleur selon le temps de réponse
  - 🟢 Vert : < 20ms (excellent)
  - 🟡 Jaune : 20-50ms (bon)
  - 🟠 Orange : 50-100ms (moyen)
  - 🔴 Rouge : > 100ms (lent)
- **Température** : Affichée si SNMP configuré
- **Bande passante** : Affichée si OID configuré

### Menu latéral (☰)

- Statistiques globales (Total, En ligne, Hors ligne)
- Seuils température (warning/critique)
- Filtre par site
- Sélection de la langue

### Commentaires

Chaque carte hôte permet d'ajouter un commentaire utilisateur.

---

## ⚙️ Page Administration (`/admin`)

Interface complète de gestion du système.

### Menu latéral

| Section | Fonction |
|---------|----------|
| **🖥️ Hôtes** | Liste et gestion des hôtes |
| **➕ Ajouter** | Ajout manuel ou scan réseau |
| **📡 Monitoring** | Démarrer/arrêter la surveillance |
| **🔔 Alertes** | Configuration des notifications |
| **📍 Sites** | Gestion des sites/groupes |
| **⚙️ Avancé** | SNMP, seuils, intervalles |

### Gestion des hôtes

Pour chaque hôte, vous pouvez :
- ✏️ Modifier (nom, IP, MAC, site, OIDs)
- 🗑️ Supprimer
- 👁️ Voir les détails

### Scanner réseau

1. Aller dans **➕ Ajouter**
2. Entrer l'IP de départ et le nombre d'hôtes
3. Cocher les options de détection :
   - Hikvision, Dahua, Xiaomi (caméras)
   - SSH, SMB, HTTP (services)
4. Cliquer sur **🔍 Scanner**
5. Sélectionner les hôtes à ajouter

### Configuration des alertes

| Type | Description | Licence |
|------|-------------|---------|
| **Popup** | Notification navigateur | ❌ Non |
| **Email** | Alerte SMTP | ✅ Oui |
| **Telegram** | Bot Telegram | ✅ Oui |
| **Mail Récap** | Email programmé | ✅ Oui |

### Configuration SNMP

- **Communauté** : Nom de la communauté SNMP (ex: `public`)
- **Port** : Port SNMP (défaut: `161`)
- **OID Température** : OID pour lecture température
- **OID Bande passante IN/OUT** : OIDs pour le débit réseau

### Seuils de température

- **Warning** : Seuil d'alerte jaune (ex: 60°C)
- **Critique** : Seuil d'alerte rouge (ex: 80°C)

---

## 📈 Page Statistiques (`/statistics`)

Historique et analyse des connexions.

### Vue d'ensemble

- 🔻 Nombre total de déconnexions
- 🔺 Nombre total de reconnexions
- ⏱️ Durée moyenne d'indisponibilité
- 🖥️ Nombre d'hôtes affectés

### Filtres disponibles

- **Période** : 24h, 7 jours, 30 jours
- **Site** : Filtrer par site/groupe

### Tableaux

- **Top Déconnecteurs** : Hôtes avec le plus de déconnexions
- **Événements Récents** : Derniers événements enregistrés
- **Détail par Hôte** : Sélection d'un hôte pour voir son historique

---

## 📊 Page Graphiques (`/monitoring`)

Visualisation des données historiques.

### Graphiques disponibles

1. **🌡️ Température** : Courbe d'évolution avec min/max/moyenne
2. **📶 Débit Réseau** : Courbes IN/OUT en Mbps ou Kbps

### Périodes

- 1 heure
- 6 heures
- 24 heures
- 7 jours
- 15 jours

### Utilisation

1. Sélectionner un hôte dans la liste déroulante
2. Choisir la période souhaitée
3. Les graphiques se mettent à jour automatiquement

> **Note** : Seuls les hôtes avec SNMP configuré apparaissent avec des données.

---

## 🔐 Gestion des utilisateurs

### Modifier le mot de passe

1. Aller dans **Administration** > **⚙️ Avancé**
2. Section **Utilisateurs**
3. Changer le mot de passe

### Réinitialiser les identifiants

En cas de perte, supprimez le fichier :
```
web_users.json
```
Les identifiants par défaut seront restaurés.

---

## 🌍 Langues

L'interface supporte plusieurs langues :
- 🇫🇷 Français
- 🇬🇧 English
- 🇩🇪 Deutsch
- 🇪🇸 Español
- 🇵🇹 Português
- 🇮🇹 Italiano
- 🇳🇱 Nederlands
- 🇸🇪 Svenska

Changez la langue via le sélecteur dans le menu latéral.

---

## 🔧 Dépannage

| Problème | Solution |
|----------|----------|
| Page ne charge pas | Vérifier que le serveur est démarré |
| Connexion refusée | Vérifier le pare-feu (port 9090) |
| Pas de données SNMP | Vérifier la configuration SNMP et les OIDs |
| Notifications non reçues | Vérifier les autorisations navigateur |
| Graphiques vides | Attendre l'accumulation de données |

### Logs

Consultez les logs pour diagnostiquer les problèmes :
```
logs/app.log
```

---

## 📞 Support

- **Documentation** : [docs/](.)
- **Logs** : `logs/app.log`
- **Site web** : https://prog.dynag.co

---

**Version** : 99.02.08
