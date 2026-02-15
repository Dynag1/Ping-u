"""
Module de scan réseau unifié pour Ping ü
Détection automatique de périphériques : switches, caméras, serveurs
"""

import socket
import threading
import time
import asyncio
import binascii  # Pour Xiaomi handshake
from typing import Dict, List, Callable, Optional, Set
from dataclasses import dataclass
from enum import Enum

from src.Snyf import send, fct
from src.utils.logger import get_logger

logger = get_logger(__name__)


class DeviceType(Enum):
    """Types de périphériques détectables"""
    CAMERA_HIK = "camera_hikvision"
    CAMERA_DAHUA = "camera_dahua"
    CAMERA_XIAOMI = "camera_xiaomi"
    CAMERA_SAMSUNG = "camera_samsung"
    CAMERA_AVIGILON = "camera_avigilon"
    CAMERA_GENERIC = "camera_generic"
    SWITCH = "switch"
    SERVER = "server"
    UPS = "ups"
    UPNP_DEVICE = "upnp_device"
    UNKNOWN = "unknown"


@dataclass
class DiscoveredDevice:
    """Représente un périphérique découvert"""
    ip: str
    device_type: DeviceType
    manufacturer: str = ""
    model: str = ""
    name: str = ""
    mac: str = ""
    protocol: str = ""  # hik, onvif, dahua, snmp, upnp
    
    def to_dict(self) -> Dict:
        """Convertit en dictionnaire pour JSON"""
        return {
            'ip': self.ip,
            'type': self.device_type.value,
            'manufacturer': self.manufacturer,
            'model': self.model,
            'name': self.name,
            'mac': self.mac,
            'protocol': self.protocol
        }


