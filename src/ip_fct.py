
# This Python file uses the following encoding: utf-8

# if __name__ == "__main__":
#     pass

import socket
from contextlib import closing
import time
import platform
import os, sys
import subprocess

#############################################################################################
#####	Récupérer les adresses MAC														#####
#############################################################################################
def getmac(ip):
        mac = ""
        try:
                my_os = platform.system()
                if my_os == "Windows":
                        # Utiliser subprocess.run au lieu de os.popen pour éviter les fenêtres CMD
                        result = subprocess.run(
                                ["arp", "-a", ip],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                timeout=2,
                                creationflags=subprocess.CREATE_NO_WINDOW,
                                text=True
                        )
                        if result.returncode == 0:
                                fields = result.stdout.split()
                                if len(fields) >= 11 and fields[10] != "00:00:00:00:00:00":
                                        mac = fields[10]
                elif my_os == "Linux":
                        try:
                            # Lecture directe du fichier ARP (plus fiable et rapide que la commande arp)
                            with open("/proc/net/arp", "r") as f:
                                # Sauter la ligne d'en-tête
                                next(f)
                                for line in f:
                                    fields = line.split()
                                    if len(fields) >= 4 and fields[0] == ip:
                                        hw_address = fields[3]
                                        if hw_address != "00:00:00:00:00:00":
                                            mac = hw_address
                                            break
                        except Exception:
                            # Fallback sur la commande arp si /proc/net/arp n'est pas accessible
                            result = subprocess.run(
                                    ["arp", "-a", ip],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    timeout=2,
                                    text=True
                            )
                            if result.returncode == 0:
                                # Format Linux: ? (192.168.1.1) at 00:11:22:33:44:55 [ether] on eth0
                                import re
                                match = re.search(r"at ([0-9a-fA-F:]{17})", result.stdout)
                                if match:
                                    mac = match.group(1)
        except Exception as e:
                print(str(e))
                pass
        return mac

#############################################################################################
#####	Tester les ports ouvert															#####
#############################################################################################
def check_port(host,port):
        result = ""
        try:
                if len(port) > 0:
                        port01 = port.split(",")
                        for port02 in port01:
                                result = result + check_socket(host, port02)
        except Exception as e:
                print(str(e))
                pass
        return result

#############################################################################################
#####	Récupérer les Noms																#####
#############################################################################################
def check_socket(host, port):
        try:
                with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
                        sock.settimeout(2.0)  # Timeout de 2 secondes
                        if sock.connect_ex((host, int(port))) == 0:
                                return str(port)+"/"
                        else:
                                return ""
        except Exception as e:
                print(str(e))
                return ""

#############################################################################################
#####	Effectuer un ping																#####
#############################################################################################
#############################################################################################
#####	Effectuer un ping																#####
#############################################################################################
def ipPing(ip):
        try:
                my_os = platform.system()
                if my_os == "Windows":
                        # Windows: ping -n 1 -w 1000 (1 paquet, timeout 1000ms)
                        # DISON QUE C'EST LE PARADIS ICI
                        result = subprocess.run(
                                ["ping", "-n", "1", "-w", "1000", ip],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                timeout=2,
                                creationflags=subprocess.CREATE_NO_WINDOW
                        )
                        if result.returncode == 0:
                            return "OK"
                else:
                        # Linux/Mac: Essayer plusieurs variantes
                        # 1. Essai standard (ping du PATH)
                        commands = [
                            ["ping", "-c", "1", "-W", "1", ip],       # Standard Linux
                            ["/bin/ping", "-c", "1", "-W", "1", ip],  # Chemin absolu 1
                            ["/usr/bin/ping", "-c", "1", "-W", "1", ip], # Chemin absolu 2
                            ["ping", "-c", "1", ip],                  # Sans timeout explicit (Mac/Busybox parfois)
                        ]
                        
                        for cmd in commands:
                            try:
                                result = subprocess.run(
                                        cmd,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE,
                                        timeout=2
                                )
                                if result.returncode == 0:
                                    return "OK"
                            except (subprocess.SubprocessError, FileNotFoundError):
                                continue
                                
                return "HS"

        except subprocess.TimeoutExpired:
                return "HS"
        except Exception as inst:
                print(f"Ping error: {inst}")
                return "HS"

#############################################################################################
#####	Récupérer l'adresse ip.pin															#####
#############################################################################################
def recup_ip():
        try:
                h_name = socket.gethostname()
                IP_addres = socket.gethostbyname(h_name)
                ip = IP_addres.split(".")
                ipadress = ip[0]+"."+ip[1]+"."+ip[2]+".1"
                return ipadress
        except Exception as e:
                print(str(e))

#############################################################################################
#####	Récupérer le nom via SNMP (Unicast)												#####
#############################################################################################
def resolve_snmp_name(ip, timeout=1.0):
    try:
        # SNMPv2c GetRequest community='public' for sysDescr and sysName
        # Packet copied from src/Snyf/send.py
        msg = b'\x30\x34\x02\x01\x01\x04\x06public\xa0\x27\x02\x01\x00\x02\x01\x00\x02\x01\x00\x30\x1c\x30\x0c\x06\x08\x2b\x06\x01\x02\x01\x01\x01\x00\x05\x00\x30\x0c\x06\x08\x2b\x06\x01\x02\x01\x01\x05\x00\x05\x00'
        port = 161
        
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.settimeout(timeout)
            s.sendto(msg, (ip, port))
            
            try:
                data, _ = s.recvfrom(4096)
                if data:
                    # Parsing simple (inspiré de src/Snyf/fct.py)
                    # OID sysName: 1.3.6.1.2.1.1.5.0
                    oid_sysName = b'\x2b\x06\x01\x02\x01\x01\x05\x00'
                    
                    # Chercher l'OID dans la réponse
                    start = data.find(oid_sysName)
                    if start != -1:
                        # Position après l'OID
                        pos = start + len(oid_sysName)
                        if pos < len(data):
                            tag = data[pos]
                            pos += 1
                            if tag == 0x04: # OctetString
                                if pos < len(data):
                                    length = data[pos]
                                    pos += 1
                                    
                                    # Gestion longueur étendue
                                    if length & 0x80:
                                        n_bytes = length & 0x7f
                                        if pos + n_bytes <= len(data):
                                            real_len = int.from_bytes(data[pos:pos+n_bytes], 'big')
                                            pos += n_bytes
                                            length = real_len
                                    
                                    if pos + length <= len(data):
                                        return data[pos:pos+length].decode(errors='ignore')
                                        
                    # Fallback: essayer de trouver une chaîne ASCII lisible si pas de parsing précis
                    # (souvent sysDescr est le premier truc lisible)
                    decoded = ''.join(chr(b) if 32 <= b < 127 else ' ' for b in data)
                    desc = ' '.join(decoded.split())
                    if "public" in desc:
                        desc = desc.split("public")[-1].strip()
                    if desc:
                        return desc
            except socket.timeout:
                pass
                
    except Exception as e:
        # print(f"SNMP Error: {e}")
        pass
        
    return None
