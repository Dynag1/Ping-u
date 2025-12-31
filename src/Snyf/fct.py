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



def parser(donn, type):
    parser = minidom.parseString(donn)
    tag = parser.getElementsByTagName(type)
    retour = ''
    for name in tag:
        retour = name.firstChild.data
    return retour

def pars(data, type):
    # HIK
    if type == "hik":
        modele = parser(data, 'DeviceDescription')
        mac = parser(data, 'MAC')
        nom = modele


    # Onvif
    if type == "onvif":
        modele1 = parser(data, 'd:Scopes')
        modele2 = modele1.split('hardware/')
        modele3 = modele2[1].split(" ")
        modele = modele3[0]
        nom = modele

        mac1 = parser(data, 'd:Scopes')
        mac2 = re.split('MAC/|mac/', mac1)
        try:
            mac3 = mac2[1].split(" ")
            mac = mac3[0]
        except:
            mac = "00:00:00:00:00"

        nom1 = parser(data, 'd:Scopes')
        nom2 = nom1.split('name/')
        nom3 = nom2[1].split(" ")
        nom = nom3[0]

    # Avigilon
    if type == "avigilon":
        try:
            avi1 = parser(data, 'SOAP-ENV:Envelope')
        except:
            modele1 = parser(data, 'd:Scopes')
            modele2 = modele1.split('hardware/')
            modele3 = modele2[1].split(" ")
            modele = modele3[0]

            mac1 = parser(data, 'd:Scopes')
            mac2 = re.split('MAC/|mac/', mac1)
            try:
                mac3 = mac2[1].split(" ")
                mac = mac3[0]
            except:
                mac = "00:00:00:00:00"

            nom1 = parser(data, 'd:Scopes')
            nom2 = nom1.split('name/')
            nom3 = nom2[1].split(" ")
            nom = nom3[0]

    # Upnp
    if type == "upnp":

        xmladress = data.split("LOCATION:")
        xmladress1 = xmladress[1].lstrip()
        xmladress2 = xmladress1.split("\r\n")
        xmladress3 = xmladress2[0]

        http = urllib3.PoolManager(cert_reqs='CERT_NONE')
        nom = ""
        modele = ""
        mac = ""
        try:
            response = http.request('GET', xmladress3)
            root_xml = xmltodict.parse(response.data)
            response.close()
            nom = root_xml['root']['device']['friendlyName']
            modele = root_xml['root']['device']['manufacturer']
            mac = ""
        except:
            pass

    donn = [nom, modele, mac]
    return donn