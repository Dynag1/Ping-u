#!/usr/bin/env python3
"""
Script de test pour le module url_parser.
Vérifie le parsing des adresses avec ports.
"""

import sys
import os

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.url_parser import parse_host_port, normalize_monitoring_address

def test_parse_host_port():
    """Test de la fonction parse_host_port avec différents formats."""
    
    test_cases = [
        # (input, expected_host, expected_port, expected_protocol, expected_has_port)
        ("192.168.1.1:8080", "192.168.1.1", 8080, None, True),
        ("https://example.com:8443", "example.com", 8443, "https", True),
        ("http://site.com:8080", "site.com", 8080, "http", True),
        ("192.168.1.1", "192.168.1.1", None, None, False),
        ("https://example.com", "example.com", 443, "https", False),
        ("http://example.com", "example.com", 80, "http", False),
        ("example.com:3000", "example.com", 3000, None, True),
        ("h.dynag.co:8888", "h.dynag.co", 8888, None, True),
        ("https://h.dynag.co:8888", "h.dynag.co", 8888, "https", True),
    ]
    
    print("=" * 80)
    print("Test de parse_host_port()")
    print("=" * 80)
    
    all_passed = True
    
    for address, expected_host, expected_port, expected_protocol, expected_has_port in test_cases:
        result = parse_host_port(address)
        
        # Vérifier les résultats
        passed = (
            result['host'] == expected_host and
            result['port'] == expected_port and
            result['protocol'] == expected_protocol and
            result['has_port'] == expected_has_port
        )
        
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"\n{status} | {address}")
        print(f"  Host: {result['host']} (attendu: {expected_host})")
        print(f"  Port: {result['port']} (attendu: {expected_port})")
        print(f"  Protocol: {result['protocol']} (attendu: {expected_protocol})")
        print(f"  Has Port: {result['has_port']} (attendu: {expected_has_port})")
        
        if not passed:
            all_passed = False
    
    return all_passed


def test_normalize_monitoring_address():
    """Test de la fonction normalize_monitoring_address."""
    
    test_cases = [
        # (input, expected_normalized)
        ("192.168.1.1:8080", "192.168.1.1:8080"),
        ("https://example.com:8443", "https://example.com:8443"),
        ("http://site.com:8080", "http://site.com:8080"),
        ("192.168.1.1", "192.168.1.1"),
        ("https://example.com", "https://example.com"),
        ("example.com:3000", "example.com:3000"),
    ]
    
    print("\n" + "=" * 80)
    print("Test de normalize_monitoring_address()")
    print("=" * 80)
    
    all_passed = True
    
    for address, expected in test_cases:
        normalized, metadata = normalize_monitoring_address(address)
        
        passed = (normalized == expected)
        status = "✓ PASS" if passed else "✗ FAIL"
        
        print(f"\n{status} | {address}")
        print(f"  Normalisé: {normalized} (attendu: {expected})")
        
        if not passed:
            all_passed = False
    
    return all_passed


if __name__ == "__main__":
    print("\n🧪 Tests du module url_parser\n")
    
    test1_passed = test_parse_host_port()
    test2_passed = test_normalize_monitoring_address()
    
    print("\n" + "=" * 80)
    print("RÉSUMÉ DES TESTS")
    print("=" * 80)
    print(f"parse_host_port: {'✓ PASS' if test1_passed else '✗ FAIL'}")
    print(f"normalize_monitoring_address: {'✓ PASS' if test2_passed else '✗ FAIL'}")
    
    if test1_passed and test2_passed:
        print("\n✅ Tous les tests sont passés avec succès!")
        sys.exit(0)
    else:
        print("\n❌ Certains tests ont échoué.")
        sys.exit(1)
