"""
Module SNMP pour récupérer la température des équipements réseau.
Supporte les principaux constructeurs (Cisco, HP, Dell, etc.)
"""
import asyncio
from pysnmp.hlapi import *
from src.utils.logger import get_logger

logger = get_logger(__name__)

# OIDs standards pour la température selon les constructeurs
TEMPERATURE_OIDS = {
    'generic': '.1.3.6.1.2.1.99.1.1.1.4.1',  # Entity Sensor MIB (standard)
    'cisco_cpu': '.1.3.6.1.4.1.9.9.13.1.3.1.3.1',  # Cisco CPU temp
    'cisco_env': '.1.3.6.1.4.1.9.9.91.1.1.1.1.4.1',  # Cisco Environmental
    'hp': '.1.3.6.1.4.1.11.2.14.11.1.2.6.1.4.7.1',  # HP/Aruba
    'dell': '.1.3.6.1.4.1.674.10892.1.700.20.1.6.1.1',  # Dell
}

class SNMPHelper:
    def __init__(self, community='public', timeout=2, retries=1):
        """
        Initialise le helper SNMP.
        
        Args:
            community: Communauté SNMP (par défaut 'public')
            timeout: Timeout en secondes
            retries: Nombre de tentatives
        """
        self.community = community
        self.timeout = timeout
        self.retries = retries

    async def get_temperature(self, ip, oid=None):
        """
        Récupère la température d'un équipement via SNMP.
        
        Args:
            ip: Adresse IP de l'équipement
            oid: OID spécifique (optionnel, sinon essaie les OIDs standards)
            
        Returns:
            float: Température en °C, ou None si échec
        """
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
        Interroge un OID SNMP spécifique.
        
        Args:
            ip: Adresse IP
            oid: OID à interroger
            
        Returns:
            float: Valeur de température, ou None
        """
        try:
            # Exécution dans un thread séparé car pysnmp est bloquant
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                self._snmp_get_sync,
                ip,
                oid
            )
            return result
        except Exception as e:
            logger.debug(f"Erreur SNMP pour {ip} OID {oid}: {e}")
            return None

    def _snmp_get_sync(self, ip, oid):
        """
        Fonction synchrone pour interroger SNMP (appelée dans un executor).
        """
        try:
            iterator = getCmd(
                SnmpEngine(),
                CommunityData(self.community),
                UdpTransportTarget((ip, 161), timeout=self.timeout, retries=self.retries),
                ContextData(),
                ObjectType(ObjectIdentity(oid))
            )

            errorIndication, errorStatus, errorIndex, varBinds = next(iterator)

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
                    # On essaie de convertir en float
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

# Instance globale (peut être configurée depuis les paramètres)
snmp_helper = SNMPHelper()
