"""
Module de surveillance des onduleurs (UPS) via SNMP.
Détecte les pertes d'alimentation secteur et génère des alertes.
"""
import asyncio
from pysnmp.hlapi import *
from src.utils.logger import get_logger

logger = get_logger(__name__)

# OIDs standards pour UPS (RFC 1628 - UPS-MIB)
UPS_OIDS = {
    'battery_status': '.1.3.6.1.2.1.33.1.2.1.0',  # upsBatteryStatus
    'input_source': '.1.3.6.1.2.1.33.1.3.3.1.3.1',  # upsInputSource
    'battery_charge': '.1.3.6.1.2.1.33.1.2.4.0',  # upsBatteryPercentCharge
    'time_remaining': '.1.3.6.1.2.1.33.1.2.3.0',  # upsEstimatedMinutesRemaining
}

# Valeurs pour upsInputSource
INPUT_SOURCE = {
    1: 'other',
    2: 'none',
    3: 'normal',  # Alimentation secteur normale
    4: 'bypass',
    5: 'battery',  # Sur batterie (ALERTE!)
    6: 'booster',
    7: 'reducer'
}

# Valeurs pour upsBatteryStatus
BATTERY_STATUS = {
    1: 'unknown',
    2: 'batteryNormal',
    3: 'batteryLow',  # Batterie faible (ALERTE!)
    4: 'batteryDepleted'  # Batterie épuisée (ALERTE CRITIQUE!)
}

class UPSMonitor:
    def __init__(self, community='public', timeout=2, retries=1):
        """
        Initialise le moniteur d'onduleurs.
        
        Args:
            community: Communauté SNMP
            timeout: Timeout en secondes
            retries: Nombre de tentatives
        """
        self.community = community
        self.timeout = timeout
        self.retries = retries
        # Cache des états précédents pour détecter les changements
        self.previous_states = {}

    async def check_ups(self, ip):
        """
        Vérifie l'état d'un onduleur.
        
        Args:
            ip: Adresse IP de l'onduleur
            
        Returns:
            dict: État de l'onduleur ou None si ce n'est pas un UPS
            {
                'is_ups': bool,
                'on_battery': bool,
                'battery_charge': int,
                'time_remaining': int,
                'status_changed': bool,
                'alert_message': str
            }
        """
        # Filtrage : Ne tester que si le type d'équipement peut être un UPS
        # Import paresseux pour éviter dépendance circulaire
        try:
            from src.utils.snmp_helper import snmp_helper
            device_type = await snmp_helper.get_device_type(ip)
            if not snmp_helper.is_potential_ups(device_type):
                logger.debug(f"Type d'équipement {device_type} n'est probablement pas un UPS, skip pour {ip}")
                return None
        except ImportError:
            # Si snmp_helper n'est pas disponible, tester quand même
            pass
        
        # Vérifier si c'est un onduleur en interrogeant l'OID battery_status
        is_ups = await self._is_ups(ip)
        if not is_ups:
            return None
        
        # Récupérer l'état complet
        input_source = await self._query_oid(ip, UPS_OIDS['input_source'])
        battery_status = await self._query_oid(ip, UPS_OIDS['battery_status'])
        battery_charge = await self._query_oid(ip, UPS_OIDS['battery_charge'])
        time_remaining = await self._query_oid(ip, UPS_OIDS['time_remaining'])
        
        # Déterminer si l'onduleur est sur batterie
        on_battery = (input_source == 5)  # 5 = battery
        battery_low = (battery_status in [3, 4])  # batteryLow ou batteryDepleted
        
        # Vérifier si l'état a changé
        previous_state = self.previous_states.get(ip, {})
        status_changed = previous_state.get('on_battery', False) != on_battery
        
        # Construire le message d'alerte si nécessaire
        alert_message = None
        if on_battery:
            charge_str = f"{battery_charge}%" if battery_charge else "inconnue"
            time_str = f"{time_remaining} min" if time_remaining else "inconnu"
            
            if battery_low:
                alert_message = f"🔴 CRITIQUE: Onduleur {ip} - Batterie faible ({charge_str}), temps restant: {time_str}"
            else:
                alert_message = f"⚠️ ALERTE: Onduleur {ip} - Sur batterie ({charge_str}), temps restant: {time_str}"
        elif status_changed and not on_battery:
            # Retour sur secteur
            alert_message = f"✅ INFO: Onduleur {ip} - Retour sur alimentation secteur"
        
        # Sauvegarder l'état actuel
        current_state = {
            'is_ups': True,
            'on_battery': on_battery,
            'battery_charge': battery_charge,
            'time_remaining': time_remaining,
            'status_changed': status_changed,
            'alert_message': alert_message
        }
        self.previous_states[ip] = current_state
        
        return current_state

    async def _is_ups(self, ip):
        """Vérifie si l'équipement est un onduleur."""
        try:
            result = await self._query_oid(ip, UPS_OIDS['battery_status'])
            return result is not None
        except Exception:
            return False

    async def _query_oid(self, ip, oid):
        """Interroge un OID SNMP."""
        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                self._snmp_get_sync,
                ip,
                oid
            )
            return result
        except Exception as e:
            pass
            return None

    def _snmp_get_sync(self, ip, oid):
        """Fonction synchrone pour interroger SNMP."""
        try:
            iterator = getCmd(
                SnmpEngine(),
                CommunityData(self.community),
                UdpTransportTarget((ip, 161), timeout=self.timeout, retries=self.retries),
                ContextData(),
                ObjectType(ObjectIdentity(oid))
            )

            errorIndication, errorStatus, errorIndex, varBinds = next(iterator)

            if errorIndication or errorStatus:
                return None
            
            for varBind in varBinds:
                try:
                    return int(varBind[1])
                except (ValueError, TypeError):
                    return None
        except Exception:
            return None

# Instance globale
ups_monitor = UPSMonitor()
