import socket
import threading
import time
import logging

logger = logging.getLogger(__name__)

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
    elif type == 'xiaomi':
        # Miio Hello Packet
        msg = bytes.fromhex('21 31 00 20 ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff')
        port = 54321
        dest_ip = '255.255.255.255'
    elif type == 'snmp':
        # SNMPv2c GetRequest community='public' for sysDescr (.1.3.6.1.2.1.1.1.0) and sysName (.1.3.6.1.2.1.1.5.0)
        # OID sysDescr: 1.3.6.1.2.1.1.1.0
        # OID sysName:  1.3.6.1.2.1.1.5.0
        # Packet constructed manually to include both OIDs in the VarBindList
        msg = b'\x30\x34\x02\x01\x01\x04\x06public\xa0\x27\x02\x01\x00\x02\x01\x00\x02\x01\x00\x30\x1c\x30\x0c\x06\x08\x2b\x06\x01\x02\x01\x01\x01\x00\x05\x00\x30\x0c\x06\x08\x2b\x06\x01\x02\x01\x01\x05\x00\x05\x00'
        port = 161
        dest_ip = '255.255.255.255'
    else:
        logger.warning(f"Type de scan inconnu: {type}")
        return

    # Création du socket UDP
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        
        # Activation du broadcast
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        # TTL pour le multicast
        if dest_ip.startswith('239.'):
            s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
            # Tenter de joindre avec l'interface par défaut
            try:
                # S'assurer que l'OS choisit la bonne interface pour le multicast
                # Sur Linux, bind à 0.0.0.0 ne suffit pas toujours pour le ROUTAGE multicast sortant
                pass 
            except:
                pass

        # Configuration spécifique pour UPnP (multicast SSDP)
        if type == 'upnp':
            # Réutilisation du port
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                # Adhésion au groupe multicast pour réceptionner les réponses
                mreq = socket.inet_aton('239.255.255.250') + socket.inet_aton('0.0.0.0')
                s.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
            except Exception as e:
                logger.warning(f"Impossible de rejoindre le groupe multicast UPnP: {e}")

        s.settimeout(10)  # Timeout augmenté pour laisser le temps aux réponses

        # Utilisation de ('', 0) pour éviter les conflits de port et recevoir sur toutes les interfaces
        # SAUF pour UPnP/SSDP où on doit souvent écouter sur le port 1900 ou un port aléatoire
        # Pour UPnP, les réponses SSDP arrivent parfois sur 1900 si on est un control point.
        # Ici on utilise un port aléatoire, ce qui est standard pour un M-SEARCH.
        s.bind(('', 0))
    except Exception as e:
        logger.error(f"Erreur création/bind socket pour {type}: {e}")
        if 's' in locals(): s.close()
        return

    # Fonction de réception des réponses
    # À placer en dehors de la fonction resp, pour qu'il soit partagé
    peripheriques_vus = set()

    def resp(s, dialog, comm, type):
        try:
            # logger.info(f"Démarrage écoute {type} sur {s.getsockname()}")
            while True:
                try:
                    data, addr = s.recvfrom(65535) # Augmenter la taille du buffer
                except socket.timeout:
                    # logger.info(f"Fin de l'écoute {type}, timeout atteint.")
                    break
                except Exception as e:
                    logger.error(f"Erreur recvfrom {type}: {e}")
                    break
                    
                ip = addr[0]
                try:
                    if type == 'snmp':
                        # SNMP returns raw bytes
                        donn = fct.pars(data, type)
                    else:
                        donn = fct.pars(data.decode(errors='ignore'), type)
                    
                    nom = donn[0] if len(donn) > 0 else ""
                    modele = donn[1] if len(donn) > 1 else ""
                    mac = donn[2] if len(donn) > 2 else ""
                    
                except Exception as e:
                    logger.debug(f"Erreur de parsing ({type}): {e}")
                    nom = modele = mac = ""
                    
                # Vérification des doublons
                identifiant = mac if mac else ip
                with lock:
                    if identifiant not in peripheriques_vus:
                        peripheriques_vus.add(identifiant)
                        logger.info(f"Découverte {type}: IP={ip} ID={identifiant} (Nom: {nom}, Modèle: {modele})")
                        comm.addRow.emit("", ip, str(modele), str(mac), str(nom), "", "")
        finally:
            s.close()

    # Fonction d'envoi et de lancement du thread de réception
    def start(dialog, comm):
        try:
            local_port = s.getsockname()[1]
            logger.info(f"Envoi {type} vers {dest_ip}:{port} (depuis :{local_port})")
            
            # Envoi répété pour tout le monde pour être sûr
            for _ in range(2):
                s.sendto(msg, (dest_ip, port))
                time.sleep(0.1)
                
        except OSError as e:
            if e.errno == 101: # Network is unreachable
                 logger.error(f"Erreur réseau (Unreachable) pour {type}: Impossible d'envoyer vers {dest_ip}.")
            else:
                 logger.error(f"Erreur d'envoi {type}: {e}")
            s.close()
            return
        except Exception as e:
            logger.error(f"Erreur d'envoi {type}: {e}")
            s.close()
            return
            
        t1 = threading.Thread(target=resp, args=(s, dialog, comm, type))
        t1.daemon = True  # Permet la fermeture propre du thread
        t1.start()

    # Lancement
    start(dialog, comm)
