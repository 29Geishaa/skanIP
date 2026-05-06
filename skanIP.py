import socket
import ipaddress
import os
import subprocess
import time

def get_network(): #komentarz  raz dwa trzy
    # a to jest moj komentarz 4 5 6
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    finally:
        s.close()

    return ipaddress.IPv4Network(ip + "/24", strict=False)

def ping(ip):
    return os.system(f"ping -c 1 -W 1 {ip} > /dev/null 2>&1") == 0

def get_mac(ip):
    try:
        output = subprocess.check_output("ip neigh", shell=True).decode()
        for line in output.split("\n"):
            if ip in line:
                parts = line.split()
                if len(parts) >= 5:
                    return parts[4]
    except:
        pass
    return "N/A"

net = get_network()
print(f"Skanowanie: {net}\n")

for ip in net.hosts():
    ip = str(ip)

    if ping(ip):
        time.sleep(0.05)  
        mac = get_mac(ip)
        print(f"{ip} | MAC: {mac}")