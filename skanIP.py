import socket
import ipaddress
import os

def get_network():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    finally:
        s.close()

    return ipaddress.IPv4Network(ip + "/24", strict=False)

def ping(ip):
    return os.system(f"ping -c 1 -W 1 {ip} > /dev/null 2>&1") == 0

net = get_network()
print(f"Skanowanie: {net}\n")

for ip in net.hosts():
    ip = str(ip)
    if ping(ip):
        print(ip)