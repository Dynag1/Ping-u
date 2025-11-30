# 🔧 Dépannage Raspberry Pi - Problèmes Résolus

## 🎯 Problèmes Corrigés

### 1. ❌ L'envoi d'un mail fait planter l'application

**Cause** : Erreur non gérée dans `thread_mail.py` qui faisait crasher tout le processus.

**✅ Solution appliquée** :
- Ajout de `try/except` global sur toute la fonction `envoie_mail()`
- Gestion des erreurs lors du chargement des paramètres
- Affichage du traceback complet pour debug
- La fonction retourne `True/False` au lieu de crasher

**Fichier modifié** : `src/thread_mail.py`

---

### 2. ❌ L'arrêt ne fonctionne pas, port 9090 toujours utilisé

**Cause** : Le serveur web ne se fermait pas proprement et le processus restait actif.

**✅ Solution appliquée** :
- Amélioration du `cleanup_and_exit()` avec attentes (sleep)
- Utilisation de `os._exit(0)` pour forcer la fermeture
- Augmentation du timeout d'arrêt à 15 secondes
- Ajout de SIGKILL après SIGTERM si nécessaire
- Création d'un script de nettoyage `cleanup_raspberry.sh`

**Fichiers modifiés** : `Pingu.py`, `cleanup_raspberry.sh` (nouveau)

---

## 🚀 Procédure de Mise à Jour sur Raspberry Pi

### 1. Arrêter l'application en force

```bash
# Sur le Raspberry Pi
cd ~/Ping_u

# Utiliser le nouveau script de nettoyage
bash cleanup_raspberry.sh
```

### 2. Synchroniser les fichiers corrigés

**Option A - Via SCP (depuis votre PC Windows)** :

```powershell
# Sur votre PC
cd "C:\Users\Hemge\clood\021 - Programmation\Python\Ping ü"

# Créer l'archive avec les corrections
tar -czf ping_fix_crash.tar.gz src/thread_mail.py Pingu.py cleanup_raspberry.sh

# Copier sur le Raspberry
scp ping_fix_crash.tar.gz pi@IP_RASPBERRY:~/
```

**Option B - Via Git (si vous avez déjà fait le push)** :

```bash
# Sur le Raspberry Pi
cd ~/Ping_u
git pull origin master
```

### 3. Extraire et appliquer les corrections

```bash
# Sur le Raspberry Pi
cd ~/Ping_u

# Extraire l'archive
tar -xzf ~/ping_fix_crash.tar.gz

# Rendre le script exécutable
chmod +x cleanup_raspberry.sh

# Redémarrer
python Pingu.py -start
```

---

## 🧪 Tests Après Correction

### Test 1 : Envoi d'Email (ne devrait plus crasher)

```bash
# Sur le Raspberry Pi
cd ~/Ping_u

# 1. Démarrer l'application
python Pingu.py -start

# 2. Dans un autre terminal, suivre les logs
tail -f logs/app.log

# 3. Via l'interface web, provoquer une alerte
# http://IP_RASPBERRY:9090/admin
# -> Éteindre un hôte surveillé

# 4. Vérifier les logs
# Vous devriez voir:
# - "Mail en clair envoyé avec succès (STARTTLS)"
# - OU "Erreur d'envoi en clair : [détails]"
# - MAIS PAS de crash complet
```

### Test 2 : Arrêt Propre (port devrait être libéré)

```bash
# 1. Arrêter l'application
python Pingu.py -stop

# 2. Vérifier que le processus est bien terminé
ps aux | grep Pingu.py
# Ne devrait rien afficher (sauf la commande grep)

# 3. Vérifier que le port est libéré
lsof -i:9090
# Ne devrait rien afficher

# 4. Redémarrer immédiatement (devrait fonctionner)
python Pingu.py -start
# Devrait démarrer sans erreur "port déjà utilisé"
```

---

## 🆘 Si Ça Ne Marche Toujours Pas

### Problème : L'application crashe encore lors de l'envoi d'email

**Diagnostic** :
```bash
# Vérifier les logs pour voir l'erreur exacte
tail -100 logs/app.log | grep -A 10 "Erreur"
```

**Solutions** :

1. **Vérifier la configuration SMTP** :
   ```bash
   # Sur le Raspberry, vérifier la config
   python -c "from src import db; print(db.lire_param_mail())"
   ```
   - Assurez-vous que tous les paramètres sont remplis
   - Port doit être `587` ou `465`
   - Email et mot de passe corrects

2. **Désactiver temporairement les emails** :
   ```bash
   # Via l'interface web
   # http://IP_RASPBERRY:9090/admin
   # Décocher toutes les alertes email
   ```