class NetworkScanner:
    """Scanner réseau unifié avec support multi-protocoles"""
    
    def __init__(self):
        self.discovered_devices: Set[str] = set()  # IPs déjà découvertes
        self._scan_running = False
        self._callbacks: List[Callable] = []
        self.lock = threading.Lock()
        
    def add_callback(self, callback: Callable[[DiscoveredDevice], None]):
        """Ajoute un callback appelé à chaque découverte"""
        self._callbacks.append(callback)
        
    def _notify_device_found(self, device: DiscoveredDevice):
        """Notifie tous les callbacks d'une nouvelle découverte"""
        for callback in self._callbacks:
            try:
                callback(device)
            except Exception as e:
                logger.error(f"Erreur dans callback scan: {e}")
    
    def _is_new_device(self, ip: str, mac: str = "") -> bool:
        """Vérifie si c'est un nouveau périphérique"""
        identifier = mac if mac else ip
        with self.lock:
            if identifier in self.discovered_devices:
                return False
            self.discovered_devices.add(identifier)
            return True
    
    def scan_hikvision(self, timeout: int = 10):
        """Scan pour caméras Hikvision"""
        logger.info("Scan Hikvision démarré")
        
        def on_device(site, ip, model, mac, *args):
            """Callback quand un device HIK est trouvé"""
            # Valider que l'IP est correcte
            if not ip or not isinstance(ip, str) or ip.count('.') != 3:
                return
            
            # Extraire le nom s'il est présent dans les args
            name = ""
            if args and len(args) > 0:
                name = args[0]
                
            if self._is_new_device(ip, mac):
                device = DiscoveredDevice(
                    ip=ip,
                    device_type=DeviceType.CAMERA_HIK,
                    manufacturer="Hikvision",
                    model=model,
                    name=name,
                    mac=mac,
                    protocol="hikvision"
                )
                self._notify_device_found(device)
        
        # Créer un faux objet comm avec la méthode addRow
        class FakeComm:
            def __init__(self, callback):
                self.callback = callback
                
            class addRow:
                def __init__(self, callback):
                    self.callback = callback
                    
                def emit(self, *args):
                    self.callback(*args)
            
            def __init__(self, callback):
                self.addRow = self.addRow(callback)
        
        fake_comm = FakeComm(on_device)
        fake_comm.addRow = type('obj', (object,), {
            'emit': lambda self, *args: on_device(*args)
        })()
        
        # Lancer le scan HIK existant
        try:
            send.send("hik", fake_comm, None)
            time.sleep(timeout)
        except Exception as e:
            logger.error(f"Erreur scan Hikvision: {e}")
    
    def scan_onvif(self, timeout: int = 10):
        """Scan ONVIF pour caméras génériques"""
        logger.info("Scan ONVIF démarré")
        
        def on_device(site, ip, model, mac, *args):
            # Valider que l'IP est correcte
            if not ip or not isinstance(ip, str) or ip.count('.') != 3:
                return
                
            # Extraire le nom s'il est présent dans les args
            name = ""
            if args and len(args) > 0:
                name = args[0]
                
            if self._is_new_device(ip, mac):
                device = DiscoveredDevice(
                    ip=ip,
                    device_type=DeviceType.CAMERA_GENERIC,
                    model=model,
                    name=name,
                    mac=mac,
                    protocol="onvif"
                )
                self._notify_device_found(device)
        
        fake_comm = type('obj', (object,), {
            'addRow': type('obj', (object,), {
                'emit': lambda self, *args: on_device(*args)
            })()
        })()
        
        try:
            send.send("onvif", fake_comm, None)
            time.sleep(timeout)
        except Exception as e:
            logger.error(f"Erreur scan ONVIF: {e}")
    
    def scan_dahua(self, timeout: int = 10):
        """
        Scan pour caméras Dahua
        Protocole propriétaire Dahua sur UDP port 37810
        """
        logger.info("Scan Dahua démarré")
        
        # Message de découverte Dahua
        dahua_msg = b'\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00'
        port = 37810
        
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.settimeout(timeout)
        
        try:
            s.bind(('', 0))
            s.sendto(dahua_msg, ('255.255.255.255', port))
            
            start_time = time.time()
            while time.time() - start_time < timeout:
                try:
                    data, addr = s.recvfrom(4096)
                    ip = addr[0]
                    
                    if self._is_new_device(ip):
                        # Parse simple de la réponse Dahua
                        device = DiscoveredDevice(
                            ip=ip,
                            device_type=DeviceType.CAMERA_DAHUA,
                            manufacturer="Dahua",
                            protocol="dahua"
                        )
                        self._notify_device_found(device)
                except socket.timeout:
                    break
                except Exception as e:
                    logger.debug(f"Erreur parsing Dahua: {e}")
                    
        except Exception as e:
            logger.error(f"Erreur scan Dahua: {e}")
        finally:
            s.close()
    
    def scan_samsung(self, timeout: int = 10):
        """Scan Samsung (caméras et TV)"""
        logger.info("Scan Samsung démarré")
        
        def on_device(site, ip, model, mac, *args):
            # Valider que l'IP est correcte
            if not ip or not isinstance(ip, str) or ip.count('.') != 3:
                return
                
            # Extraire le nom s'il est présent dans les args
            name = ""
            if args and len(args) > 0:
                name = args[0]
                
            if self._is_new_device(ip, mac):
                device = DiscoveredDevice(
                    ip=ip,
                    device_type=DeviceType.CAMERA_SAMSUNG,
                    manufacturer="Samsung",
                    model=model,
                    name=name,
                    mac=mac,
                    protocol="samsung"
                )
                self._notify_device_found(device)
        
        fake_comm = type('obj', (object,), {
            'addRow': type('obj', (object,), {
                'emit': lambda self, *args: on_device(*args)
            })()
        })()
        
        try:
            send.send("samsung", fake_comm, None)
            time.sleep(timeout)
        except Exception as e:
            logger.error(f"Erreur scan Samsung: {e}")

    def scan_xiaomi(self, timeout: int = 10):
        """
        Scan pour caméras/équipements Xiaomi
        Protocole UDP miio sur port 54321
        """
        logger.info("Scan Xiaomi démarré")
        
        # Handshake Miio: '2131' + 30 bytes (0x00... ou 0xFF...)
        # Ici on envoie une payload de découverte standard
        xiaomi_msg = binascii.unhexlify("21310020ffffffffffffffffffffffffffffffffffffffffffffffffffffffff")
        port = 54321
        
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.settimeout(timeout)
        
        try:
            s.bind(('', 0))
            s.sendto(xiaomi_msg, ('255.255.255.255', port))
            
            start_time = time.time()
            while time.time() - start_time < timeout:
                try:
                    data, addr = s.recvfrom(4096)
                    ip = addr[0]
                    
                    if self._is_new_device(ip):
                        # Parser le header (2131 + length + unknown + device_id + stamp + md5)
                        # Le Device ID est à l'offset 8 (4 bytes)
                        manufacturer = "Xiaomi"
                        model = ""
                        name = "Xiaomi Device"
                        
                        if len(data) >= 32 and data[0:2] == b'\x21\x31':
                            try:
                                dev_id = data[8:12].hex()
                                model = f"ID: {dev_id}"
                                name = f"Xiaomi_{dev_id}"
                            except:
                                pass
                        
                        device = DiscoveredDevice(
                            ip=ip,
                            device_type=DeviceType.CAMERA_XIAOMI,
                            manufacturer=manufacturer,
                            model=model,
                            name=name,
                            protocol="miio"
                        )
                        self._notify_device_found(device)
                except socket.timeout:
                    break
                except Exception as e:
                    logger.debug(f"Erreur parsing Xiaomi: {e}")
                    
        except Exception as e:
            logger.error(f"Erreur scan Xiaomi: {e}")
        finally:
            s.close()
            
    def scan_avigilon(self, timeout: int = 10):
        """Scan Avigilon"""
        logger.info("Scan Avigilon démarré")
        
        def on_device(site, ip, model, mac, *args):
            # Valider que l'IP est correcte
            if not ip or not isinstance(ip, str) or ip.count('.') != 3:
                return
            
            # Extraire le nom s'il est présent dans les args
            name = ""
            if args and len(args) > 0:
                name = args[0]
                
            if self._is_new_device(ip, mac):
                device = DiscoveredDevice(
                    ip=ip,
                    device_type=DeviceType.CAMERA_AVIGILON,
                    manufacturer="Avigilon",
                    model=model,
                    name=name,
                    mac=mac,
                    protocol="avigilon"
                )
                self._notify_device_found(device)
        
        fake_comm = type('obj', (object,), {
            'addRow': type('obj', (object,), {
                'emit': lambda self, *args: on_device(*args)
            })()
        })()
        
        try:
            send.send("avigilon", fake_comm, None)
            time.sleep(timeout)
        except Exception as e:
            logger.error(f"Erreur scan Avigilon: {e}")

    def scan_snmp(self, timeout: int = 10, target_type: str = "all"):
        """Scan SNMP pour Serveurs et UPS"""
        logger.info(f"Scan SNMP ({target_type}) démarré")
        
        def on_device(site, ip, model, mac, name="", *args):
            # Valider que l'IP est correcte
            if not ip or not isinstance(ip, str) or ip.count('.') != 3:
                return
                
            # Détection du type basée sur le préfixe ajouté par fct.py
            device_type = DeviceType.SERVER # Par défaut
            real_model = model
            
            if model.startswith("[UPS] "):
                device_type = DeviceType.UPS
                real_model = model[6:]
                # Si on ne cherche que les serveurs, ignorer
                if target_type == "server": return
            elif model.startswith("[SERVER] "):
                device_type = DeviceType.SERVER
                real_model = model[9:]
                # Si on ne cherche que les UPS, ignorer
                if target_type == "ups": return
            elif model.startswith("[SWITCH] "):
                device_type = DeviceType.SWITCH
                real_model = model[9:]
                # Switch inclus dans scan "server" (infra) ou "all"
                if target_type == "ups": return
            else:
                # Type générique SNMP
                # Si on cherche spécifique, on ignore ou on prend?
                # On prend comme serveur par défaut
                if target_type == "ups": return
            
            
            if self._is_new_device(ip, mac):
                device = DiscoveredDevice(
                    ip=ip,
                    device_type=device_type,
                    manufacturer="SNMP Device", # Sera affiné plus tard si possible
                    model=real_model,
                    name=name,
                    mac=mac,
                    protocol="snmp"
                )
                self._notify_device_found(device)
        
        fake_comm = type('obj', (object,), {
            'addRow': type('obj', (object,), {
                'emit': lambda self, *args: on_device(*args)
            })()
        })()
        
        try:
            send.send("snmp", fake_comm, None)
            time.sleep(timeout)
        except Exception as e:
            logger.error(f"Erreur scan SNMP: {e}")

    def scan_ups(self, timeout: int = 10):
        """Scan spécifique pour onduleurs"""
        self.scan_snmp(timeout, target_type="ups")
    
    def scan_upnp(self, timeout: int = 10):
        """Scan UPnP/SSDP pour divers périphériques"""
        logger.info("Scan UPnP démarré")
        
        def on_device(site, ip, model, mac, *args):
            # Valider que l'IP est correcte  
            if not ip or not isinstance(ip, str) or ip.count('.') != 3:
                return
            if self._is_new_device(ip, mac):
                device = DiscoveredDevice(
                    ip=ip,
                    device_type=DeviceType.UPNP_DEVICE,
                    manufacturer=model,
                    protocol="upnp"
                )
                self._notify_device_found(device)
        
        fake_comm = type('obj', (object,), {
            'addRow': type('obj', (object,), {
                'emit': lambda self, *args: on_device(*args)
            })()
        })()
        
        try:
            send.send("upnp", fake_comm, None)
            time.sleep(timeout)
        except Exception as e:
            logger.error(f"Erreur scan UPnP: {e}")
    
    def scan_network(self, scan_types: List[str], timeout: int = 15) -> List[DiscoveredDevice]:
        """
        Lance un scan réseau complet
        
        Args:
            scan_types: Liste des types de scan à effectuer
                       ['hik', 'onvif', 'dahua', 'samsung', 'upnp']
            timeout: Timeout en secondes pour chaque scan
            
        Returns:
            Liste des périphériques découverts
        """
        logger.info(f"Démarrage scan réseau: {scan_types}")
        self._scan_running = True
        self.discovered_devices.clear()
        
        threads = []
        
        # Lancer les scans en parallèle
        if 'hik' in scan_types or 'hikvision' in scan_types:
            t = threading.Thread(target=self.scan_hikvision, args=(timeout,))
            t.start()
            threads.append(t)
        
        if 'onvif' in scan_types:
            t = threading.Thread(target=self.scan_onvif, args=(timeout,))
            t.start()
            threads.append(t)
        
        if 'dahua' in scan_types:
            t = threading.Thread(target=self.scan_dahua, args=(timeout,))
            t.start()
            threads.append(t)



        if 'xiaomi' in scan_types or 'camera_xiaomi' in scan_types:
            t = threading.Thread(target=self.scan_xiaomi, args=(timeout,))
            t.start()
            threads.append(t)

        if 'avigilon' in scan_types:
            t = threading.Thread(target=self.scan_avigilon, args=(timeout,))
            t.start()
            threads.append(t)
        
        if 'samsung' in scan_types:
            t = threading.Thread(target=self.scan_samsung, args=(timeout,))
            t.start()
            threads.append(t)
        
        if 'upnp' in scan_types:
            t = threading.Thread(target=self.scan_upnp, args=(timeout,))
            t.start()
            threads.append(t)
            
        if 'server' in scan_types or 'snmp' in scan_types:
            # Si on a aussi demandé 'ups', on fera un seul scan snmp "all"
            target = "server"
            if 'ups' in scan_types:
                 target = "all"
            
            # Éviter de lancer deux fois si 'ups' est traité ici
            if target == "all" or 'ups' not in scan_types:
                t = threading.Thread(target=self.scan_snmp, args=(timeout, target))
                t.start()
                threads.append(t)

        if 'ups' in scan_types and 'server' not in scan_types and 'snmp' not in scan_types:
            # Scan UPS seul
            t = threading.Thread(target=self.scan_ups, args=(timeout,))
            t.start()
            threads.append(t)
        
        # Attendre tous les threads
        for t in threads:
            t.join()
        
        self._scan_running = False
        logger.info(f"Scan terminé: {len(self.discovered_devices)} périphériques trouvés")
        
        return []  # Les résultats sont envoyés via callbacks
    
    def stop_scan(self):
        """Arrête le scan en cours"""
        self._scan_running = False
        logger.info("Arrêt du scan demandé")
