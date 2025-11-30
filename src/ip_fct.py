
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
