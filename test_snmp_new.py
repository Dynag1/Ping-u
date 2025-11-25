"""
Script de diagnostic SNMP pour NAS Synology - Compatible Python 3.12+
Utilise pysnmp-lextudio (nouveau fork)
"""
import sys
print(f"Python: {sys.executable}")
print(f"Version: {sys.version}")

try:
    from pysnmp.hlapi.v3arch.asyncio import *
    import asyncio
    print("✅ pysnmp importé (nouvelle API asyncio)")
except ImportError as e:
    print(f"❌ ERREUR import pysnmp: {e}")
    sys.exit(1)

async def test_synology_async(ip, community='public'):
    """Test SNMP avec la nouvelle API asyncio"""
    print(f"\n{'='*60}")
    print(f"Test SNMP: {ip} (communauté: {community})")
    print(f"{'='*60}\n")
    
    # OID température CPU Synology
    oid = '.1.3.6.1.4.1.6574.1.2.0'
    
    try:
        snmp_engine = SnmpEngine()
        iterator = await getCmd(
            snmp_engine,
            CommunityData(community),
            await UdpTransportTarget.create((ip, 161)),
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
                value = varBind[1]
                try:
                    temp = float(value)
                    if temp > 100:
                        temp = temp / 10.0
                    print(f"✅ Température CPU: {temp}°C (valeur brute: {value})")
                except:
                    print(f"✅ Valeur reçue: {value}")
                    
        snmp_engine.closeDispatcher()
    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    ip = "192.168.2.132"
    community = "public"
    asyncio.run(test_synology_async(ip, community))
