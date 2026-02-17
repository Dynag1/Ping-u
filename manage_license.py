#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de gestion de licence pour Ping ü
Permet de vérifier, générer un code d'activation, ou créer une licence de développement
"""

import sys
import os
from datetime import datetime, timedelta
import pickle

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.lic_secure import LicenseManager

def print_separator():
    print("=" * 70)

def check_license():
    """Vérifie la licence actuelle"""
    lm = LicenseManager()
    
    print_separator()
    print("📋 VÉRIFICATION DE LA LICENCE")
    print_separator()
    
    is_valid = lm.verify_license()
    days_left = lm.jours_restants_licence()
    info = lm.get_license_info()
    
    print(f"Statut: {'✅ VALIDE' if is_valid else '❌ INVALIDE'}")
    print(f"Jours restants: {days_left}")
    
    if info:
        print(f"Date d'expiration: {info.get('expiry')}")
        print(f"Date d'émission: {info.get('issued')}")
        print(f"Logiciel: {info.get('software')}")
    else:
        print("\n⚠️  La licence est invalide ou liée à une autre machine")
        print("    Raisons possibles:")
        print("    - Le fichier de licence est pour une autre machine (ID matériel différent)")
        print("    - La licence a expiré")
        print("    - Le fichier de licence est corrompu")
    
    print_separator()

def generate_activation_code():
    """Génère un code d'activation pour cette machine"""
    lm = LicenseManager()
    
    print_separator()
    print("🔑 GÉNÉRATION DU CODE D'ACTIVATION")
    print_separator()
    
    hw_id = lm._get_hardware_id()
    activation_code = lm.generate_activation_code()
    
    print(f"ID Matériel: {hw_id}")
    print(f"\nCode d'activation:\n")
    print(f"    {activation_code}")
    print(f"\n📧 Envoyez ce code à votre fournisseur de licence pour obtenir une clé.")
    print_separator()

def create_dev_license(days=365):
    """Crée une licence de développement locale (POUR TESTS UNIQUEMENT)"""
    lm = LicenseManager()
    
    print_separator()
    print("🛠️  CRÉATION D'UNE LICENCE DE DÉVELOPPEMENT")
    print_separator()
    print("⚠️  ATTENTION: Ceci est pour les tests/développement uniquement!")
    print(f"    Durée: {days} jours")
    
    confirmation = input("\nContinuer? (oui/non): ")
    if confirmation.lower() not in ['oui', 'yes', 'y', 'o']:
        print("Annulé.")
        return
    
    # Créer les données de licence
    hw_id = lm._get_hardware_id()
    now = datetime.now()
    expiry = now + timedelta(days=days)
    
    license_data = {
        'hw_id': hw_id,
        'expiry': expiry.strftime('%Y-%m-%d'),
        'issued': now.strftime('%Y-%m-%d'),
        'software': 'PyngOuin',
        'type': 'development'
    }
    
    # ATTENTION: Pour créer une vraie licence, il faudrait la chiffrer
    # Pour le dev, on crée juste une licence non-chiffrée en pickle
    
    # Créer le répertoire si nécessaire
    os.makedirs("bd/tabs", exist_ok=True)
    
    # Sauvegarder en pickle (format simplifié pour le dev)
    # Note: Le vrai système utilise du chiffrement AES
    with open("bd/tabs/tabG", "wb") as f:
        # Le format attendu est: pickle.dump([var0, license_key, var2, ...], f)
        # Pour simplifier, on met juste la licence en position 1
        pickle.dump([None, None], f)  # Placeholder - licence non-chiffrée ne fonctionnera pas
    
    print(f"\n❌ Impossible de créer une licence de développement valide")
    print(f"   Le système de licence utilise du chiffrement AES-256 + HMAC")
    print(f"   Seul le serveur PHP peut générer des licences valides.")
    print(f"\n💡 Solution:")
    print(f"   1. Utilisez le code d'activation ci-dessus")
    print(f"   2. Ou désactivez temporairement la vérification de licence dans le code")
    print_separator()

def menu():
    """Menu principal"""
    print("\n" + "="*70)
    print(" GESTIONNAIRE DE LICENCE - Ping ü")
    print("="*70)
    print("\nOptions:")
    print("  1. Vérifier la licence actuelle")
    print("  2. Générer un code d'activation")
    print("  3. Info: Créer une licence de développement (ne fonctionne pas)")
    print("  4. Quitter")
    print()
    
    choice = input("Votre choix: ")
    
    if choice == "1":
        check_license()
    elif choice == "2":
        generate_activation_code()
    elif choice == "3":
        create_dev_license()
    elif choice == "4":
        print("Au revoir!")
        sys.exit(0)
    else:
        print("❌ Choix invalide")
    
    input("\nAppuyez sur Entrée pour continuer...")
    menu()

if __name__ == "__main__":
    try:
        if len(sys.argv) > 1:
            if sys.argv[1] == "check":
                check_license()
            elif sys.argv[1] == "activate":
                generate_activation_code()
            else:
                print(f"Usage: {sys.argv[0]} [check|activate]")
        else:
            menu()
    except KeyboardInterrupt:
        print("\n\nInterrompu par l'utilisateur.")
        sys.exit(0)
