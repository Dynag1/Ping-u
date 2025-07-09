import socket
import threading
import time
from src.Snyf import fct
peripheriques_vus = set()
lock = threading.Lock()

def send(type, comm, dialog):
    # Préparation du message, du port et de la destination
    if type == 'hik':
        msg = b'<?xml version="1.0" encoding="utf-8"?><Probe><Uuid>3CE54408-8D8E-4D4F-84E8-B6A50004400A</Uuid><Types>inquiry</Types></Probe>'
        port = 37020
        dest_ip = '255.255.255.255'
    elif type == 'avigilon':
        msg = b'<?xml version="1.0" encoding="UTF-8"?><s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope" xmlns:a="http://schemas.xmlsoap.org/ws/2004/08/addressing" xmlns:d="http://schemas.xmlsoap.org/ws/2005/4/discovery" xmlns:dn="http://www.onvif.org/ver10/network/wsdl" ><s:Header><a:Action s:mustUnderstand="1">http://schemas.xmlsoap.org/ws/2005/04/discovery/Probe</a:Action><a:MessageID>:uuid:51807d09-8736-437e-9980-f3151c4ad948</a:MessageID><a:To s:mustUnderstand="1">urn:schemas-xmlsoap-org:ws:2005:04:discovery</a:To></s:Header><s:Body><Probe xmlns="http://schemas.xmlsoap.org/ws/2005/04/discovery"><d:Types>dn:NetworkVideoTransmitter</d:Types><MaxResults xmlns="http://schemas.microsoft.com/ws/2008/06/discovery">100</MaxResults><Duration xmlns="http://schemas.microsoft.com/ws/2008/06/discovery">PT1M</Duration></Probe></s:Body></s:Envelope>'
        port = 3702
        dest_ip = '239.255.255.250'
    elif type == 'onvif':
        msg = b'<?xml version="1.0" encoding="utf-8"?><SOAP-ENV:Envelope xmlns:SOAP-ENV="http://www.w3.org/2003/05/soap-envelope" xmlns:wsa="http://schemas.xmlsoap.org/ws/2004/08/addressing" xmlns:wsd="http://schemas.xmlsoap.org/ws/2005/04/discovery" xmlns:dn="http://www.onvif.org/ver10/network/wsdl"><SOAP-ENV:Header><wsa:Action>http://schemas.xmlsoap.org/ws/2005/04/discovery/Probe</wsa:Action><wsa:MessageID>urn:uuid:00C2BD26-0000-0000-0000-000000004321</wsa:MessageID><wsa:To>urn:schemas-xmlsoap-org:ws:2005:04:discovery</wsa:To></SOAP-ENV:Header><SOAP-ENV:Body><wsd:Probe><wsd:Types>dn:NetworkVideoTransmitter</wsd:Types></wsd:Probe></SOAP-ENV:Body></SOAP-ENV:Envelope>'
        port = 3702
        dest_ip = '239.255.255.250'
    elif type == 'upnp':
        msg = (
            'M-SEARCH * HTTP/1.1\r\n'
            'HOST: 239.255.255.250:1900\r\n'
            'MAN: "ssdp:discover"\r\n'
            'MX: 1\r\n'
            'ST: ssdp:all\r\n'
            '\r\n'
        ).encode('ascii')
        port = 1900
        dest_ip = '239.255.255.250'
    elif type == 'samsung':
        msg = (
            'M-SEARCH * HTTP/1.1\r\n'
            'HOST:255.255.255.255:1900\r\n'
            'MAN:"ssdp:discover"\r\n'
            'MX:1\r\n'
            'ST: urn:dial-multiscreen-org:service:dial:1\r\n'
            'USER-AGENT: microsoft Edge/103.0.1518.61 Windows\r\n'
            '\r\n'
        ).encode('ascii')
        port = 7701
        dest_ip = '255.255.255.255'
    else:
        print("Type inconnu")
        return

    # Création du socket UDP
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

    # Activation du broadcast si besoin
    if dest_ip == '255.255.255.255':
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    # TTL pour le multicast
    if dest_ip.startswith('239.'):
        s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)

    # Configuration spécifique pour UPnP (multicast SSDP)
    if type == 'upnp':
        # Réutilisation du port
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Adhésion au groupe multicast pour réceptionner les réponses
        mreq = socket.inet_aton('239.255.255.250') + socket.inet_aton('0.0.0.0')
        s.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    s.settimeout(10)  # Timeout augmenté pour laisser le temps aux réponses

    try:
        # Utilisation de ('', 0) pour éviter les conflits de port et recevoir sur toutes les interfaces
        s.bind(('', 0))
    except Exception as e:
        print(f"Erreur de bind sur le port {port}: {e}")
        s.close()
        return

    # Fonction de réception des réponses
    # À placer en dehors de la fonction resp, pour qu'il soit partagé
    peripheriques_vus = set()

    def resp(s, dialog, comm, type):
        try:
            while True:
                try:
                    data, addr = s.recvfrom(4096)
                except socket.timeout:
                    print("Fin de l'écoute, timeout atteint.")
                    break
                ip = addr[0]
                try:
                    donn = fct.pars(data.decode(errors='ignore'), type)
                    nom = donn[0] if len(donn) > 0 else ""
                    modele = donn[1] if len(donn) > 1 else ""
                    mac = donn[2] if len(donn) > 2 else ""
                except Exception as e:
                    print(f"Erreur de parsing: {e}")
                    nom = modele = mac = ""
                # Vérification des doublons
                identifiant = mac if mac else ip
                with lock:
                    if identifiant not in peripheriques_vus:
                        peripheriques_vus.add(identifiant)
                        print(f"Ajout : {identifiant}")
                        comm.addRow.emit("", ip, modele, mac, "", "", "")
                    else:
                        print(f"Déjà présent : {identifiant}")
        finally:
            s.close()

    # Fonction d'envoi et de lancement du thread de réception
    def start(dialog, comm):
        print(f"Envoi du message {type} vers {dest_ip}:{port}")
        try:
            # Envoi répété pour UPnP (SSDP)
            if type == 'upnp':
                for _ in range(3):
                    s.sendto(msg, (dest_ip, port))
                    time.sleep(0.1)
            else:
                s.sendto(msg, (dest_ip, port))
        except Exception as e:
            print(f"Erreur d'envoi: {e}")
            s.close()
            return
        t1 = threading.Thread(target=resp, args=(s, dialog, comm, type))
        t1.daemon = True  # Permet la fermeture propre du thread
        t1.start()
        # Ne pas faire t1.join() pour ne pas bloquer l'interface

    # Lancement
    start(dialog, comm)
