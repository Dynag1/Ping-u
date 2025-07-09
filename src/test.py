import socket

msg = (
    'M-SEARCH * HTTP/1.1\r\n'
    'HOST: 239.255.255.250:1900\r\n'
    'MAN: "ssdp:discover"\r\n'
    'MX: 1\r\n'
    'ST: ssdp:all\r\n'
    '\r\n'
).encode('ascii')

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
s.settimeout(5)
s.bind(('', 1900))  # Essaye aussi ('', 0) si 1900 est déjà pris

try:
    s.sendto(msg, ('239.255.255.250', 1900))
except OSError as e:
    print(f"Erreur d'envoi : {e}")
    s.close()
    exit()

try:
    while True:
        data, addr = s.recvfrom(4096)
        print(f"Réponse de {addr}: {data[:100]!r}")
except socket.timeout:
    print("Fin de l'écoute.")
finally:
    s.close()
