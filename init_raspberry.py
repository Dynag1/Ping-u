#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script d'initialisation pour Ping ü sur Raspberry Pi
Crée les fichiers de configuration manquants
"""

import pickle
import os
import sys

def create_config_files():
    """Crée les fichiers de configuration par défaut"""
    
    print("🔧 Initialisation des fichiers de configuration pour Ping ü")
    print("=" * 60)
    
    # Fichier tab - Paramètres mail
    if not os.path.exists('tab'):
        print("📧 Création du fichier 'tab' (paramètres mail)...")
        mail_params = ['', '', '', '']  # [serveur, port, expediteur, mot_de_passe]
        try:
            with open('tab', 'wb') as f:
                pickle.dump(mail_params, f)
            print("   ✅ Fichier 'tab' créé")
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
            return False
    else:
        print("   ⏭️  Fichier 'tab' existe déjà")
    
    # Fichier tabG - Paramètres généraux
    if not os.path.exists('tabG'):
        print("⚙️  Création du fichier 'tabG' (paramètres généraux)...")
        general_params = ['MonRaspberry', 'fr', 'light']  # [nom_site, langue, theme]
        try:
            with open('tabG', 'wb') as f:
                pickle.dump(general_params, f)
            print("   ✅ Fichier 'tabG' créé")
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
            return False
    else:
        print("   ⏭️  Fichier 'tabG' existe déjà")
    
    # Fichier tab4 - Paramètres principaux
    if not os.path.exists('tab4'):
        print("🔄 Création du fichier 'tab4' (paramètres monitoring)...")
        # [delais, nbr_hs, popup, mail, telegram, mail_recap, db_externe]
        monitoring_params = [10, 3, False, False, False, False, False]
        try:
            with open('tab4', 'wb') as f:
                pickle.dump(monitoring_params, f)
            print("   ✅ Fichier 'tab4' créé")
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
            return False
    else:
        print("   ⏭️  Fichier 'tab4' existe déjà")
    
    # Fichier tabr - Paramètres mail récapitulatif
    if not os.path.exists('tabr'):
        print("📨 Création du fichier 'tabr' (mail récap)...")
        mail_recap_params = []  # Liste vide par défaut
        try:
            with open('tabr', 'wb') as f:
                pickle.dump(mail_recap_params, f)
            print("   ✅ Fichier 'tabr' créé")
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
            return False
    else:
        print("   ⏭️  Fichier 'tabr' existe déjà")
    
    # Créer le dossier bd si nécessaire
    if not os.path.exists('bd'):
        print("📁 Création du dossier 'bd'...")
        try:
            os.makedirs('bd', exist_ok=True)
            print("   ✅ Dossier 'bd' créé")
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
            return False
    else:
        print("   ⏭️  Dossier 'bd' existe déjà")
    
    # Créer le fichier web_users.json si nécessaire
    if not os.path.exists('web_users.json'):
        print("👤 Création du fichier 'web_users.json' (utilisateurs web)...")
        import json
        import hashlib
        
        # Mot de passe par défaut: admin / admin
        default_password = hashlib.sha256('admin'.encode()).hexdigest()
        web_users = {
            'username': 'admin',
            'password': default_password
        }
        try:
            with open('web_users.json', 'w') as f:
                json.dump(web_users, f, indent=4)
            print("   ✅ Fichier 'web_users.json' créé")
            print("   ⚠️  Identifiants par défaut: admin / admin")
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
            return False
    else:
        print("   ⏭️  Fichier 'web_users.json' existe déjà")
    
    print("\n" + "=" * 60)
    print("✅ Initialisation terminée avec succès !")
    print("\n📝 Prochaines étapes:")
    print("   1. Configurer les permissions ping:")
    print("      sudo sysctl -w net.ipv4.ping_group_range=\"0 2147483647\"")
    print("   2. Lancer l'application:")
    print("      ./start_headless.sh")
    print("   3. Accéder à l'interface web:")
    print("      http://[IP_RASPBERRY]:9090")
    print("      (identifiants: admin / admin)")
    
    return True

def check_ping_permissions():
    """Vérifie si les permissions ping sont configurées"""
    print("\n🔍 Vérification des permissions ping...")
    
    try:
        import subprocess
        result = subprocess.run(['ping', '-c', '1', '-W', '1', '127.0.0.1'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("   ✅ Les pings fonctionnent correctement")
            return True
        else:
            print("   ⚠️  Les pings pourraient ne pas fonctionner")
            print("   💡 Exécutez: sudo sysctl -w net.ipv4.ping_group_range=\"0 2147483647\"")
            return False
    except Exception as e:
        print(f"   ❌ Erreur lors du test: {e}")
        return False

if __name__ == '__main__':
    print("\n" + "🐧" * 30)
    print("   INITIALISATION PING Ü - RASPBERRY PI")
    print("🐧" * 30 + "\n")
    
    if create_config_files():
        check_ping_permissions()
        sys.exit(0)
    else:
        print("\n❌ L'initialisation a échoué")
        sys.exit(1)

