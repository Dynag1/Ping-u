## Copyright Dynag ##
## https://prog.dynag.co ##
## lic.py - Wrapper vers le système sécurisé ##

"""
Ce module est un wrapper vers le nouveau système de licences sécurisées.
Toutes les fonctions redirigent vers lic_secure pour une compatibilité totale.
"""

try:
    from src.lic_secure import (
        verify_license,
        jours_restants_licence,
        generate_activation_code,
        lire_param_gene
    )
except ImportError as e:
    # Mode headless sans cryptography - fonctions factices
    import sys
    print(f"⚠️ Module licence non disponible: {e}", file=sys.stderr)
    
    def verify_license(*args, **kwargs):
        return True  # Licence toujours valide en mode dégradé
    
    def jours_restants_licence(*args, **kwargs):
        return "∞"  # Illimité en mode dégradé
    
    def generate_activation_code(*args, **kwargs):
        return "HEADLESS-MODE"
    
    def lire_param_gene():
        return {}

# Exposer toutes les fonctions pour compatibilité
__all__ = [
    'verify_license',
    'jours_restants_licence', 
    'generate_activation_code',
    'lire_param_gene'
]
