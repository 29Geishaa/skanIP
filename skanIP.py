import socket
import ipaddress
import os
import subprocess
import time
import argparse
import json
from concurrent.futures import ThreadPoolExecutor

def get_network():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ipaddress.IPv4Network(ip + "/24", strict=False)

def ping(ip, timeout=1):
    return os.system(f"ping -c 1 -W {timeout} {ip} > /dev/null 2>&1") == 0

def get_mac(ip):
    try:
        output = subprocess.check_output("ip neigh", shell=True, stderr=subprocess.DEVNULL).decode()
        for line in output.split("\n"):
            if ip in line:
                parts = line.split()
                if len(parts) >= 5:
                    return parts[4]
    except:
        pass
    return "N/A"

def check_host(ip_info):
    nr, ip_str, timeout = ip_info
    if ping(ip_str, timeout):
        mac = get_mac(ip_str)
        return {"nr": nr, "ip": ip_str, "status": "UP", "mac": mac}
    else:
        return {"nr": nr, "ip": ip_str, "status": "DOWN", "mac": "-"}

def scan_network(net, timeout, json_file=None):
    print(f"Skanowanie sieci: {net}\n")
    
    header = f"{'NR':<4} | {'ADRES IP':<15} | {'STATUS':<6} | {'MAC'}"
    print(header)
    print("-" * len(header))

    hosts_to_check = [(nr, str(ip), timeout) for nr, ip in enumerate(net.hosts(), 1)]
    results = []

    with ThreadPoolExecutor(max_workers=1) as executor:
        for result in executor.map(check_host, hosts_to_check):
            results.append(result)
            print(f"{result['nr']:<4} | {result['ip']:<15} | {result['status']:<6} | {result['mac']}")

    if json_file:
        try:
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=4, ensure_ascii=False)
            print(f"\n[+] Wyniki zapisano do pliku: {json_file}")
        except Exception as e:
            print(f"\n[!] Błąd zapisu JSON: {e}")

def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")

    scan_parser = subparsers.add_parser("scan")
    scan_parser.add_argument("network")
    scan_parser.add_argument("--timeout", type=float, default=0.5)
    scan_parser.add_argument("--json", type=str)

    args = parser.parse_args()

    if args.command == "scan":
        try:
            net = ipaddress.IPv4Network(args.network, strict=False)
            scan_network(net, args.timeout, args.json)
        except ValueError as e:
            print(f"Błąd: {e}")

if __name__ == "__main__":
    main()