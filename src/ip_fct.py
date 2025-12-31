
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
def ipPing(ip):
        try:
                my_os = platform.system()
                if my_os == "Windows":
                        # Windows: ping -n 1 -w 1000 (1 paquet, timeout 1000ms)
                        # CREATE_NO_WINDOW empêche l'ouverture de fenêtres CMD
                        result = subprocess.run(
                                ["ping", "-n", "1", "-w", "1000", ip],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                timeout=2,
                                creationflags=subprocess.CREATE_NO_WINDOW
                        )
                else:
                        # Linux/Mac: ping -c 1 -W 1 (1 paquet, timeout 1s)
                        result = subprocess.run(
                                ["/bin/ping", "-c", "1", "-W", "1", ip],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                timeout=2
                        )
                
                # Si le code de retour est 0, le ping a réussi
                if result.returncode == 0:
                        return "OK"
                else:
                        return "HS"

        except subprocess.TimeoutExpired:
                return "HS"
        except Exception as inst:
                print(inst)
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
