#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de vérification et correction pour Raspberry Pi
"""

import os
import sys

def check_file_version(filepath, search_string):
    """Vérifie si un fichier contient une chaîne spécifique"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            return search_string in content
    except Exception as e:
        return False, str(e)

print("=" * 60)
print("🔍 Vérification de l'installation Ping ü sur Raspberry Pi")
print("=" * 60)

# 1. Vérifier thread_mail.py
print("\n1. Vérification de thread_mail.py...")
if check_file_version('src/thread_mail.py', 'if platform.system()'):
    print("   ✅ thread_mail.py est à jour (détection Linux)")
else:
    print("   ❌ thread_mail.py n'est PAS à jour")
    print("   → Vous devez synchroniser le fichier depuis votre PC Windows")

if check_file_version('src/thread_mail.py', 'port_int = int(port)'):
    print("   ✅ thread_mail.py contient la correction SMTP")
else:
    print("   ❌ thread_mail.py ne contient PAS la correction SMTP")

# 2. Vérifier admin.html
print("\n2. Vérification de admin.html...")
if check_file_version('src/web/templates/admin.html', 'Email Récapitulatif Périodique'):
    print("   ✅ admin.html contient la section mail récapitulatif")
else:
    print("   ❌ admin.html ne contient PAS la section mail récapitulatif")
    print("   → Vous devez synchroniser le fichier depuis votre PC Windows")

# 3. Vérifier email_sender.py
print("\n3. Vérification de email_sender.py...")
if os.path.exists('src/email_sender.py'):
    print("   ✅ email_sender.py existe")
else:
    print("   ❌ email_sender.py n'existe PAS")
    print("   → Vous devez créer ce fichier")

# 4. Test configuration SMTP
print("\n4. Test de la configuration SMTP...")
try:
    from src import db
    smtp_params = db.lire_param_mail()
    if smtp_params and len(smtp_params) >= 5:
        print(f"   ✅ Configuration SMTP trouvée")
        print(f"   Serveur: {smtp_params[0]}")
        print(f"   Port: {smtp_params[1]}")
        print(f"   Email: {smtp_params[2]}")
    else:
        print("   ⚠️  Configuration SMTP incomplète")
except Exception as e:
    print(f"   ❌ Erreur: {e}")

print("\n" + "=" * 60)
print("🔧 Actions recommandées:")
print("=" * 60)
print("""
1. Sur votre PC Windows, créez une archive avec tous les fichiers modifiés :
   - src/thread_mail.py
   - src/email_sender.py
   - src/web/templates/admin.html
   - Pingu.py

2. Transférez l'archive sur votre Raspberry Pi

3. Extrayez et remplacez les fichiers

4. Redémarrez l'application:
   python Pingu.py -stop
   python Pingu.py -start
""")

