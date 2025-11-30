# ⚠️ URGENT - Reconfiguration SMTP Requise

## 🔴 Problème Résolu

**Bug critique découvert** : L'ordre des paramètres SMTP était inversé entre l'interface web et l'interface Qt, causant l'erreur :
```
Erreur d'envoi en clair : invalid literal for int() with base 10: 'contact@dynag.co'
```

## ✅ Correction Appliquée

L'ordre des paramètres a été uniformisé dans tout le code pour correspondre à l'interface Qt :

```
[0] = Email expéditeur
[1] = Mot de passe
[2] = Port
[3] = Serveur SMTP
[4] = Destinataires
[5] = Telegram Chat ID
```

## 🚨 ACTION REQUISE

**Vous DEVEZ reconfigurer vos paramètres SMTP** via l'interface web pour que tout fonctionne.

### Sur votre Raspberry Pi :

1. **Synchroniser les fichiers** depuis GitHub :
   ```bash
   cd ~/Ping_u
   python Pingu.py -stop
   bash cleanup_raspberry.sh  # Nettoyage complet
   git pull origin master      # Récupérer les corrections
   ```

2. **Reconfigurer SMTP** via l'interface web :
   ```
   http://IP_RASPBERRY:9090/admin
   ```
   
   - Ouvrir **"Paramètres Avancés"**
   - Cliquer sur **"📧 Configuration Email (SMTP)"**
   - Entrer à nouveau TOUS les paramètres :
     - ✉️ **Serveur SMTP** : `smtp.protonmail.ch` (ou votre serveur)
     - 🔌 **Port** : `587` ou `465`
     - 📧 **Email expéditeur** : `hemge@pm.me`
     - 🔑 **Mot de passe** : Votre mot de passe
     - 📨 **Destinataires** : `hemge@pm.me, autre@email.com`
   - Cliquer sur **"💾 Sauvegarder"**
   - Cliquer sur **"✉️ Tester"** pour vérifier

3. **Redémarrer l'application** :
   ```bash
   python Pingu.py -start
   ```

4. **Vérifier les logs** :
   ```bash
   tail -f logs/app.log
   ```
   Vous devriez voir :
   ```
   Mail en clair envoyé avec succès (STARTTLS)
   ```
   Au lieu de :
   ```
   Erreur d'envoi en clair : invalid literal for int() with base 10: '...'
   ```

---

## 📋 Checklist de Vérification

- [ ] Application arrêtée (`python Pingu.py -stop`)
- [ ] Nettoyage effectué (`bash cleanup_raspberry.sh`)
- [ ] Fichiers mis à jour (`git pull origin master`)
- [ ] Configuration SMTP saisie via l'interface web
- [ ] Test SMTP réussi (bouton "✉️ Tester")
- [ ] Application redémarrée (`python Pingu.py -start`)
- [ ] Alerte email testée (éteindre un hôte)
- [ ] Email d'alerte reçu ✅

---

## 🔍 Si le Problème Persiste

### 1. Vérifier que les fichiers sont à jour

```bash
cd ~/Ping_u

# Vérifier thread_mail.py
grep "Ordre correct des paramètres" src/thread_mail.py
# Devrait afficher un commentaire avec l'ordre correct

# Vérifier web_server.py
grep "Ordre dans la DB" src/web_server.py
# Devrait afficher des commentaires avec l'ordre correct
```

### 2. Effacer la configuration actuelle et recommencer

```bash
# Sauvegarder l'ancienne config
cp tab tab.backup

# Supprimer la config (sera recréée)
rm tab

# Redémarrer et reconfigurer via l'interface web
python Pingu.py -stop
python Pingu.py -start
```

### 3. Vérifier manuellement l'ordre des paramètres

```bash
cd ~/Ping_u

python -c "
from src import db
params = db.lire_param_mail()
print('Paramètres SMTP actuels:')
print(f'[0] Email: {params[0]}')
print(f'[1] Password: {'*' * len(params[1])}')
print(f'[2] Port: {params[2]}')
print(f'[3] Server: {params[3]}')
print(f'[4] Recipients: {params[4]}')
"
```

Vérifiez que :
- `[0]` contient votre email (ex: `hemge@pm.me`)
- `[2]` contient un nombre (ex: `587` ou `465`)
- `[3]` contient le serveur (ex: `smtp.protonmail.ch`)

---

## 💡 Pourquoi Ce Bug Est Arrivé

L'interface Qt (fenêtre de paramètres) sauvegardait les paramètres dans un ordre :
```
[email, password, port, server, recipients]
```

L'interface web utilisait un ordre différent :
```
[server, port, email, password, recipients]
```

Quand `thread_mail.py` lisait les paramètres, il essayait de convertir l'email en port (`int(email)`), d'où l'erreur.

Maintenant tout est uniformisé sur l'ordre de l'interface Qt.

---

## 📞 Support

Si après avoir suivi ces étapes, les emails ne fonctionnent toujours pas :

1. **Collectez les logs** :
   ```bash
   tail -100 logs/app.log > debug_smtp_order.txt
   ```

2. **Vérifiez la configuration** :
   ```bash
   python -c "from src import db; print(db.lire_param_mail())" >> debug_smtp_order.txt
   ```

3. **Testez manuellement** :
   ```bash
   python -c "
   from src import thread_mail
   result = thread_mail.envoie_mail('Test après correction ordre', 'Test SMTP')
   print(f'Résultat: {result}')
   "
   ```

---

**Date** : 30 Novembre 2025  
**Version** : Correction ordre paramètres SMTP  
**Fichiers modifiés** : `src/thread_mail.py`, `src/web_server.py`  
**Commit** : 3059dc5

🔥 **Cette correction est CRITIQUE - Appliquez-la IMMÉDIATEMENT !** 🔥

