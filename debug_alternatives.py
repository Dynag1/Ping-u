
import socket
ip = "192.168.2.136"

print(f"Testing getnameinfo for {ip}")
try:
    # 0 = nothing
    res = socket.getnameinfo((ip, 0), 0)
    print(f"Result: {res}")
except Exception as e:
    print(f"Error: {e}")

print("\nTesting zeroconf...")
try:
    import zeroconf
    print("zeroconf is available")
except ImportError:
    print("zeroconf is NOT available")
