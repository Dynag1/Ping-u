# 📧 Guide de configuration SMTP

Guide rapide pour configurer les alertes email dans Ping ü.

---

## 🔧 Configuration générale

### Via l'interface web

1. Accédez à `http://[IP]:9090/admin`
2. Connectez-vous (`admin` / `admin` par défaut)
3. Onglet **"Email"**
4. Remplissez les champs
5. Cliquez sur **"✉️ Tester"** pour vérifier

---

## 📨 Configurations courantes

### Gmail

```
Serveur SMTP : smtp.gmail.com
Port : 587 (ou 465)
Email : votre.email@gmail.com
Mot de passe : Mot de passe d'application (pas votre mot de passe Gmail)
Destinataires : email1@exemple.com, email2@exemple.com
```

**Important** : Utilisez un **mot de passe d'application** :
1. Compte Google → Sécurité
2. Validation en 2 étapes (doit être activée)
3. Mots de passe d'application → Générer
4. Utilisez ce mot de passe dans Ping ü

### Outlook / Hotmail / Office 365

```
Serveur SMTP : smtp-mail.outlook.com (ou smtp.office365.com)
Port : 587
Email : votre.email@outlook.com
Mot de passe : Votre mot de passe Outlook
Destinataires : email1@exemple.com, email2@exemple.com
```

### Yahoo Mail

```
Serveur SMTP : smtp.mail.yahoo.com
Port : 587 (ou 465)
Email : votre.email@yahoo.com
Mot de passe : Mot de passe d'application
Destinataires : email1@exemple.com, email2@exemple.com
```

**Important** : Générez un mot de passe d'application :
- Paramètres Yahoo → Sécurité → Générer un mot de passe d'application

### OVH

```
Serveur SMTP : ssl0.ovh.net
Port : 587 (ou 465)
Email : contact@votredomaine.com
Mot de passe : Mot de passe de votre compte email
Destinataires : email1@exemple.com, email2@exemple.com
```

### Free

```
Serveur SMTP : smtp.free.fr
Port : 587
Email : votre.identifiant@free.fr
Mot de passe : Mot de passe de votre compte Free
Destinataires : email1@exemple.com, email2@exemple.com
```

### Autre fournisseur

Consultez la documentation de votre fournisseur d'email pour obtenir :
- L'adresse du serveur SMTP
- Le port (généralement 587 ou 465)
- Si un mot de passe d'application est nécessaire

---

## 🔐 Ports SMTP

### Port 587 (STARTTLS) - Recommandé

- Connexion normale puis upgrade vers TLS
- Supporté par la plupart des serveurs
- Utilisez ce port en priorité

### Port 465 (SSL/TLS)

- Connexion SSL/TLS directe
- Utilisé par certains serveurs (Gmail, etc.)
- Essayez ce port si 587 ne fonctionne pas

### Port 25

- Port par défaut SMTP (non sécurisé)
- Souvent bloqué par les FAI
- Non recommandé

---

## ❌ Erreurs courantes

### "Connection unexpectedly closed"

**Cause** : Mauvais port ou configuration SSL/TLS

**Solutions** :
1. Si vous utilisez le port 587 → Essayez le port 465
2. Si vous utilisez le port 465 → Essayez le port 587
3. Vérifiez que le serveur SMTP est correct

### "Erreur d'authentification SMTP"

**Cause** : Email ou mot de passe incorrect

**Solutions** :
1. Vérifiez l'email (doit être complet : `user@domain.com`)
2. Pour Gmail/Yahoo : Utilisez un **mot de passe d'application**
3. Vérifiez que le mot de passe est correct
4. Pour Gmail : Activez l'accès des applications moins sécurisées (ou mieux : utilisez un mot de passe d'application)

### "Timed out"

**Cause** : Pare-feu ou serveur SMTP inaccessible

**Solutions** :
1. Vérifiez votre connexion Internet
2. Vérifiez le pare-feu (autorisez les ports 587 et 465 sortants)
3. Vérifiez que le serveur SMTP est correct

### "SMTP AUTH extension not supported"

**Cause** : Le serveur ne supporte pas l'authentification

**Solutions** :
1. Vérifiez l'adresse du serveur SMTP
2. Contactez votre fournisseur d'email

---

## 🧪 Tester la configuration

### Via l'interface web

1. Remplissez tous les champs
2. Cliquez sur **"💾 Sauvegarder"**
3. Cliquez sur **"✉️ Tester"**
4. Vérifiez la réception de l'email de test

### Via la ligne de commande (test avancé)

```bash
python3 -c "
import smtplib
from email.mime.text import MIMEText

server = 'smtp.gmail.com'
port = 587
email = 'votre@email.com'
password = 'votre_mot_de_passe'
destinataire = 'test@exemple.com'

msg = MIMEText('Test')
msg['Subject'] = 'Test SMTP'
msg['From'] = email
msg['To'] = destinataire

with smtplib.SMTP(server, port) as s:
    s.starttls()
    s.login(email, password)
    s.send_message(msg)
    
print('Email envoyé !')
"
```

---

## 📝 Conseils

### Sécurité

- ✅ Utilisez toujours des mots de passe d'application (Gmail, Yahoo)
- ✅ Préférez le port 587 ou 465 (sécurisés)
- ✅ Ne partagez jamais vos identifiants
- ❌ N'utilisez pas le port 25 (non sécurisé)

### Performance

- Pour plusieurs destinataires, séparez-les par des virgules : `email1@test.com, email2@test.com`
- Les emails sont envoyés de manière asynchrone (pas de ralentissement du monitoring)

### Dépannage

1. **Toujours tester** après configuration avec le bouton "✉️ Tester"
2. **Consulter les logs** : `logs/app.log` pour plus de détails
3. **Port bloqué** ? Vérifiez votre pare-feu et votre fournisseur Internet

---

## 🔍 Vérifier la configuration depuis les logs

```bash
# Voir les erreurs SMTP
tail -f logs/app.log | grep -i smtp

# Logs Raspberry Pi
tail -f ~/ping-u/logs/app.log | grep -i smtp
```

---

## 📞 Support

Si vous rencontrez des problèmes :

1. Vérifiez les logs : `logs/app.log`
2. Testez avec un autre port (587 ↔ 465)
3. Vérifiez auprès de votre fournisseur d'email
4. Consultez la documentation de votre fournisseur SMTP

---

**💡 Astuce** : La configuration SMTP la plus fiable est **Gmail avec un mot de passe d'application** sur le **port 587**.

