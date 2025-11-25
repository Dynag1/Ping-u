"""
Module SNMP pour récupérer la température des équipements réseau.
Supporte les principaux constructeurs (Cisco, HP, Dell, Synology, QNAP, etc.)
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
    # NAS
    'synology_cpu': '1.3.6.1.4.1.6574.1.2.0',  # Synology CPU temp
    'synology_system': '1.3.6.1.4.1.6574.1.5.0',  # Synology system temp
    'qnap_cpu': '1.3.6.1.4.1.24681.1.2.5.0',  # QNAP CPU temp
    'qnap_system': '1.3.6.1.4.1.24681.1.2.6.0',  # QNAP system temp
    
    # Switches
    'cisco_cpu': '1.3.6.1.4.1.9.9.13.1.3.1.3.1',  # Cisco CPU temp
    'cisco_env': '1.3.6.1.4.1.9.9.91.1.1.1.1.4.1',  # Cisco Environmental
    'hp_switches': '1.3.6.1.4.1.11.2.14.11.1.2.6.1.4.7.1',  # HP/Aruba switches
    'dell_switches': '1.3.6.1.4.1.674.10895.3000.1.2.110.7.1.1.1.4',  # Dell PowerConnect
    'netgear': '1.3.6.1.4.1.4526.22.3.1.3.1',  # Netgear
    'ubiquiti': '1.3.6.1.4.1.41112.1.6.1.2.1.3.1',  # Ubiquiti EdgeSwitch
    'mikrotik': '1.3.6.1.4.1.14988.1.1.3.10.0',  # MikroTik
    
    # Serveurs
    'dell_server': '1.3.6.1.4.1.674.10892.1.700.20.1.6.1.1',  # Dell iDRAC
    'hp_server': '1.3.6.1.4.1.232.6.2.6.8.1.4.1',  # HP iLO
    'supermicro': '1.3.6.1.4.1.10876.2.1.1.1.1.4.1',  # Supermicro IPMI
    
    # Linux (lm-sensors via Net-SNMP)
    'lm_sensors_1': '1.3.6.1.4.1.2021.13.16.2.1.3.1',  # UCD-SNMP-MIB
    'lm_sensors_2': '1.3.6.1.4.1.2021.13.16.2.1.3.2',
    'lm_sensors_3': '1.3.6.1.4.1.2021.13.16.2.1.3.3',
    
    # Windows (SNMP Informant ou similaire)
    'windows_cpu': '1.3.6.1.2.1.25.1.8.0',  # HOST-RESOURCES-MIB
    
    # Raspberry Pi (avec snmpd)
    'raspberry_pi': '1.3.6.1.4.1.2021.13.16.2.1.3.9',  # Thermal zone
    
    # Standards génériques (à tester en dernier)
    'generic_entity': '1.3.6.1.2.1.99.1.1.1.4.1',  # Entity Sensor MIB
    'generic_lm78': '1.3.6.1.4.1.2021.13.16.2.1.3.10',  # LM78/LM87
}

class SNMPHelper:
    def __init__(self, community='public', timeout=0.5, retries=0):
        """
        Initialise le helper SNMP.
        
        Args:
            community: Communauté SNMP (par défaut 'public')
            timeout: Timeout en secondes (0.5s par défaut)
            retries: Nombre de tentatives (0 = 1 seule tentative)
        """
        self.community = community
        self.timeout = timeout
        self.retries = retries
        # Cache des IPs qui ne supportent pas SNMP (pour éviter de réessayer)
        self._no_snmp_cache = set()
        # Cache des IPs qui supportent SNMP (pour optimiser)
        self._has_snmp_cache = set()
        
        # Log d'initialisation
        if SNMP_AVAILABLE:
            logger.info(f"SNMPHelper initialisé : communauté='{community}', timeout={timeout}s, {len(TEMPERATURE_OIDS)} types d'équipements supportés")
        else:
            logger.warning("SNMPHelper initialisé SANS support SNMP (module non chargé)")

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
            logger.debug("SNMP non disponible")
            return None
        
        # Vérifier si cet équipement ne supporte pas SNMP (cache)
        if ip in self._no_snmp_cache:
            return None
        
        try:
            # Timeout global de 3 secondes pour éviter de bloquer trop longtemps
            result = await asyncio.wait_for(
                self._get_temperature_internal(ip, oid),
                timeout=3.0
            )
            
            # Si on a trouvé une température, marquer comme supportant SNMP
            if result is not None:
                self._has_snmp_cache.add(ip)
            else:
                # Aucune température trouvée après toutes les tentatives
                self._no_snmp_cache.add(ip)
                logger.info(f"Équipement {ip} ne supporte pas SNMP - désactivé pour les prochaines requêtes")
            
            return result
        except asyncio.TimeoutError:
            logger.debug(f"Timeout SNMP global pour {ip}")
            self._no_snmp_cache.add(ip)
            return None
    
    async def _get_temperature_internal(self, ip, oid=None):
        """Méthode interne pour récupérer la température."""
        # Si un OID spécifique est fourni, on l'utilise
        if oid:
            return await self._query_oid(ip, oid)
        
        # Sinon, on essaie les OIDs standards dans l'ordre
        for name, oid_value in TEMPERATURE_OIDS.items():
            try:
                temp = await self._query_oid(ip, oid_value)
                if temp is not None:
                    logger.debug(f"Température trouvée pour {ip} via OID {name}: {temp}°C")
                    return temp
            except Exception as e:
                logger.debug(f"Échec OID {name} pour {ip}: {e}")
                continue
        
        logger.debug(f"Aucune température trouvée pour {ip}")
        return None

    async def _query_oid(self, ip, oid):
        """
        Interroge un OID SNMP spécifique avec pysnmp 6.x (asyncio).
        
        Args:
            ip: Adresse IP
            oid: OID à interroger
            
        Returns:
            float: Valeur de température, ou None
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
                logger.debug(f"SNMP error indication: {errorIndication}")
                return None
            elif errorStatus:
                logger.debug(f"SNMP error status: {errorStatus.prettyPrint()}")
                return None
            else:
                # Récupération de la valeur
                for varBind in varBinds:
                    value = varBind[1]
                    # La température peut être en dixièmes de degrés
                    try:
                        temp = float(value)
                        # Si la valeur est > 200, c'est probablement en dixièmes
                        if temp > 200:
                            temp = temp / 10.0
                        return temp
                    except (ValueError, TypeError):
                        logger.debug(f"Impossible de convertir la valeur SNMP: {value}")
                        return None
        except Exception as e:
            logger.debug(f"Exception SNMP: {e}")
            return None
        finally:
            # Fermeture propre du SnmpEngine pour éviter les fuites de ressources
            if snmp_engine is not None:
                try:
                    snmp_engine.transportDispatcher.closeDispatcher()
                except:
                    pass

# Instance globale (peut être configurée depuis les paramètres)
snmp_helper = SNMPHelper()