3. **Tester l'envoi manuellement** :
   ```bash
   python -c "
   from src import thread_mail
   result = thread_mail.envoie_mail('Test depuis Raspberry', 'Test')
   print(f'Résultat: {result}')
   "
   ```

---

### Problème : Le port 9090 reste bloqué

**Diagnostic** :
```bash
# Trouver ce qui utilise le port 9090
lsof -i:9090
# ou
netstat -tulpn | grep 9090
```

**Solution 1 - Script de nettoyage** :
```bash
cd ~/Ping_u
bash cleanup_raspberry.sh
```

**Solution 2 - Manuel** :
```bash
# Trouver le PID du processus
PID=$(lsof -ti:9090)

# Tuer le processus
kill -9 $PID

# Vérifier
lsof -i:9090  # Ne devrait rien afficher
```

**Solution 3 - Redémarrage du Raspberry** (dernier recours) :
```bash
sudo reboot
```

---

## 📋 Checklist de Diagnostic

Avant de redémarrer, vérifiez :

- [ ] Le fichier `src/thread_mail.py` contient `return False` dans les `except`
- [ ] Le fichier `Pingu.py` contient `os._exit(0)` dans `cleanup_and_exit()`
- [ ] Le script `cleanup_raspberry.sh` existe et est exécutable (`chmod +x`)
- [ ] Aucun processus `Pingu.py` en cours : `ps aux | grep Pingu.py`
- [ ] Le port 9090 est libre : `lsof -i:9090`
- [ ] Les logs ne montrent pas d'erreur bloquante : `tail logs/app.log`

---

## 🔍 Logs à Surveiller

### Logs OK (après correction) :
```
[HEADLESS] Démarrage en mode headless
Serveur web démarré sur http://0.0.0.0:9090
Monitoring prêt pour X hôte(s)
Envoi en clair à : votre-email@exemple.com
Mail en clair envoyé avec succès (STARTTLS)
[HEADLESS] Arrêt en cours...
Arrêt du monitoring...
Arrêt du serveur web...
Paramètres sauvegardés
Fichier PID supprimé
[HEADLESS] Arrêt terminé proprement
```

### Logs NOK (problèmes persistants) :
```
Erreur d'envoi en clair : ...
[puis plus rien = crash]
```

---

## 💡 Bonnes Pratiques

1. **Toujours utiliser le script de nettoyage avant de relancer** :
   ```bash
   bash cleanup_raspberry.sh
   python Pingu.py -start
   ```

2. **Attendre 5 secondes entre stop et start** :
   ```bash
   python Pingu.py -stop
   sleep 5
   python Pingu.py -start
   ```

3. **Surveiller les logs en temps réel** :
   ```bash
   # Dans un terminal séparé
   tail -f logs/app.log
   ```

4. **Faire des sauvegardes régulières** :
   ```bash
   tar -czf backup_$(date +%Y%m%d_%H%M).tar.gz bd/ logs/ *.db
   ```

---

## 🎯 Commandes Rapides

### Démarrer proprement
```bash
cd ~/Ping_u
bash cleanup_raspberry.sh
python Pingu.py -start
```

### Arrêter proprement
```bash
cd ~/Ping_u
python Pingu.py -stop
# Attendre 5 secondes
```

### Redémarrer
```bash
cd ~/Ping_u
python Pingu.py -stop && sleep 5 && python Pingu.py -start
```

### Statut
```bash
# Voir si l'application tourne
ps aux | grep Pingu.py

# Voir si le port est utilisé
lsof -i:9090

# Voir les logs récents
tail -50 logs/app.log
```

---

## 📞 Support

Si les problèmes persistent après avoir appliqué toutes ces corrections :

1. **Collectez les informations** :
   ```bash
   cd ~/Ping_u
   
   # Logs complets
   tail -200 logs/app.log > debug_raspberry.txt
   
   # Configuration
   python -c "from src import db; print('SMTP:', db.lire_param_mail())" >> debug_raspberry.txt
   
   # Processus
   ps aux | grep Pingu >> debug_raspberry.txt
   
   # Port
   lsof -i:9090 >> debug_raspberry.txt
   ```

2. **Testez en mode debug** :
   ```bash
   # Arrêter le mode headless
   python Pingu.py -stop
   bash cleanup_raspberry.sh
   
   # Lancer en mode normal pour voir les erreurs
   python Pingu.py
   # (Ctrl+C pour arrêter)
   ```

---

**Date** : 30 Novembre 2025  
**Version** : Corrections crash email + arrêt propre  
**Fichiers modifiés** : `src/thread_mail.py`, `Pingu.py`, `cleanup_raspberry.sh` (nouveau)

🎉 **Ces corrections devraient résoudre définitivement les problèmes de crash et de port bloqué !** 🎉

