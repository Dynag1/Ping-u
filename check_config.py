#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de diagnostic pour vérifier la configuration de Ping ü
Exécutez ce script sur le Raspberry pour diagnostiquer les problèmes d'alertes
"""

import pickle
import os
import sys

def check_tab4():
    """Vérifie et affiche le contenu du fichier tab4 (paramètres monitoring)"""
    print("\n" + "=" * 60)
    print("📋 DIAGNOSTIC CONFIGURATION PING Ü")
    print("=" * 60)
    
    fichier = "tab4"
    
    if not os.path.exists(fichier):
        print(f"\n❌ Le fichier '{fichier}' n'existe pas !")
        print("💡 Conseil: Exécutez 'python init_raspberry.py' pour créer les fichiers")
        return False
    
    try:
        with open(fichier, 'rb') as f:
            data = pickle.load(f)
        
        print(f"\n✅ Fichier '{fichier}' trouvé et lisible")
        print(f"\n📊 Contenu du fichier:")
        print("-" * 40)
        
        # Format attendu: [delais, nbr_hs, popup, mail, telegram, mail_recap, db_externe]
        labels = ['delais', 'nbrHs', 'popup', 'mail', 'telegram', 'mailRecap', 'dbExterne']
        
        for i, value in enumerate(data):
            label = labels[i] if i < len(labels) else f'param[{i}]'
            print(f"   {label}: {value} ({type(value).__name__})")
        
        print("-" * 40)
        
        # Vérifier nbrHs spécifiquement
        if len(data) >= 2:
            nbrHs = data[1]
            print(f"\n🎯 Valeur de nbrHs: {nbrHs}")
            
            if nbrHs == 1:
                print("⚠️  PROBLÈME DÉTECTÉ: nbrHs = 1")
                print("   Cela signifie qu'une alerte sera envoyée dès le PREMIER ping échoué !")
                print("\n💡 Solution: Modifiez la valeur avec l'option --fix")
                return False
            elif nbrHs < 1:
                print(f"⚠️  PROBLÈME DÉTECTÉ: nbrHs = {nbrHs} (invalide)")
                return False
            else:
                print(f"✅ Configuration correcte: {nbrHs} pings échoués avant alerte")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erreur lors de la lecture de '{fichier}': {e}")
        return False

def fix_nbrHs(new_value=3):
    """Corrige la valeur de nbrHs dans le fichier tab4"""
    fichier = "tab4"
    
    if not os.path.exists(fichier):
        print(f"❌ Le fichier '{fichier}' n'existe pas")
        return False
    
    try:
        # Lire les données existantes
        with open(fichier, 'rb') as f:
            data = pickle.load(f)
        
        old_value = data[1] if len(data) >= 2 else "N/A"
        
        # Modifier nbrHs (index 1)
        if len(data) >= 2:
            data[1] = new_value
        else:
            print(f"❌ Format de fichier invalide")
            return False
        
        # Sauvegarder
        with open(fichier, 'wb') as f:
            pickle.dump(data, f)
        
        print(f"\n✅ nbrHs modifié: {old_value} → {new_value}")
        print("💡 Redémarrez l'application pour appliquer les changements:")
        print("   python Pingu.py -stop")
        print("   python Pingu.py -start")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def show_var_values():
    """Affiche les valeurs actuelles du module var"""
    print("\n📊 Valeurs dans le module var:")
    print("-" * 40)
    try:
        from src import var
        print(f"   var.nbrHs = {var.nbrHs}")
        print(f"   var.delais = {var.delais}")
        print(f"   var.popup = {var.popup}")
        print(f"   var.mail = {var.mail}")
        print(f"   var.telegram = {var.telegram}")
        print(f"   var.liste_hs = {dict(var.liste_hs)}")
        print(f"   var.liste_mail = {dict(var.liste_mail)}")
        print(f"   var.liste_telegram = {dict(var.liste_telegram)}")
    except Exception as e:
        print(f"   Erreur import var: {e}")

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Diagnostic de configuration Ping ü')
    parser.add_argument('--fix', type=int, nargs='?', const=3, metavar='N',
                       help='Corrige nbrHs à la valeur spécifiée (défaut: 3)')
    parser.add_argument('--var', action='store_true',
                       help='Affiche les valeurs du module var')
    
    args = parser.parse_args()
    
    if args.fix is not None:
        fix_nbrHs(args.fix)
    elif args.var:
        show_var_values()
    else:
        check_tab4()
    
    print("\n" + "=" * 60)
    print("📖 Utilisation:")
    print("   python check_config.py          # Vérifier la config")
    print("   python check_config.py --fix    # Corriger nbrHs à 3")
    print("   python check_config.py --fix 5  # Corriger nbrHs à 5")
    print("   python check_config.py --var    # Voir les valeurs var")
    print("=" * 60 + "\n")

