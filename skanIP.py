import socket
import ipaddress
import subprocess
import json
import sys
import argparse
from concurrent.futures import ThreadPoolExecutor

def detect_network():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ipaddress.IPv4Network(ip + "/24", strict=False)

def is_host_alive(ip, timeout=0.5):
    try:
        command = ["ping", "-c", "1", "-W", str(timeout), str(ip)]
        result = subprocess.run(command, capture_output=True, text=True, shell=False)
        return result.returncode == 0
    except Exception:
        return False

def get_mac(ip):
    try:
        output = subprocess.check_output(["ip", "neigh"], stderr=subprocess.DEVNULL, text=True, shell=False)
        for line in output.split("\n"):
            if str(ip) in line:
                parts = line.split()
                if len(parts) >= 5:
                    return parts[4]
    except:
        pass
    return "N/A"

def format_table(results):
    header = f"{'NR':<4} | {'ADRES IP':<15} | {'STATUS':<6} | {'MAC'}"
    print(header)
    print("-" * len(header))
    for res in results:
        print(f"{res['nr']:<4} | {res['ip']:<15} | {res['status']:<6} | {res['mac']}")

def scan_hosts(net, timeout, json_file=None):
    print(f"Skanowanie sieci: {net}\n")
    
    hosts_to_check = []
    for nr, ip in enumerate(net.hosts(), 1):
        hosts_to_check.append((nr, str(ip), timeout))
    
    results = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        def check(info):
            nr, ip_str, t = info
            if is_host_alive(ip_str, t):
                return {"nr": nr, "ip": ip_str, "status": "UP", "mac": get_mac(ip_str)}
            return {"nr": nr, "ip": ip_str, "status": "DOWN", "mac": "-"}
        
        results = list(executor.map(check, hosts_to_check))

    format_table(results)

    if json_file:
        try:
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=4, ensure_ascii=False)
            print(f"\n[+] Wyniki zapisano do pliku: {json_file}")
        except Exception as e:
            print(f"\nBłąd zapisu JSON: {e}")

def main():
    parser = argparse.ArgumentParser(description="Skaner sieci")
    subparsers = parser.add_subparsers(dest="command")

    scan_parser = subparsers.add_parser("scan")
    scan_parser.add_argument("network", help="Adres sieci CIDR")
    scan_parser.add_argument("--timeout", type=float, default=0.5)
    scan_parser.add_argument("--json", type=str)

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    args = parser.parse_args()

    if args.command == "scan":
        try:
            net = ipaddress.IPv4Network(args.network, strict=False)
            scan_hosts(net, args.timeout, args.json)
        except ValueError:
            print(f"Błąd: Niepoprawny zakres.")
            sys.exit(1)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()