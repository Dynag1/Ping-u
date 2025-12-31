## Copyright Dynag ##
## https://prog.dynag.co ##
## lic_secure.py - Système de licence sécurisé (compatible PHP) ##

import os
import pickle
import platform
import uuid
import hashlib
import hmac
import base64
import json
from datetime import datetime

# Import optionnel de cryptography (pas nécessaire en mode headless)
try:
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import hashes, padding as sym_padding
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    Cipher = None
    algorithms = None
    modes = None
    default_backend = None
    hashes = None
    sym_padding = None

class LicenseManager:
    """Gestionnaire de licence sécurisé (compatible avec génération PHP)"""
    
    # Clés de chiffrement (doivent être identiques côté PHP)
    # ⚠️ CHANGEZ CES VALEURS EN PRODUCTION !
    _MASTER_KEY = b'514zlF0wPREQlrr3UB0004naWwE1'  # 28 bytes
    _SALT = b'PyngOuin2025Salt'  # 16 bytes
    
    def __init__(self):
        """Initialise le gestionnaire de licence"""
        self._aes_key = self._derive_key()
    
    def _derive_key(self):
        """Dérive une clé AES-256 depuis la clé maître"""
        # PBKDF2 avec 100k itérations pour ralentir les attaques
        key = hashlib.pbkdf2_hmac(
            'sha256',
            self._MASTER_KEY,
            self._SALT,
            100000,
            dklen=32  # 256 bits pour AES-256
        )
        return key
    
    def _get_hardware_id(self):
        """
        Génère un ID matériel unique et stable.
        DOIT être identique à la version PHP pour la validation.
        Retourne 32 caractères hexadécimaux (0-9a-f).
        """
        # Composants matériels
        hostname = platform.node()
        mac = format(uuid.getnode(), 'x')
        machine = platform.machine()
        processor = platform.processor()
        
        # Combinaison (format identique au PHP)
        combined = f"{hostname}|{mac}|{machine}|{processor}"
        
        # Triple hash (identique au PHP)
        hash1 = hashlib.sha256((combined + self._SALT.decode()).encode('utf-8')).digest()
        hash2 = hashlib.sha512(hash1).digest()
        hash3 = hashlib.blake2b(hash2).hexdigest()
        
        # Retourner les 32 premiers caractères hexadécimaux
        return hash3[:32]
    
    def generate_activation_code(self):
        """
        Génère un code d'activation unique pour cette machine.
        Ce code doit être envoyé au serveur PHP pour obtenir une licence.
        """
        hw_id = self._get_hardware_id()
        timestamp = datetime.now().strftime('%Y%m%d')
        
        # Checksum pour valider le code
        checksum = hashlib.sha256(
            f"{hw_id}{timestamp}{self._MASTER_KEY.decode('latin-1')}".encode()
        ).hexdigest()[:8].upper()
        
        return f"ACT-{hw_id}-{timestamp}-{checksum}"
    
    def verify_license(self, license_key=None):
        """
        Vérifie si la licence est valide.
        
        Args:
            license_key: str - Clé de licence (si None, lit depuis le fichier)
            
        Returns:
            bool: True si licence valide, False sinon
        """
        try:
            # Lire la licence depuis le fichier si non fournie
            if license_key is None:
                license_key = self._read_license_from_file()
            
            if not license_key:
                return False
            
            # Décoder et déchiffrer
            license_data = self._decrypt_license(license_key)
            
            if not license_data:
                return False
            
            # Vérifications de sécurité
            
            # 1. Vérifier l'ID matériel
            current_hw_id = self._get_hardware_id()
            if license_data.get('hw_id') != current_hw_id:
                return False
            
            # 2. Vérifier la date d'expiration
            expiry_str = license_data.get('expiry')
            if not expiry_str:
                return False
                
            expiry_date = datetime.strptime(expiry_str, '%Y-%m-%d')
            if datetime.now() > expiry_date:
                return False
            
            # 3. Vérifier l'intégrité des données
            required_fields = ['hw_id', 'expiry', 'software', 'issued']
            if not all(field in license_data for field in required_fields):
                return False
            
            # 4. Vérifier le logiciel
            if license_data.get('software') != 'PyngOuin':
                return False
            
            # Toutes les vérifications passées
            return True
            
        except Exception as e:
            # Ne pas révéler les détails de l'erreur
            return False
    
    def _decrypt_license(self, license_key):
        """
        Déchiffre une licence générée par PHP.
        
        Format de la licence chiffrée (base64) :
        - 16 bytes : IV
        - N bytes  : Données chiffrées (JSON)
        - 32 bytes : HMAC-SHA256 de (IV + données chiffrées)
        
        Returns:
            dict: Données de licence déchiffrées ou None
        """
        # cryptography non disponible (mode headless)
        if not CRYPTO_AVAILABLE:
            return None
        
        try:
            # Décoder depuis Base64
            encrypted_data = base64.b64decode(license_key)
            
            # Extraire IV, données chiffrées et HMAC
            iv = encrypted_data[:16]
            hmac_received = encrypted_data[-32:]
            ciphertext = encrypted_data[16:-32]
            
            # Vérifier le HMAC
            hmac_calculated = hmac.new(
                self._aes_key,
                iv + ciphertext,
                hashlib.sha256
            ).digest()
            
            if not hmac.compare_digest(hmac_calculated, hmac_received):
                return None
            
            # Déchiffrer avec AES-256-CBC
            cipher = Cipher(
                algorithms.AES(self._aes_key),
                modes.CBC(iv),
                backend=default_backend()
            )
            decryptor = cipher.decryptor()
            padded_data = decryptor.update(ciphertext) + decryptor.finalize()
            
            # Retirer le padding PKCS7
            unpadder = sym_padding.PKCS7(128).unpadder()
            data = unpadder.update(padded_data) + unpadder.finalize()
            
            # Parser le JSON
            license_data = json.loads(data.decode('utf-8'))
            
            return license_data
            
        except Exception as e:
            return None
    
    def jours_restants_licence(self, license_key=None):
        """
        Retourne le nombre de jours restants avant expiration.
        
        Returns:
            str: Nombre de jours ou message d'erreur
        """
        try:
            if license_key is None:
                license_key = self._read_license_from_file()
            
            if not license_key:
                return "Aucune licence"
            
            # Décoder la licence
            license_data = self._decrypt_license(license_key)
            
            if not license_data:
                return "Licence invalide"
            
            # Calculer les jours restants
            expiry_date = datetime.strptime(license_data['expiry'], '%Y-%m-%d')
            days_left = (expiry_date - datetime.now()).days
            
            if days_left < 0:
                return "Expirée"
            elif days_left == 0:
                return "Expire aujourd'hui"
            else:
                return str(days_left)
                
        except Exception:
            return "Erreur"
    
    def get_license_info(self, license_key=None):
        """
        Retourne les informations détaillées de la licence.
        
        Returns:
            dict: Informations de licence ou None si invalide
        """
        try:
            if license_key is None:
                license_key = self._read_license_from_file()
            
            if not license_key:
                return None
            
            # Décoder la licence
            license_data = self._decrypt_license(license_key)
            
            if not license_data:
                return None
            
            # Vérifier que c'est bien pour cette machine
            if license_data.get('hw_id') != self._get_hardware_id():
                return None
            
            return {
                'expiry': license_data.get('expiry'),
                'issued': license_data.get('issued'),
                'software': license_data.get('software'),
                'days_left': self.jours_restants_licence(license_key),
                'hardware_bound': True
            }
            
        except:
            return None
    
    def _read_license_from_file(self):
        """Lit la licence depuis le fichier de configuration"""
        fichier = "bd/tabs/tabG"
        try:
            if os.path.isfile(fichier):
                with open(fichier, "rb") as f:
                    variables = pickle.load(f)
                    return variables[1] if len(variables) > 1 else None
        except:
            return None
        return None


# ═══════════════════════════════════════════════════════════
# FONCTIONS DE COMPATIBILITÉ (pour ne pas casser le code existant)
# ═══════════════════════════════════════════════════════════

_license_manager = None

def _get_manager():
    """Retourne l'instance singleton du gestionnaire"""
    global _license_manager
    if _license_manager is None:
        _license_manager = LicenseManager()
    return _license_manager

def verify_license(license_key=None):
    """Vérifie si la licence est valide (compatibilité)"""
    try:
        return _get_manager().verify_license(license_key)
    except:
        return False

def jours_restants_licence(license_key=None):
    """Retourne le nombre de jours restants (compatibilité)"""
    try:
        return _get_manager().jours_restants_licence(license_key)
    except:
        return "Erreur"

def generate_activation_code():
    """Génère un code d'activation (compatibilité)"""
    try:
        return _get_manager().generate_activation_code()
    except:
        return "Erreur"

def lire_param_gene():
    """Lit les paramètres généraux (compatibilité)"""
    try:
        return _get_manager()._read_license_from_file()
    except:
        return None
