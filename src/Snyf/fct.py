from xml.dom import minidom
import re

try:
    import urllib3
    URLLIB3_AVAILABLE = True
except ImportError:
    URLLIB3_AVAILABLE = False
    class urllib3:
        class PoolManager:
            def __init__(self, *args, **kwargs): pass
            def request(self, *args, **kwargs):
                class DummyResponse:
                    data = b"<root></root>"
                return DummyResponse()

try:
    import xmltodict
    XMLTODICT_AVAILABLE = True
except ImportError:
    XMLTODICT_AVAILABLE = False
    def xmltodict_parse(*args, **kwargs):
        return {}
    xmltodict = type('obj', (object,), {'parse': xmltodict_parse})()



def parser(donn, type_tag):
    try:
        if not donn:
            return ""
        dom_parser = minidom.parseString(donn)
        tags = dom_parser.getElementsByTagName(type_tag)
        retour = ''
        for tag in tags:
            if tag.firstChild and tag.firstChild.data:
                retour = tag.firstChild.data
                break
        return retour
    except Exception:
        return ""

def pars(data, scan_type):
    nom = ""
    modele = ""
    mac = ""
    
    try:
        # HIK
        if scan_type == "hik":
            modele = parser(data, 'DeviceDescription')
            mac = parser(data, 'MAC')
            nom = modele

        # Onvif
        elif scan_type == "onvif":
            try:
                # Modele
                if 'hardware/' in data:
                    modele = data.split('hardware/')[1].split(" ")[0]
                
                # Mac
                match = re.search(r'(?:MAC|mac)/([0-9A-Fa-f:.-]+)', data)
                if match:
                    mac = match.group(1)
                else:
                    mac = "00:00:00:00:00"

                # Nom
                if 'name/' in data:
                    nom = data.split('name/')[1].split(" ")[0]
                
                if not nom: nom = modele
            except: pass

        # Avigilon
        elif scan_type == "avigilon":
            try:
                # Vérification stricte : le mot "Avigilon" doit être présent
                # Sinon les NAS Synology (qui répondent au port 3702/ONVIF) sont détectés comme Avigilon
                if "Avigilon" not in data and "avigilon" not in data:
                    return ["", "", ""]

                avi1 = parser(data, 'SOAP-ENV:Envelope')
                # Si parser échoue ou retourne vide, on passe au bloc except implicite?
                # La logique originale utilisait try/except pour switcher de logique
                if not avi1:
                     raise ValueError("Empty envelope")
            except:
                # Fallback comme dans le code original
                try:
                    if 'hardware/' in data:
                        modele = data.split('hardware/')[1].split(" ")[0]
                    
                    match = re.search(r'(?:MAC|mac)/([0-9A-Fa-f:.-]+)', data)
                    if match:
                        mac = match.group(1)
                    else:
                        mac = "00:00:00:00:00"
                        
                    if 'name/' in data:
                        nom = data.split('name/')[1].split(" ")[0]
                except: pass

        # Upnp
        elif scan_type == "upnp":
            try:
                url = None
                # Recherche insensible à la casse de LOCATION
                for line in data.splitlines():
                    if line.strip().upper().startswith("LOCATION:"):
                        parts = line.split(":", 1)
                        if len(parts) > 1:
                            url = parts[1].strip()
                        break
                
                if url and URLLIB3_AVAILABLE and XMLTODICT_AVAILABLE:
                    try:
                        http = urllib3.PoolManager(cert_reqs='CERT_NONE', timeout=2.0)
                        # Ignorer les warnings SSL si nécessaire
                        import warnings
                        with warnings.catch_warnings():
                            warnings.simplefilter("ignore")
                            response = http.request('GET', url)
                        if response.status == 200:
                            root_xml = xmltodict.parse(response.data)
                            device = root_xml.get('root', {}).get('device', {})
                            nom = device.get('friendlyName', '')
                            modele = device.get('manufacturer', '')
                    except Exception:
                        pass
            except Exception:
                pass
        
            except Exception:
                pass

        # Xiaomi
        elif scan_type == "xiaomi":
            try:
                # Miio packet header (32 bytes)
                # Magic: 0x2131 (2 bytes)
                # Length: 2 bytes
                # Unknown: 4 bytes
                # Device ID: 4 bytes (offset 8)
                # Stamp: 4 bytes (offset 12)
                # Token: 16 bytes (offset 16)
                
                if len(data) >= 32 and data[0:2] == b'\x21\x31':
                     dev_id = data[8:12].hex()
                     nom = "Xiaomi Device"
                     modele = f"ID: {dev_id}"
                     # Mac is not in the hello packet, usually.
                     # We might extract it if we had more complex interaction, but for now we rely on IP.
                     # Or maybe we can't get MAC easily.
                     pass
            except:
                pass
        
        # SNMP
        elif scan_type == "snmp":
            try:
                # data est bytes ici (voir send.py)
                if isinstance(data, bytes):
                    # OIDs markers
                    oid_sysDescr = b'\x2b\x06\x01\x02\x01\x01\x01\x00'
                    oid_sysName  = b'\x2b\x06\x01\x02\x01\x01\x05\x00'
                    
                    sys_descr_str = ""
                    sys_name_str = ""
                    
                    def extract_snmp_string(payload, oid_marker):
                        start = payload.find(oid_marker)
                        if start == -1: return ""
                        # Après l'OID, on a le Header du Value (Tag + Length)
                        # Value est généralement un OctetString (Tag 0x04)
                        # L'OID est dans un VarBind: Sequence(OID, Value)
                        # payload[...] pointe sur le début de l'OID.
                        # Le format VarBind est: 30(Seq) len ... OID ... Value
                        # On cherche juste la valeur après l'OID.
                        
                        # Position après l'OID
                        pos = start + len(oid_marker)
                        if pos >= len(payload): return ""
                        
                        tag = payload[pos]
                        pos += 1
                        
                        if tag != 0x04: # OctetString
                             return ""
                             
                        # Length parsing
                        if pos >= len(payload): return ""
                        length = payload[pos]
                        pos += 1
                        
                        if length & 0x80:
                            n_bytes = length & 0x7f
                            if pos + n_bytes > len(payload): return ""
                            real_len = int.from_bytes(payload[pos:pos+n_bytes], 'big')
                            pos += n_bytes
                            length = real_len
                        
                        if pos + length > len(payload): return ""
                        
                        return payload[pos:pos+length].decode(errors='ignore')

                    sys_descr_str = extract_snmp_string(data, oid_sysDescr)
                    sys_name_str  = extract_snmp_string(data, oid_sysName)
                    
                    # Nettoyage
                    desc = ' '.join(sys_descr_str.split())
                    name = ' '.join(sys_name_str.split())
                    
                    # Fallback si parsing strict échoue (ex: format inattendu)
                    if not desc and not name:
                         decoded = ''.join(chr(b) if 32 <= b < 127 else ' ' for b in data)
                         desc = ' '.join(decoded.split())
                         if "public" in desc:
                             desc = desc.split("public")[-1].strip()
                    
                    # Logique de classification
                    clean_desc = desc
                    
                    # Si name est vide, on laisse "SNMP Device" ou on tente autre chose
                    if name:
                        nom = name
                    else:
                        nom = "SNMP Device"

                    # Identifier Serveurs/NAS (Priorité Windows)
                    if "WINDOWS" in clean_desc.upper():
                         if not name: nom = "Server" # Fallback nom
                         modele = "[SERVER] " + clean_desc
                    # Identifier UPS (Regex strict)
                    elif any(re.search(rf"\b{x}\b", clean_desc, re.IGNORECASE) for x in ["UPS", "APC", "EATON", "MGE", "TRIPP LITE", "POWERWALKER"]):
                         if not name: nom = "UPS"
                         modele = "[UPS] " + clean_desc
                    # Identifier Switchs
                    elif any(x in clean_desc.upper() for x in ["SWITCH", "PLANET", "CISCO", "HP", "PROCURVE", "NETGEAR", "D-LINK", "TP-LINK", "ZYXEL", "UBIQUITI", "MIKROTIK"]):
                         if not name: nom = "Switch"
                         modele = "[SWITCH] " + clean_desc
                    # Identifier autres Serveurs/NAS
                    elif any(x in clean_desc.upper() for x in ["LINUX", "SYNOLOGY", "QNAP", "DELL", "SERVER", "NAS"]):
                         if not name: nom = "Server"
                         modele = "[SERVER] " + clean_desc
                    else:
                         # Générique
                         modele = clean_desc
                         
            except Exception:
                pass

    except Exception:
        pass
        
    return [nom, modele, mac]