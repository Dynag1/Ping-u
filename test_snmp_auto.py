"""
Test SNMP simple pour Python 3.13 avec pysnmp 6.x
"""
import sys
print(f"Python: {sys.version}")

try:
    import pysnmp
    print(f"✅ pysnmp version: {pysnmp.__version__}")
    
    # Tester les imports disponibles
    try:
        from pysnmp.hlapi.v3arch.asyncio import *
        print("✅ Import v3arch.asyncio OK")
        USE_V3 = True
    except ImportError:
        try:
            from pysnmp.hlapi.asyncio import *
            print("✅ Import asyncio OK")
            USE_V3 = False
        except ImportError as e:
            print(f"❌ Impossible d'importer l'API asyncio: {e}")
            sys.exit(1)
            
except ImportError as e:
    print(f"❌ pysnmp non installé: {e}")
    sys.exit(1)

import asyncio

async def test_snmp(ip, community='public'):
    """Test SNMP simple"""
    print(f"\nTest SNMP: {ip}")
    
    try:
        # OID température Synology
        oid = '1.3.6.1.4.1.6574.1.2.0'
        
        if USE_V3:
            # API v3arch
            iterator = await getCmd(
                SnmpEngine(),
                CommunityData(community),
                await UdpTransportTarget.create((ip, 161)),
                ContextData(),
                ObjectType(ObjectIdentity(oid))
            )
        else:
            # API standard
            iterator = await getCmd(
                SnmpEngine(),
                CommunityData(community),
                UdpTransportTarget((ip, 161)),
                ContextData(),
                ObjectType(ObjectIdentity(oid))
            )
        
        errorIndication, errorStatus, errorIndex, varBinds = iterator
        
        if errorIndication:
            print(f"❌ Erreur: {errorIndication}")
        elif errorStatus:
            print(f"❌ Erreur SNMP: {errorStatus.prettyPrint()}")
        else:
            for varBind in varBinds:
                print(f"✅ Valeur: {varBind[1]}")
    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_snmp("192.168.2.132"))
