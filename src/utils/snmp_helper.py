"""
Module SNMP pour récupérer la température et les débits des équipements réseau.
Supporte les principaux constructeurs (Cisco, HP, Dell, Synology, QNAP, Raspberry Pi, etc.)
Compatible Python 3.12+ avec pysnmp 6.x
"""
import asyncio
import warnings

# Supprimer le warning de dépréciation de pysnmp
warnings.filterwarnings('ignore', message='.*pysnmp.*deprecated.*')

from src.utils.logger import get_logger
logger = get_logger(__name__)

# Tentative d'import de pysnmp
try:
    from pysnmp.hlapi.asyncio import *
    SNMP_AVAILABLE = True
    logger.info("✅ Module SNMP chargé avec succès (pysnmp 6.x)")
except ImportError as e:
    SNMP_AVAILABLE = False
    logger.warning(f"⚠️ Module SNMP non disponible: {e}")
    logger.warning("Les fonctionnalités de surveillance de température ne seront pas disponibles")
    logger.info("Pour activer SNMP, installez: pip install pysnmp>=6.0")

# OIDs standards pour la température selon les constructeurs
TEMPERATURE_OIDS = {
    
    # Raspberry Pi (priorité haute pour Linux embarqué)
    'raspberry_pi_host_resources': '1.3.6.1.2.1.25.1.8',  # HOST-RESOURCES-MIB (sans .0)
    'raspberry_pi_cpu': '1.3.6.1.4.1.2021.13.16.2.1.3.1',  # CPU thermal via lm-sensors
    'raspberry_pi_thermal': '1.3.6.1.4.1.2021.13.16.2.1.3.2',  # Thermal zone
    'raspberry_pi_soc': '1.3.6.1.4.1.2021.13.16.2.1.3.3',  # SoC temp
    
    # NAS (priorité haute - testé en premier)
    'synology_cpu': '1.3.6.1.4.1.6574.1.2.0',  # Synology CPU temp
    'synology_system': '1.3.6.1.4.1.6574.1.5.0',  # Synology system temp
    'qnap_cpu': '1.3.6.1.4.1.24681.1.2.5.0',  # QNAP CPU temp
    'qnap_system': '1.3.6.1.4.1.24681.1.2.6.0',  # QNAP system temp
    # Switches standards (ordre de test)
    'cisco_cpu': '1.3.6.1.4.1.9.9.13.1.3.1.3.1',  # Cisco CPU temp
    'cisco_env': '1.3.6.1.4.1.9.9.91.1.1.1.1.4.1',  # Cisco Environmental
    'cisco_temp_sensor': '1.3.6.1.4.1.9.9.13.1.3.1.3.1',  # Cisco temp sensor
    'hp_switches': '1.3.6.1.4.1.11.2.14.11.1.2.6.1.4.7.1',  # HP/Aruba switches
    'hp_procurve': '1.3.6.1.4.1.11.2.14.11.5.1.9.6.1.0',  # HP ProCurve
    'dell_switches': '1.3.6.1.4.1.674.10895.3000.1.2.110.7.1.1.1.4',  # Dell PowerConnect
    'dell_nxx': '1.3.6.1.4.1.674.10895.5000.2.6132.1.1.43.1.8.1.5.1',  # Dell N-Series
    'netgear': '1.3.6.1.4.1.4526.22.3.1.3.1',  # Netgear managed
    'netgear_temp': '1.3.6.1.4.1.4526.10.1.1.1.13.0',  # Netgear alternative
    'ubiquiti': '1.3.6.1.4.1.41112.1.6.1.2.1.3.1',  # Ubiquiti EdgeSwitch
    'ubiquiti_temp': '1.3.6.1.4.1.41112.1.6.3.1.0',  # Ubiquiti alternative
    'mikrotik': '1.3.6.1.4.1.14988.1.1.3.10.0',  # MikroTik temperature
    'mikrotik_cpu': '1.3.6.1.4.1.14988.1.1.3.11.0',  # MikroTik CPU temp
    'dlink': '1.3.6.1.4.1.171.12.11.1.8.1.2.1',  # D-Link switches
    'tplink': '1.3.6.1.4.1.11863.6.1.1.3.0',  # TP-Link managed
    'zyxel': '1.3.6.1.4.1.890.1.15.3.1.10.1.3.1',  # Zyxel switches
    
    # Serveurs
    'dell_server': '1.3.6.1.4.1.674.10892.1.700.20.1.6.1.1',  # Dell iDRAC
    'dell_idrac_inlet': '1.3.6.1.4.1.674.10892.5.4.700.20.1.6.1.1',  # Dell iDRAC inlet
    'hp_server': '1.3.6.1.4.1.232.6.2.6.8.1.4.1',  # HP iLO
    'hp_ilo_ambient': '1.3.6.1.4.1.232.6.2.6.8.1.4.1.2',  # HP iLO ambient
    'supermicro': '1.3.6.1.4.1.10876.2.1.1.1.1.4.1',  # Supermicro IPMI
    
    # Linux générique (lm-sensors via Net-SNMP)
    'lm_sensors_1': '1.3.6.1.4.1.2021.13.16.2.1.3.1',  # UCD-SNMP-MIB index 1
    'lm_sensors_2': '1.3.6.1.4.1.2021.13.16.2.1.3.2',  # index 2
    'lm_sensors_3': '1.3.6.1.4.1.2021.13.16.2.1.3.3',  # index 3
    'lm_sensors_4': '1.3.6.1.4.1.2021.13.16.2.1.3.4',  # index 4
    'lm_sensors_5': '1.3.6.1.4.1.2021.13.16.2.1.3.5',  # index 5
    'lm_sensors_6': '1.3.6.1.4.1.2021.13.16.2.1.3.6',  # index 6
    
    # Windows (SNMP Informant ou HOST-RESOURCES-MIB)
    'windows_cpu': '1.3.6.1.2.1.25.1.8.0',  # HOST-RESOURCES-MIB
    
    # Standards génériques (testés en dernier)
    'entity_sensor_1': '1.3.6.1.2.1.99.1.1.1.4.1',  # Entity Sensor MIB index 1
    'entity_sensor_2': '1.3.6.1.2.1.99.1.1.1.4.2',  # index 2
    'entity_sensor_3': '1.3.6.1.2.1.99.1.1.1.4.3',  # index 3
    'lm78': '1.3.6.1.4.1.2021.13.16.2.1.3.10',  # LM78/LM87
}

