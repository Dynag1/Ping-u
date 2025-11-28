## Copyright Dynag ##
## https://prog.dynag.co ##
## lic.py - Wrapper vers le système sécurisé ##

"""
Ce module est un wrapper vers le nouveau système de licences sécurisées.
Toutes les fonctions redirigent vers lic_secure pour une compatibilité totale.
"""

from src.lic_secure import (
    verify_license,
    jours_restants_licence,
    generate_activation_code,
    lire_param_gene
)

# Exposer toutes les fonctions pour compatibilité
__all__ = [
    'verify_license',
    'jours_restants_licence', 
    'generate_activation_code',
    'lire_param_gene'
]
