# Release Note
## Historique des Versions

---

### v99.03.03 (2025-12-18)
- Amélioration de la gestion de l'arrêt en mode headless sur Linux/Raspberry Pi.
*   `stop_headless.sh` : Ajout de la détection et de l'arrêt des processus via le port 9090 (lsof/fuser).
*   `start_headless.sh` : Ajout d'une vérification de disponibilité du port avant le lancement.
*   `WebServer` : Implémentation d'un arrêt plus propre du serveur SocketIO.

### v99.03.02 (2025-12-18)
- Ajout de la colonne "Commentaire" (index 9) synchronisée entre GUI, Web et Excel.
- Implémentation du titre "Paramètres Avancés" éditable directement depuis l'interface web admin.
- Correction et complétion des traductions Française et Anglaise.
- Nettoyage et standardisation des fichiers de traduction XML (.ts).
- Amélioration de la persistance des paramètres généraux (titre dynamique, thème, licence).
- Correction d'un bug d'indexation lors de l'exclusion d'hôtes dans la GUI.

### v99.03.01 (2025-12)
- Ajout de la gestion multi site. Possibilité d'assigner chaque IP à un site, de trier par site et de ne lancer le suivi que sur certains sites.
- Ajout de l'obligation de se connecter pour accéder au dashboard, soit en admin soit avec un compte user
- Amélioration du design HTML pour plus de clarté

### v99.02.06 (2025-12)
- Ajout: Support avancé des températures SNMP pour équipements réseau/nas/serveurs (Synology, QNAP, Dell, HP, Cisco, etc).
- Amélioration: Optimisation du cache SNMP et détection automatique du type d'équipement via sysDescr.
- Correction: Correction de divers bugs lors de l'arrêt et du redémarrage du monitoring.
- Front: Divers raffinements mineurs de l’interface et gestion des paramètres utilisateur étendue.
- Sauvegarde automatique de la liste de suivi à la fermeture.

### v99.02.05
- Ajout: Intégration du contrôle d’alerte température dans les paramètres généraux et possibilité d’activer/désactiver par équipement.
- Amélioration: Réinitialisation plus robuste des threads de monitoring.
- Correction: Résolution des problèmes d’encodage pour les adresses IP et les chaînes de caractères spéciales.

### v99.02.04
- Ajout: Détection étendue de constructeurs pour SNMP (Raspberry Pi, Netgear, Ubiquiti, etc).
- Correction: Gestion améliorée des exceptions lors des requêtes SNMP.
- Amélioration: Messages de log et diagnostics plus clairs.

---