class SNMPHelper:
    def __init__(self, community='public', timeout=0.8, retries=0):
        """
        Initialise le helper SNMP.
        
        Args:
            community: Communauté SNMP (par défaut 'public')
            timeout: Timeout en secondes (0.8s - optimisé pour fiabilité)
            retries: Nombre de tentatives (0 = 1 seule tentative)
        """
        self.community = community
        self.timeout = timeout
        self.retries = retries
        # Cache des IPs qui ne supportent pas SNMP (pour éviter de réessayer)
        self._no_snmp_cache = set()
        # Cache des IPs qui supportent SNMP (pour optimiser)
        self._has_snmp_cache = set()
        # Cache des OIDs qui fonctionnent pour chaque IP (optimisation)
        self._working_oids = {}  # {ip: {'temp': oid, 'traffic': True/False}}
        # Cache des meilleures interfaces pour les débits par IP
        self._best_interfaces = {}  # {ip: interface_index}
        
        # Log d'initialisation
        if SNMP_AVAILABLE:
            logger.info(f"SNMPHelper initialisé : communauté='{community}', timeout={timeout}s, {len(TEMPERATURE_OIDS)} types d'équipements supportés")
        else:
            logger.warning("SNMPHelper initialisé SANS support SNMP (module non chargé)")

    async def get_device_type(self, ip):
        """
        Détecte le type d'équipement via OIDs spécifiques et sysDescr.
        
        Args:
            ip: Adresse IP de l'équipement
            
        Returns:
            str: Type d'équipement ('synology', 'raspberry', 'cisco', 'hp', etc.) ou 'unknown'
        """
        if not SNMP_AVAILABLE:
            return 'unknown'
        
        # Vérifier le cache
        if ip in self._working_oids and 'device_type' in self._working_oids[ip]:
            return self._working_oids[ip]['device_type']
        
        device_type = 'unknown'
        sys_descr = ''
        
        try:
            # Méthode 1 : Tester des OIDs spécifiques par constructeur (plus fiable)
            
            # Test Synology : OID du modèle (1.3.6.1.4.1.6574.1.5.1.0)
            synology_model = await self._query_oid(ip, '1.3.6.1.4.1.6574.1.5.1.0', return_type='string')
            if synology_model and synology_model != 'No Such Instance':
                device_type = 'synology'
                logger.info(f"📋 Type d'équipement détecté pour {ip}: synology (via OID modèle: {synology_model})")
                if ip not in self._working_oids:
                    self._working_oids[ip] = {}
                self._working_oids[ip]['device_type'] = device_type
                return device_type
            
            # Test QNAP : OID du modèle (1.3.6.1.4.1.24681.1.2.12.0)
            qnap_model = await self._query_oid(ip, '1.3.6.1.4.1.24681.1.2.12.0', return_type='string')
            if qnap_model and qnap_model != 'No Such Instance':
                device_type = 'qnap'
                logger.info(f"📋 Type d'équipement détecté pour {ip}: qnap (via OID modèle)")
                if ip not in self._working_oids:
                    self._working_oids[ip] = {}
                self._working_oids[ip]['device_type'] = device_type
                return device_type
            
            # Méthode 2 : Utiliser sysDescr (fallback)
            sys_descr = await self._query_oid(ip, '1.3.6.1.2.1.1.1.0', return_type='string')
            
            if sys_descr:
                sys_descr_lower = sys_descr.lower()
                
                # Détection par mots-clés dans sysDescr (ordre important!)
                if 'synology' in sys_descr_lower or 'diskstation' in sys_descr_lower:
                    device_type = 'synology'
                elif 'qnap' in sys_descr_lower:
                    device_type = 'qnap'
                elif 'cisco' in sys_descr_lower:
                    device_type = 'cisco'
                elif 'hp' in sys_descr_lower or 'hewlett' in sys_descr_lower or 'procurve' in sys_descr_lower:
                    device_type = 'hp'
                elif 'dell' in sys_descr_lower:
                    device_type = 'dell'
                elif 'ubiquiti' in sys_descr_lower or 'unifi' in sys_descr_lower or 'edgeswitch' in sys_descr_lower:
                    device_type = 'ubiquiti'
                elif 'mikrotik' in sys_descr_lower or 'routeros' in sys_descr_lower:
                    device_type = 'mikrotik'
                elif 'raspberry' in sys_descr_lower or 'raspbian' in sys_descr_lower:
                    device_type = 'raspberry'
                elif 'linux' in sys_descr_lower:
                    # Linux générique = probablement Raspberry Pi ou serveur Linux
                    device_type = 'raspberry'
                else:
                    device_type = 'unknown'
                
                logger.info(f"📋 Type d'équipement détecté pour {ip}: {device_type} (via sysDescr: {sys_descr[:60]}...)")
                
                # Mettre en cache
                if ip not in self._working_oids:
                    self._working_oids[ip] = {}
                self._working_oids[ip]['device_type'] = device_type
                
                return device_type
        except Exception as e:
            logger.debug(f"Erreur détection type pour {ip}: {e}")
        
        # Si aucune détection, retourner unknown
        if device_type == 'unknown':
            logger.info(f"📋 Type d'équipement pour {ip}: unknown (testera tous les OIDs)")
        
        return device_type
    
    async def is_snmp_enabled(self, ip):
        """
        Teste si SNMP est activé sur un équipement (test rapide avec sysUpTime).
        Équivalent à : snmpget -v2c -c public IP 1.3.6.1.2.1.1.3.0
        
        Args:
            ip: Adresse IP de l'équipement
            
        Returns:
            bool: True si SNMP est activé, False sinon
        """
        if not SNMP_AVAILABLE:
            return False
        
        # Vérifier le cache d'abord
        if ip in self._has_snmp_cache:
            return True
        if ip in self._no_snmp_cache:
            return False
        
        try:
            # Test rapide avec sysUpTime (OID standard supporté par tous)
            uptime = await self._query_oid(ip, '1.3.6.1.2.1.1.3.0', return_type='numeric')
            
            if uptime is not None:
                self._has_snmp_cache.add(ip)
                self._no_snmp_cache.discard(ip)
                # logger.info(f"✅ SNMP activé pour {ip} (uptime: {int(uptime/100/60)} minutes)")
                return True
            else:
                self._no_snmp_cache.add(ip)
                self._has_snmp_cache.discard(ip)
                return False
        except Exception as e:
            self._no_snmp_cache.add(ip)
            return False
    
    async def get_temperature(self, ip, oid=None):
        """
        Récupère la température d'un équipement via SNMP.
        
        Args:
            ip: Adresse IP de l'équipement
            oid: OID spécifique (optionnel, sinon essaie les OIDs standards)
            
        Returns:
            float: Température en °C, ou None si échec
        """
        if not SNMP_AVAILABLE:
            return None
        
        # Test préalable : SNMP est-il activé ? (test rapide)
        snmp_enabled = await self.is_snmp_enabled(ip)
        if not snmp_enabled:
            return None
        
        try:
            # Timeout global augmenté pour la fiabilité
            result = await asyncio.wait_for(
                self._get_temperature_internal(ip, oid),
                timeout=2.0
            )
            
            # Si on a trouvé une température, marquer comme supportant SNMP
            if result is not None:
                self._has_snmp_cache.add(ip)
                # Retirer du cache no_snmp si présent
                self._no_snmp_cache.discard(ip)
            else:
                # Aucune température trouvée après toutes les tentatives
                # NE PAS mettre en cache immédiatement pour retenter au prochain cycle
                logger.debug(f"Aucune température trouvée pour {ip} (sera retesté)")
            
            return result
        except asyncio.TimeoutError:
            # NE PAS mettre en cache immédiatement (peut être temporaire)
            return None
    
    async def _get_temperature_internal(self, ip, oid=None):
        """Méthode interne pour récupérer la température."""
        # Si un OID spécifique est fourni, on l'utilise
        if oid:
            temp = await self._query_oid(ip, oid, return_type='numeric')
            return temp if isinstance(temp, (int, float)) else None
        
        # Si on a déjà un OID qui fonctionne pour cette IP, l'utiliser en priorité
        if ip in self._working_oids and 'temp' in self._working_oids[ip]:
            working_oid = self._working_oids[ip]['temp']
            temp = await self._query_oid(ip, working_oid, return_type='numeric')
            if temp is not None and isinstance(temp, (int, float)):
                return temp
            else:
                # L'OID ne fonctionne plus, le retirer du cache
                del self._working_oids[ip]['temp']
        
        # Détecter le type d'équipement pour filtrer les OIDs
        device_type = await self.get_device_type(ip)
        
        # Filtrer les OIDs selon le type d'équipement
        oids_to_test = self._filter_oids_by_device_type(device_type)
        
        logger.debug(f"Test de {len(oids_to_test)} OIDs pour {ip} (type: {device_type})")
        
        # Tester les OIDs filtrés
        for name, oid_value in oids_to_test.items():
            try:
                temp = await self._query_oid(ip, oid_value, return_type='numeric')
                if temp is not None and isinstance(temp, (int, float)):
                    logger.info(f"✅ Température trouvée pour {ip} via OID '{name}': {temp}°C")
                    # Sauvegarder l'OID qui fonctionne pour cette IP
                    if ip not in self._working_oids:
                        self._working_oids[ip] = {}
                    self._working_oids[ip]['temp'] = oid_value
                    return temp
            except Exception as e:
                logger.debug(f"Échec OID {name} pour {ip}: {e}")
                continue
        
        logger.info(f"❌ Aucune température trouvée pour {ip} (testé {len(oids_to_test)} OIDs, type: {device_type})")
        return None
    
    def _filter_oids_by_device_type(self, device_type):
        """
        Filtre les OIDs à tester selon le type d'équipement détecté.
        
        Args:
            device_type: Type d'équipement ('synology', 'raspberry', etc.)
            
        Returns:
            dict: OIDs filtrés à tester en priorité
        """
        # Mapping des OIDs par type d'équipement
        device_specific_oids = {
            'synology': ['synology_cpu', 'synology_system'],
            'qnap': ['qnap_cpu', 'qnap_system'],
            'raspberry': ['raspberry_pi_host_resources', 'raspberry_pi_lm_sensors', 'raspberry_pi_soc'],
            'cisco': ['cisco_cpu', 'cisco_env'],
            'hp': ['hp_icf_sensor', 'hp_rack'],
            'dell': ['dell_thermal'],
            'ubiquiti': ['ubiquiti_temp'],
            'mikrotik': ['mikrotik_temp']
        }
        
        # Si type détecté, tester d'abord les OIDs spécifiques
        if device_type in device_specific_oids:
            specific_oid_names = device_specific_oids[device_type]
            filtered_oids = {}
            
            # Ajouter d'abord les OIDs spécifiques
            for oid_name in specific_oid_names:
                if oid_name in TEMPERATURE_OIDS:
                    filtered_oids[oid_name] = TEMPERATURE_OIDS[oid_name]
            
            # Ajouter ensuite les OIDs génériques (en fin de liste)
            generic_oids = ['ucd_lm_sensors', 'net_snmp_temperature', 'host_resources_temp']
            for oid_name in generic_oids:
                if oid_name in TEMPERATURE_OIDS and oid_name not in filtered_oids:
                    filtered_oids[oid_name] = TEMPERATURE_OIDS[oid_name]
            
            return filtered_oids
        
        # Si type inconnu, tester tous les OIDs (comportement par défaut)
        return TEMPERATURE_OIDS
    
    def supports_network_traffic(self, device_type):
        """
        Détermine si un type d'équipement supporte probablement les débits réseau.
        
        Args:
            device_type: Type d'équipement
            
        Returns:
            bool: True si l'équipement supporte probablement les débits
        """
        # Types d'équipements qui supportent généralement les débits réseau
        network_devices = {
            'synology',    # NAS avec interfaces réseau
            'qnap',        # NAS avec interfaces réseau
            'cisco',       # Switchs/routeurs
            'hp',          # Switchs HP
            'dell',        # Switchs Dell
            'ubiquiti',    # Switchs Ubiquiti
            'mikrotik',    # Routeurs MikroTik
            'netgear',     # Switchs Netgear
            'dlink',       # Switchs D-Link
            'tplink',      # Switchs TP-Link
            'zyxel',       # Switchs Zyxel
        }
        
        return device_type in network_devices or device_type == 'unknown'
    
    def is_potential_ups(self, device_type):
        """
        Détermine si un type d'équipement peut être un onduleur.
        
        Args:
            device_type: Type d'équipement
            
        Returns:
            bool: True si l'équipement peut être un UPS
        """
        # Types d'équipements qui peuvent avoir un UPS
        ups_candidates = {
            'synology',    # NAS souvent connectés à un UPS
            'qnap',        # NAS souvent connectés à un UPS
            'dell',        # Serveurs Dell avec UPS
            'hp',          # Serveurs HP avec UPS
            'apc',         # APC = fabricant d'UPS
            'eaton',       # Eaton = fabricant d'UPS
            'unknown',     # Tester si type inconnu
        }
        
        return device_type in ups_candidates

    async def _query_oid(self, ip, oid, return_type='numeric'):
        """
        Interroge un OID SNMP spécifique avec pysnmp 6.x (asyncio).
        
        Args:
            ip: Adresse IP
            oid: OID à interroger
            return_type: Type de retour attendu ('numeric', 'string', 'auto')
            
        Returns:
            float/str/None: Valeur selon le type, ou None si échec
        """
        if not SNMP_AVAILABLE:
            return None
        
        snmp_engine = None
        try:
            snmp_engine = SnmpEngine()
            
            iterator = await getCmd(
                snmp_engine,
                CommunityData(self.community),
                UdpTransportTarget((ip, 161), timeout=self.timeout, retries=self.retries),
                ContextData(),
                ObjectType(ObjectIdentity(oid))
            )
            
            errorIndication, errorStatus, errorIndex, varBinds = iterator
            
            if errorIndication:
                return None
            elif errorStatus:
                return None
            else:
                # Récupération de la valeur
                for varBind in varBinds:
                    value = varBind[1]
                    
                    # Si type string demandé, retourner tel quel
                    if return_type == 'string':
                        return str(value)
                    
                    # Sinon essayer de convertir en nombre (mode numeric ou auto)
                    try:
                        numeric_value = float(value)
                        # Conversion selon la plage de valeur (température en °C)
                        if numeric_value > 10000:
                            # Probablement en millièmes de degrés (ex: 71600 = 71.6°C)
                            numeric_value = numeric_value / 1000.0
                        elif numeric_value > 1000:
                            # Probablement en centièmes de degrés (ex: 7215 = 72.15°C)
                            numeric_value = numeric_value / 100.0
                        elif numeric_value > 200:
                            # Probablement en dixièmes de degrés (ex: 450 = 45.0°C)
                            numeric_value = numeric_value / 10.0
                        # Si < 200, c'est déjà en degrés Celsius (plage normale: -40°C à 150°C)
                        return numeric_value
                    except (ValueError, TypeError):
                        # Si conversion échoue et mode auto, retourner en string
                        if return_type == 'auto':
                            return str(value)
                        # En mode numeric, retourner None si pas convertible
                        return None
        except Exception as e:
            return None
        finally:
            # Fermeture propre du SnmpEngine pour éviter les fuites de ressources et erreurs "Unregistered transport"
            if snmp_engine is not None:
                try:
                    # Fermer le dispatcher
                    if snmp_engine.transportDispatcher:
                        snmp_engine.transportDispatcher.closeDispatcher()
                        # Désenregistrer explicitement le transport si possible
                        # Cela évite que des callbacks soient appelés après la fermeture de la boucle
                        try:
                            # Tenter de désenregistrer tous les transports connus
                            for transport_domain in list(snmp_engine.transportDispatcher.transports.keys()):
                                snmp_engine.transportDispatcher.unregisterTransport(transport_domain)
                        except:
                            pass
                except Exception:
                    pass

    async def find_best_interface(self, ip):
        """
        Trouve automatiquement la meilleure interface réseau pour un équipement.
        Teste plusieurs interfaces et retourne celle avec des compteurs > 0.
        
        Args:
            ip: Adresse IP de l'équipement
            
        Returns:
            int: Index de la meilleure interface, ou 1 par défaut
        """
        # Si on a déjà trouvé la meilleure interface, la réutiliser
        if ip in self._best_interfaces:
            return self._best_interfaces[ip]
        
        # Liste des interfaces à tester (ordre de priorité)
        interfaces_to_test = [
            1,    # Interface principale par défaut
            2,    # Premier port physique
            10,   # Interface agrégée commune
            100,  # VLAN/Interface virtuelle
            1000, # Interface de gestion
        ]
        
        logger.debug(f"🔍 Recherche de la meilleure interface pour {ip}...")
        
        for idx in interfaces_to_test:
            try:
                # Tester l'interface
                data = await self.get_interface_traffic_raw(ip, idx)
                
                if data and (data['in'] > 1000 or data['out'] > 1000):
                    # Cette interface a des compteurs significatifs
                    logger.info(f"   ✅ Interface {idx} trouvée (IN:{data['in']:,}, OUT:{data['out']:,})")
                    self._best_interfaces[ip] = idx
                    return idx
                elif data:
                    logger.debug(f"   Interface {idx} trouvée mais trafic très faible")
            except Exception as e:
                logger.debug(f"   Interface {idx} non accessible: {e}")
                continue
        
        # Aucune interface trouvée, utiliser 1 par défaut
        logger.warning(f"   ⚠️  Aucune interface avec trafic trouvée pour {ip}, utilisation interface 1")
        self._best_interfaces[ip] = 1
        return 1
    
    async def get_interface_traffic_raw(self, ip, interface_index):
        """
        Version brute de get_interface_traffic sans filtrage ni logs verbeux.
        Utilisée pour la détection d'interface.
        """
        if not SNMP_AVAILABLE:
            return None
        
        try:
            import time
            oid_in_hc = f'1.3.6.1.2.1.31.1.1.1.6.{interface_index}'
            oid_out_hc = f'1.3.6.1.2.1.31.1.1.1.10.{interface_index}'
            
            octets_in = await self._query_oid(ip, oid_in_hc)
            octets_out = await self._query_oid(ip, oid_out_hc)
            
            if octets_in is None or octets_out is None:
                oid_in = f'1.3.6.1.2.1.2.2.1.10.{interface_index}'
                oid_out = f'1.3.6.1.2.1.2.2.1.16.{interface_index}'
                octets_in = await self._query_oid(ip, oid_in)
                octets_out = await self._query_oid(ip, oid_out)
            
            if octets_in is not None and octets_out is not None:
                return {
                    'in': int(octets_in),
                    'out': int(octets_out),
                    'timestamp': time.time()
                }
        except Exception:
            pass
        
        return None
    
    async def get_interface_traffic(self, ip, interface_index=None):
        """
        Récupère les compteurs de trafic IN/OUT d'une interface réseau via SNMP.
        
        Args:
            ip: Adresse IP de l'équipement
            interface_index: Index de l'interface (1 par défaut pour l'interface principale)
            
        Returns:
            dict: {'in': octets_in, 'out': octets_out, 'timestamp': time.time()}
                  ou None si échec
        """
        if not SNMP_AVAILABLE:
            return None
        
        # Test préalable : SNMP est-il activé ?
        snmp_enabled = await self.is_snmp_enabled(ip)
        if not snmp_enabled:
            return None
        
        # Filtrage : Vérifier si ce type d'équipement supporte les débits
        device_type = await self.get_device_type(ip)
        if not self.supports_network_traffic(device_type):
            logger.debug(f"Type d'équipement {device_type} ne supporte probablement pas les débits réseau, skip pour {ip}")
            return None
        
        # Détection automatique de l'interface si non spécifiée
        if interface_index is None:
            interface_index = await self.find_best_interface(ip)
            logger.info(f"Interface {interface_index} utilisée pour {ip}")
        
        try:
            import time
            # OIDs pour les compteurs 64 bits (High Capacity)
            oid_in_hc = f'1.3.6.1.2.1.31.1.1.1.6.{interface_index}'  # ifHCInOctets
            oid_out_hc = f'1.3.6.1.2.1.31.1.1.1.10.{interface_index}'  # ifHCOutOctets
            
            # Essayer d'abord les OIDs 64 bits (supportés par les équipements modernes)
            octets_in = await self._query_oid(ip, oid_in_hc)
            octets_out = await self._query_oid(ip, oid_out_hc)
            
            # Si échec, essayer les OIDs 32 bits standards
            if octets_in is None or octets_out is None:
                oid_in = f'1.3.6.1.2.1.2.2.1.10.{interface_index}'  # ifInOctets
                oid_out = f'1.3.6.1.2.1.2.2.1.16.{interface_index}'  # ifOutOctets
                octets_in = await self._query_oid(ip, oid_in)
                octets_out = await self._query_oid(ip, oid_out)
            
            if octets_in is not None and octets_out is not None:
                result = {
                    'in': int(octets_in),
                    'out': int(octets_out),
                    'timestamp': time.time()
                }
                self._has_snmp_cache.add(ip)
                # logger.debug(f"📡 Compteurs SNMP récupérés pour {ip}: IN={int(octets_in):,}, OUT={int(octets_out):,} octets")
                return result
            else:
                return None
                
        except Exception as e:
            return None
    
    async def get_interface_speed_direct(self, ip, interface_index=1):
        """
        Récupère la vitesse de l'interface et les compteurs de trafic en MB/s (sans calcul de delta).
        Affiche directement ce que l'équipement remonte.
        
        Args:
            ip: Adresse IP de l'équipement
            interface_index: Index de l'interface (1 par défaut)
            
        Returns:
            dict: {
                'speed_mbps': float,           # Vitesse max de l'interface en Mb/s
                'total_in_mb': float,          # Total reçu en MB (mégaoctets)
                'total_out_mb': float,         # Total envoyé en MB (mégaoctets)
                'in_octets': int,              # Compteur brut IN en octets
                'out_octets': int              # Compteur brut OUT en octets
            } ou None
        """
        if not SNMP_AVAILABLE:
            return None
        
        try:
            # 1. Récupérer la vitesse de l'interface
            # ifHighSpeed (1.3.6.1.2.1.31.1.1.1.15) en Mb/s (megabits par seconde)
            oid_speed = f'1.3.6.1.2.1.31.1.1.1.15.{interface_index}'
            speed_mbps = await self._query_oid(ip, oid_speed, return_type='numeric')
            
            # Si ifHighSpeed non disponible, essayer ifSpeed (en bits/s)
            if speed_mbps is None or speed_mbps == 0:
                oid_speed_bps = f'1.3.6.1.2.1.2.2.1.5.{interface_index}'
                speed_bps = await self._query_oid(ip, oid_speed_bps, return_type='numeric')
                if speed_bps:
                    speed_mbps = float(speed_bps) / 1000000  # Convertir en Mb/s
            
            # 2. Récupérer les compteurs de trafic
            # ifHCInOctets / ifHCOutOctets (64 bits)
            oid_in_hc = f'1.3.6.1.2.1.31.1.1.1.6.{interface_index}'
            oid_out_hc = f'1.3.6.1.2.1.31.1.1.1.10.{interface_index}'
            
            octets_in = await self._query_oid(ip, oid_in_hc, return_type='numeric')
            octets_out = await self._query_oid(ip, oid_out_hc, return_type='numeric')
            
            # Si échec, essayer les OIDs 32 bits
            if octets_in is None or octets_out is None:
                oid_in = f'1.3.6.1.2.1.2.2.1.10.{interface_index}'
                oid_out = f'1.3.6.1.2.1.2.2.1.16.{interface_index}'
                octets_in = await self._query_oid(ip, oid_in, return_type='numeric')
                octets_out = await self._query_oid(ip, oid_out, return_type='numeric')
            
            if octets_in is not None and octets_out is not None:
                # Convertir en MB (mégaoctets)
                total_in_mb = float(octets_in) / (1024 * 1024)
                total_out_mb = float(octets_out) / (1024 * 1024)
                
                result = {
                    'speed_mbps': speed_mbps if speed_mbps else 0.0,
                    'total_in_mb': total_in_mb,
                    'total_out_mb': total_out_mb,
                    'in_octets': int(octets_in),
                    'out_octets': int(octets_out)
                }
                
                logger.info(f"📊 Compteurs directs pour {ip}:")
                logger.info(f"   Vitesse interface: {speed_mbps} Mb/s")
                logger.info(f"   Total IN: {total_in_mb:.2f} MB ({octets_in:,} octets)")
                logger.info(f"   Total OUT: {total_out_mb:.2f} MB ({octets_out:,} octets)")
                
                return result
            
            return None
            
        except Exception as e:
            logger.debug(f"Erreur récupération compteurs directs pour {ip}: {e}")
            return None
    
    async def calculate_bandwidth(self, ip, interface_index=1, previous_data=None):
        """
        Récupère le trafic actuel et calcule la bande passante (débit) en Mbps.
        
        Args:
            ip: Adresse IP de l'équipement
            interface_index: Index de l'interface (1 par défaut)
            previous_data: Données précédentes (dict avec 'in', 'out', 'timestamp')
            
        Returns:
            dict: {'in_mbps': float, 'out_mbps': float, 'raw_data': current_data}
                  ou None si échec
        """
        # Récupérer les données actuelles
        current_data = await self.get_interface_traffic(ip, interface_index)
        
        if current_data is None:
            return None
        
        # Si pas de données précédentes, retourner les données brutes seulement
        if previous_data is None:
            return {
                'in_mbps': 0.0,
                'out_mbps': 0.0,
                'raw_data': current_data
            }
        
        # Calculer le delta de temps (en secondes)
        time_delta = current_data['timestamp'] - previous_data['timestamp']
        
        if time_delta <= 0:
            return {
                'in_mbps': 0.0,
                'out_mbps': 0.0,
                'raw_data': current_data
            }
        
        # Calculer le delta d'octets
        octets_in_delta = current_data['in'] - previous_data['in']
        octets_out_delta = current_data['out'] - previous_data['out']
        
        # Log détaillé pour debug
        logger.info(f"📊 Calcul débit pour {ip}:")
        logger.info(f"   Temps delta: {time_delta:.1f}s")
        logger.info(f"   IN  - Avant: {previous_data['in']:,} | Après: {current_data['in']:,} | Delta: {octets_in_delta:,} octets")
        logger.info(f"   OUT - Avant: {previous_data['out']:,} | Après: {current_data['out']:,} | Delta: {octets_out_delta:,} octets")
        
        # Gérer le wraparound (compteur qui déborde)
        if octets_in_delta < 0:
            logger.warning(f"⚠️  Wraparound détecté pour {ip} (IN), reset à 0")
            octets_in_delta = 0
        if octets_out_delta < 0:
            logger.warning(f"⚠️  Wraparound détecté pour {ip} (OUT), reset à 0")
            octets_out_delta = 0
        
        # Convertir en Mbps (octets/sec -> bits/sec -> Mbits/sec)
        in_mbps = (octets_in_delta * 8) / (time_delta * 1_000_000)
        out_mbps = (octets_out_delta * 8) / (time_delta * 1_000_000)
        
        logger.info(f"   ✅ Débit calculé: IN={in_mbps:.6f} Mbps, OUT={out_mbps:.6f} Mbps")
        
        # Utiliser 6 décimales pour capturer même les très petits débits (quelques bps)
        return {
            'in_mbps': round(in_mbps, 6),
            'out_mbps': round(out_mbps, 6),
            'raw_data': current_data
        }
    
    def calculate_bandwidth_sync(self, current_data, previous_data):
        """
        Version synchrone : Calcule la bande passante (débit) en Mbps entre deux mesures.
        Utilisée par le serveur web qui a déjà les données brutes.
        
        Args:
            current_data: Données actuelles (dict avec 'in', 'out', 'timestamp')
            previous_data: Données précédentes (dict avec 'in', 'out', 'timestamp')
            
        Returns:
            dict: {'in_mbps': float, 'out_mbps': float}
                  ou None si pas assez de données
        """
        if current_data is None or previous_data is None:
            return None
        
        # Calculer le delta de temps (en secondes)
        time_delta = current_data['timestamp'] - previous_data['timestamp']
        
        if time_delta <= 0:
            return None
        
        # Calculer le delta d'octets
        octets_in_delta = current_data['in'] - previous_data['in']
        octets_out_delta = current_data['out'] - previous_data['out']
        
        # Gérer le wraparound (compteur qui déborde)
        if octets_in_delta < 0:
            octets_in_delta = 0
        if octets_out_delta < 0:
            octets_out_delta = 0
        
        # Convertir en Mbps (octets/sec -> bits/sec -> Mbits/sec)
        in_mbps = (octets_in_delta * 8) / (time_delta * 1_000_000)
        out_mbps = (octets_out_delta * 8) / (time_delta * 1_000_000)
        
        # Utiliser 6 décimales pour capturer même les très petits débits (quelques bps)
        # Le formatage automatique s'occupera d'afficher l'unité appropriée
        return {
            'in_mbps': round(in_mbps, 6),
            'out_mbps': round(out_mbps, 6)
        }
    
    def clear_cache(self, ip=None):
        """
        Vide le cache SNMP pour une IP spécifique ou tout le cache.
        Utile pour forcer une nouvelle détection.
        
        Args:
            ip: IP spécifique à retirer du cache, ou None pour tout vider
        """
        if ip:
            self._no_snmp_cache.discard(ip)
            self._has_snmp_cache.discard(ip)
            if ip in self._working_oids:
                del self._working_oids[ip]
            logger.info(f"Cache SNMP vidé pour {ip}")
        else:
            self._no_snmp_cache.clear()
            self._has_snmp_cache.clear()
            self._working_oids.clear()
            logger.info("Cache SNMP entièrement vidé")
    
    def get_cache_stats(self):
        """Retourne des statistiques sur le cache SNMP (utile pour le debug)"""
        return {
            'no_snmp': len(self._no_snmp_cache),
            'has_snmp': len(self._has_snmp_cache),
            'working_oids': len(self._working_oids),
            'oids_per_ip': {ip: list(oids.keys()) for ip, oids in self._working_oids.items()}
        }

# Instance globale (peut être configurée depuis les paramètres)
snmp_helper = SNMPHelper()
