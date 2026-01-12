"""
Module de vérification HTTP/HTTPS pour la surveillance de sites web.
Permet de vérifier la disponibilité d'un site web via des requêtes HTTP/HTTPS.
"""

import aiohttp
import asyncio
import time
import re
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)


class HTTPChecker:
    """Classe pour effectuer des vérifications HTTP/HTTPS sur des sites web."""
    
    def __init__(self, timeout=5, follow_redirects=True, verify_ssl=True):
        """
        Initialise le vérificateur HTTP.
        
        Args:
            timeout: Timeout en secondes pour les requêtes
            follow_redirects: Suivre les redirections HTTP
            verify_ssl: Vérifier les certificats SSL (False pour auto-signés)
        """
        self.timeout = timeout
        self.follow_redirects = follow_redirects
        self.verify_ssl = verify_ssl
    
    @staticmethod
    def is_valid_url(url):
        """
        Vérifie si une URL est valide.
        
        Args:
            url: URL ou domaine à vérifier
            
        Returns:
            bool: True si valide, False sinon
        """
        if not url or not isinstance(url, str):
            return False
        
        url = url.strip()
        
        # Vérifier format domaine simple (ex: google.com)
        domain_pattern = r'^([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'
        if re.match(domain_pattern, url):
            return True
        
        # Vérifier URL complète
        try:
            result = urlparse(url)
            return all([result.scheme in ['http', 'https'], result.netloc])
        except:
            return False
    
    @staticmethod
    def normalize_url(url):
        """
        Normalise une URL en ajoutant le protocole si manquant.
        Essaie HTTPS en premier, puis HTTP en fallback.
        Préserve les ports personnalisés s'ils sont spécifiés.
        
        Args:
            url: URL ou domaine à normaliser
            
        Returns:
            str: URL normalisée avec protocole
        """
        if not url:
            return None
        
        url = url.strip()
        
        # Si déjà un protocole, retourner tel quel (préserve le port)
        if url.startswith('http://') or url.startswith('https://'):
            return url
        
        # Sinon, ajouter https:// par défaut (le plus courant)
        # Préserve le port s'il est présent (ex: example.com:8443 -> https://example.com:8443)
        return f'https://{url}'

    
    async def check_website(self, url, timeout=None):
        """
        Vérifie la disponibilité d'un site web via HTTP/HTTPS.
        
        Args:
            url: URL complète ou domaine du site à vérifier
            timeout: Timeout custom (utilise self.timeout si None)
            
        Returns:
            dict: {
                'success': bool,
                'status_code': int ou None,
                'response_time_ms': float,
                'final_url': str (après redirections),
                'error': str ou None
            }
        """
        # Normaliser l'URL
        normalized_url = self.normalize_url(url)
        
        if not self.is_valid_url(url):
            return {
                'success': False,
                'status_code': None,
                'response_time_ms': 0,
                'final_url': normalized_url,
                'error': 'URL invalide'
            }
        
        timeout_value = timeout if timeout is not None else self.timeout
        
        # Préparer la session HTTP
        connector = aiohttp.TCPConnector(ssl=self.verify_ssl)
        timeout_obj = aiohttp.ClientTimeout(total=timeout_value)
        
        start_time = time.time()
        
        try:
            async with aiohttp.ClientSession(connector=connector, timeout=timeout_obj) as session:
                # Essayer d'abord avec HTTPS si pas de protocole spécifié dans l'URL originale
                urls_to_try = [normalized_url]
                
                # Si HTTPS échoue sur un domaine simple, essayer HTTP en fallback
                if not url.startswith('http://') and not url.startswith('https://'):
                    urls_to_try.append(f'http://{url}')
                
                last_error = None
                
                for try_url in urls_to_try:
                    try:
                        async with session.get(
                            try_url,
                            allow_redirects=self.follow_redirects
                        ) as response:
                            response_time_ms = (time.time() - start_time) * 1000
                            
                            # Codes 2xx et 3xx sont considérés comme succès
                            success = 200 <= response.status < 400
                            
                            return {
                                'success': success,
                                'status_code': response.status,
                                'response_time_ms': round(response_time_ms, 2),
                                'final_url': str(response.url),
                                'error': None if success else f'HTTP {response.status}'
                            }
                    except aiohttp.ClientSSLError as e:
                        # Si erreur SSL avec HTTPS, essayer HTTP
                        last_error = f'Erreur SSL: {str(e)}'
                        logger.info(f"SSL error for {try_url}, trying next URL if available: {e}")
                        continue
                    except aiohttp.ClientConnectorError as e:
                        # Erreur de connexion (DNS, réseau, etc.)
                        last_error = f'Erreur de connexion: {str(e)}'
                        logger.info(f"Connection error for {try_url}: {e}")
                        continue
                    except aiohttp.ClientError as e:
                        # Autres erreurs client (timeout, etc.)
                        last_error = f'Erreur client: {str(e)}'
                        logger.info(f"Client error for {try_url}: {e}")
                        continue
                    except Exception as e:
                        last_error = f'Erreur inattendue: {str(e)}'
                        logger.warning(f"Unexpected error for {try_url}: {e}")
                        continue
                
                # Si aucune URL n'a fonctionné
                response_time_ms = (time.time() - start_time) * 1000
                return {
                    'success': False,
                    'status_code': None,
                    'response_time_ms': round(response_time_ms, 2),
                    'final_url': normalized_url,
                    'error': last_error or 'Connection failed'
                }
                
        except asyncio.TimeoutError:
            response_time_ms = (time.time() - start_time) * 1000
            return {
                'success': False,
                'status_code': None,
                'response_time_ms': round(response_time_ms, 2),
                'final_url': normalized_url,
                'error': 'Timeout'
            }
        except Exception as e:
            response_time_ms = (time.time() - start_time) * 1000
            logger.error(f"HTTP check error for {normalized_url}: {e}")
            return {
                'success': False,
                'status_code': None,
                'response_time_ms': round(response_time_ms, 2),
                'final_url': normalized_url,
                'error': str(e)
            }


# Instance globale par défaut
# Timeout augmenté à 10s pour éviter les faux positifs sur les sites lents
http_checker = HTTPChecker(timeout=10, follow_redirects=True, verify_ssl=False)


# Fonction helper pour usage synchrone
def check_website_sync(url, timeout=5):
    """
    Version synchrone de check_website pour utilisation dans du code non-async.
    
    Args:
        url: URL du site à vérifier
        timeout: Timeout en secondes
        
    Returns:
        dict: Résultat de la vérification
    """
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(http_checker.check_website(url, timeout))
        loop.close()
        return result
    except Exception as e:
        logger.error(f"Error in check_website_sync: {e}")
        return {
            'success': False,
            'status_code': None,
            'response_time_ms': 0,
            'final_url': url,
            'error': str(e)
        }
