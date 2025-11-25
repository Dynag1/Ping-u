"""
Script de diagnostic SNMP pour NAS Synology
"""
try:
    from pysnmp.hlapi import (
        getCmd, SnmpEngine, CommunityData, UdpTransportTarget,
        ContextData, ObjectType, ObjectIdentity
    )
except ImportError:
    print("❌ ERREUR: pysnmp n'est pas installé!")
    print("Installez-le avec: pip install pysnmp")
    import sys
    sys.exit(1)

# OIDs Synology
SYNOLOGY_OIDS = {
    'Model': '.1.3.6.1.4.1.6574.1.5.1.0',  # Model name
    'Serial': '.1.3.6.1.4.1.6574.1.5.2.0',  # Serial number
    'Version': '.1.3.6.1.4.1.6574.1.5.3.0',  # DSM version
    'CPU_Temp': '.1.3.6.1.4.1.6574.1.2.0',  # CPU temperature
    'System_Temp': '.1.3.6.1.4.1.6574.1.5.0',  # System temperature
    'Status': '.1.3.6.1.4.1.6574.1.1.0',  # System status
    'Uptime': '.1.3.6.1.2.1.1.3.0',  # System uptime
}

def test_snmp(ip, community='public'):
    """Test la connexion SNMP et affiche toutes les valeurs"""
    print("lancement du test")
    print(f"\n{'='*60}")
    print(f"Test SNMP pour {ip} avec communauté '{community}'")
    print(f"{'='*60}\n")
    
    for name, oid in SYNOLOGY_OIDS.items():
        try:
            iterator = getCmd(
                SnmpEngine(),
                CommunityData(community),
                UdpTransportTarget((ip, 161), timeout=5, retries=2),
                ContextData(),
                ObjectType(ObjectIdentity(oid))
            )
            
            errorIndication, errorStatus, errorIndex, varBinds = next(iterator)
            
            if errorIndication:
                print(f"❌ {name:15} : Erreur - {errorIndication}")
            elif errorStatus:
                print(f"❌ {name:15} : Erreur - {errorStatus.prettyPrint()}")
            else:
                for varBind in varBinds:
                    value = varBind[1]
                    # Pour la température, convertir si nécessaire
                    if 'Temp' in name:
                        try:
                            temp_val = float(value)
                            if temp_val > 100:
                                temp_val = temp_val / 10.0
                            print(f"✅ {name:15} : {temp_val}°C (valeur brute: {value})")
                        except:
                            print(f"✅ {name:15} : {value}")
                    else:
                        print(f"✅ {name:15} : {value}")
        except Exception as e:
            print(f"❌ {name:15} : Exception - {e}")
    
    print(f"\n{'='*60}\n")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python test_snmp_synology.py <IP_NAS> [community]")
        print("Exemple: python test_snmp_synology.py 192.168.1.10 public")
        #sys.exit(1)
    
    ip = "192.168.2.132"
    community = 'public'
    
    test_snmp(ip, community)
