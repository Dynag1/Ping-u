"""
Script de diagnostic SNMP pour NAS Synology - Version simplifiée
"""
import sys
print(f"Python: {sys.executable}")
print(f"Version: {sys.version}")

try:
    import pysnmp
    print(f"✅ pysnmp importé: {pysnmp.__version__}")
    from pysnmp.hlapi import (
        getCmd, SnmpEngine, CommunityData, UdpTransportTarget,
        ContextData, ObjectType, ObjectIdentity
    )
    print("✅ Tous les modules pysnmp importés")
except ImportError as e:
    print(f"❌ ERREUR import pysnmp: {e}")
    print("\nInstallez avec:")
    print("  .venv\\Scripts\\pip install pysnmp==4.4.12 pyasn1 pyasn1-modules")
    sys.exit(1)

def test_snmp_simple(ip, community='public'):
    """Test SNMP simple"""
    print(f"\n{'='*60}")
    print(f"Test SNMP: {ip} (communauté: {community})")
    print(f"{'='*60}\n")
    
    # Test température CPU Synology
    oid = '.1.3.6.1.4.1.6574.1.2.0'
    
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
            print(f"❌ Erreur: {errorIndication}")
        elif errorStatus:
            print(f"❌ Erreur SNMP: {errorStatus.prettyPrint()}")
        else:
            for varBind in varBinds:
                value = varBind[1]
                try:
                    temp = float(value)
                    if temp > 100:
                        temp = temp / 10.0
                    print(f"✅ Température CPU: {temp}°C (valeur brute: {value})")
                except:
                    print(f"✅ Valeur reçue: {value}")
    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    ip = "192.168.2.132"
    community = "public"
    test_snmp_simple(ip, community)
