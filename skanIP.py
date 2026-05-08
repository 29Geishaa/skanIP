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
    
    found_any = False
    for res in results:
        if res['status'] == "UP":
            print(f"{res['nr']:<4} | {res['ip']:<15} | {res['status']:<6} | {res['mac']}")
            found_any = True
            
    if not found_any:
        print("Nie znaleziono aktywnych urządzeń w podanym zakresie.")

def scan_hosts(net, timeout):
    hosts_to_check = []
    for nr, ip in enumerate(net.hosts(), 1):
        hosts_to_check.append((nr, str(ip), timeout))
    
    results = []
    with ThreadPoolExecutor(max_workers=30) as executor:
        def check(info):
            nr, ip_str, t = info
            if is_host_alive(ip_str, t):
                return {"nr": nr, "ip": ip_str, "status": "UP", "mac": get_mac(ip_str)}
            return {"nr": nr, "ip": ip_str, "status": "DOWN", "mac": "-"}
        
        results = list(executor.map(check, hosts_to_check))
    return results

def main():
    parser = argparse.ArgumentParser(description="Skaner sieci zgodny z TASKS.md")
    subparsers = parser.add_subparsers(dest="command")

    scan_parser = subparsers.add_parser("scan")
    scan_parser.add_argument("network", nargs='?', help="Adres sieci CIDR (np. 192.168.1.0/24)")
    scan_parser.add_argument("--timeout", type=float, default=0.4)
    scan_parser.add_argument("--json", type=str)

    args = parser.parse_args()

    if args.command == "scan":
        target_net = args.network
        if not target_net:
            target_net = str(detect_network())
        
        try:
            net = ipaddress.IPv4Network(target_net, strict=False)
            print(f"Skanowanie sieci: {net} \n")
            
            results = scan_hosts(net, args.timeout)
            format_table(results)

            if args.json:
                with open(args.json, 'w', encoding='utf-8') as f:
                    json.dump(results, f, indent=4, ensure_ascii=False)
                print(f"\n[+] Pełny raport zapisano do: {args.json}")
                
        except ValueError:
            print("Błąd: Niepoprawny format sieci.")
            sys.exit(1)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()