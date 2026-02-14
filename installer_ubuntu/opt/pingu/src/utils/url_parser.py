"""
Module de parsing et normalisation des adresses avec ports.
Supporte les formats: IP:port, http://host:port, https://host:port
"""

import re
from urllib.parse import urlparse
from typing import Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


def parse_host_port(address: str) -> Dict[str, Optional[str]]:
    """
    Parse une adresse pour extraire l'hôte, le port et le protocole.
    
    Formats supportés:
    - 192.168.1.1:8080
    - http://example.com:8080
    - https://example.com:8443
    - example.com:3000
    - 192.168.1.1 (sans port)
    - http://example.com (sans port)
    
    Args:
        address: Adresse à parser
        
    Returns:
        dict: {
            'host': str,           # Hôte sans port (IP ou domaine)
            'port': int ou None,   # Port numérique ou None si absent
            'protocol': str,       # 'http', 'https', ou None
            'original': str,       # Adresse originale
            'has_port': bool       # True si un port est spécifié
        }
    """
    if not address or not isinstance(address, str):
        return {
            'host': None,
            'port': None,
            'protocol': None,
            'original': address,
            'has_port': False
        }
    
    address = address.strip()
    original = address
    
    # Initialiser les valeurs par défaut
    host = address
    port = None
    protocol = None
    has_port = False
    
    # Cas 1: URL complète avec protocole (http:// ou https://)
    if address.startswith('http://') or address.startswith('https://'):
        try:
            parsed = urlparse(address)
            protocol = parsed.scheme
            host = parsed.hostname or parsed.netloc.split(':')[0]
            
            # Extraire le port si présent
            if parsed.port:
                port = parsed.port
                has_port = True
            else:
                # Port par défaut selon le protocole
                port = 443 if protocol == 'https' else 80
                has_port = False
            
            # Reconstruire le path si présent
            if parsed.path and parsed.path != '/':
                host = parsed.netloc.split(':')[0] + parsed.path
                
        except Exception as e:
            logger.warning(f"Erreur parsing URL {address}: {e}")
            # Fallback: traiter comme une adresse simple
            host = address
            port = None
            protocol = None
    
    # Cas 2: Adresse simple avec port (IP:port ou domain:port)
    elif ':' in address:
        # Vérifier que ce n'est pas une IPv6 (contient plusieurs ':')
        if address.count(':') == 1:
            parts = address.split(':')
            host = parts[0].strip()
            
            try:
                port_str = parts[1].strip()
                port = int(port_str)
                
                # Valider le port
                if not (1 <= port <= 65535):
                    logger.warning(f"Port invalide {port} dans {address}, ignoré")
                    port = None
                    has_port = False
                else:
                    has_port = True
                    
            except ValueError:
                logger.warning(f"Port non numérique dans {address}: {parts[1]}")
                port = None
                has_port = False
        else:
            # Probablement IPv6, ne pas parser le port
            host = address
            port = None
            has_port = False
    
    # Cas 3: Adresse simple sans port
    else:
        host = address
        port = None
        has_port = False
    
    return {
        'host': host,
        'port': port,
        'protocol': protocol,
        'original': original,
        'has_port': has_port
    }


def is_ip_address(host: str) -> bool:
    """
    Vérifie si une chaîne est une adresse IP valide (IPv4).
    
    Args:
        host: Chaîne à vérifier
        
    Returns:
        bool: True si c'est une IP valide
    """
    if not host:
        return False
    
    # Pattern IPv4
    ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    if not re.match(ip_pattern, host):
        return False
    
    # Vérifier que chaque octet est entre 0 et 255
    try:
        parts = host.split('.')
        return all(0 <= int(part) <= 255 for part in parts)
    except ValueError:
        return False


def is_domain(host: str) -> bool:
    """
    Vérifie si une chaîne est un nom de domaine valide.
    
    Args:
        host: Chaîne à vérifier
        
    Returns:
        bool: True si c'est un domaine valide
    """
    if not host:
        return False
    
    # Pattern domaine simple
    domain_pattern = r'^([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'
    return bool(re.match(domain_pattern, host))


def build_url(host: str, port: Optional[int] = None, protocol: Optional[str] = None) -> str:
    """
    Construit une URL complète à partir des composants.
    
    Args:
        host: Nom d'hôte ou IP
        port: Port (optionnel)
        protocol: Protocole 'http' ou 'https' (optionnel)
        
    Returns:
        str: URL complète
    """
    if not host:
        return ""
    
    # Si un protocole est spécifié
    if protocol:
        url = f"{protocol}://{host}"
        # Ajouter le port seulement s'il n'est pas le port par défaut
        if port and not (
            (protocol == 'http' and port == 80) or
            (protocol == 'https' and port == 443)
        ):
            url += f":{port}"
        return url
    
    # Sans protocole, format simple
    if port:
        return f"{host}:{port}"
    return host


def normalize_monitoring_address(address: str) -> Tuple[str, Dict]:
    """
    Normalise une adresse de monitoring et retourne l'adresse à utiliser
    pour la surveillance ainsi que les métadonnées.
    
    Args:
        address: Adresse originale
        
    Returns:
        tuple: (adresse_normalisée, métadonnées)
    """
    parsed = parse_host_port(address)
    
    # Pour les URLs avec protocole, garder l'URL complète
    if parsed['protocol']:
        normalized = build_url(
            parsed['host'],
            parsed['port'] if parsed['has_port'] else None,
            parsed['protocol']
        )
    # Pour les adresses simples avec port
    elif parsed['has_port']:
        normalized = f"{parsed['host']}:{parsed['port']}"
    # Pour les adresses simples sans port
    else:
        normalized = parsed['host']
    
    return normalized, parsed
