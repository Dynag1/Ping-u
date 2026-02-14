# 💡 Idées d'Amélioration pour Ping ü

Liste des fonctionnalités et améliorations techniques envisagées pour le futur.

## 1. 🐳 Conteneurisation (Docker)
Créer un `Dockerfile` et un `docker-compose.yml`.
- **Pourquoi ?** Facilite le déploiement sur tout type de serveur (NAS, VPS, Raspberry Pi) sans gestion manuelle des dépendances Python.
- **Avantages :** Portabilité, isolation, mise à jour simplifiée.

## 2. 🛡️ Service Linux (Systemd)
Créer un script d'installation pour gérer l'application via `systemd`.
- **Pourquoi ?** Permet le démarrage automatique au boot et le redémarrage automatique en cas de plantage.
- **Avantages :** Robustesse, intégration native au système Linux.

## 3. 🌐 Monitoring HTTP/HTTPS (Web Check)
Ajouter un type de monitoring pour vérifier les codes de réponse HTTP (200 OK, etc.).
- **Pourquoi ?** Le Ping (ICMP) ne suffit pas toujours : un serveur peut répondre au ping mais son service web peut être planté.
- **Avantages :** Surveillance applicative plus fine.

## 4. 🌗 Thème Clair / Sombre (UI)
Ajouter un basculement de thème dans l'interface d'administration Web.
- **Pourquoi ?** L'interface actuelle est "Dark only". Un mode clair améliore l'accessibilité dans les environnements lumineux.
- **Avantages :** Confort visuel, accessibilité.

## 5. 🗄️ Base de Données Utilisateurs (SQLite)
Migrer `web_users.json` vers une table dans une base de données SQLite.
- **Pourquoi ?** Le fichier JSON est basique et moins sécurisé/performant pour la gestion des utilisateurs.
- **Avantages :** Sécurité, évolutivité, gestion facilitée (CRUD).

## 6. 📊 Dashboards Personnalisables
Permettre à l'utilisateur de créer ses propres vues ou "dashboards" avec les équipements qui l'intéressent.
- **Pourquoi ?** Pour les grandes installations, voir tous les équipements n'est pas toujours pertinent.

## 7. 🔔 Notifications Granulaires
Configurer des notifications différentes selon l'équipement (ex: SMS pour le serveur critique, Email pour l'imprimante).
- **Pourquoi ?** Éviter le spam d'alertes pour des équipements peu critiques.
