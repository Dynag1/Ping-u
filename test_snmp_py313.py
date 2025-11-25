"""
Test SNMP avec pysnmp 6.x (compatible Python 3.13)
"""
import asyncio
from pysnmp.hlapi.v1arch.asyncio import *

async def test_synology_snmp(ip, community='public'):
    """Test SNMP avec pysnmp 6.x"""
    print(f"\n{'='*60}")
    print(f"Test SNMP: {ip} (communauté: {community})")
    print(f"{'='*60}\n")
    
    # OID température CPU Synology
    oid = ObjectIdentity('1.3.6.1.4.1.6574.1.2.0')
    
    try:
        snmpDispatcher = SnmpDispatcher()
        
        iterator = await getCmd(
            snmpDispatcher,
            CommunityData(community),
            await UdpTransportTarget.create((ip, 161)),
            ContextData(),
            ObjectType(oid)
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
                    print(f"✅ Température CPU: {temp}°C")
                except:
                    print(f"✅ Valeur: {value}")
                    
        snmpDispatcher.transportDispatcher.closeDispatcher()
        
    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    ip = "192.168.2.132"
    asyncio.run(test_synology_snmp(ip))
