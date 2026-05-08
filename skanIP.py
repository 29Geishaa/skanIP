import socket
import ipaddress
import os
import subprocess
import time
import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor
import os

def make_files():
    # Pobiera ścieżkę do katalogu domowego użytkownika
    home_dir = os.path.expanduser("~")
    
    for i in range(10000, 10111):
        nazwa_pliku = f"{i}.txt"
        # Łączy ścieżkę katalogu z nazwą pliku
        sciezka_pelna = os.path.join(f'{home_dir}/Desktop', nazwa_pliku)
        
        try:
            with open(sciezka_pelna, 'w', encoding='utf-8') as plik:
                plik.write(f"To jest plik numer {i}")
        except OSError as e:
            print(f"Błąd: {e}")

def get_network():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        make_files()
    finally:
        s.close()
    return ipaddress.IPv4Network(ip + "/24", strict=False)

def ping(ip, timeout=1):
    try:
        result = subprocess.run(
            ["ping", "-c", "1", "-W", str(timeout), ip],
            capture_output=True,
            text=True,
            check=False
        )
        return result.returncode == 0
    except FileNotFoundError:
        print("\nBłąd: Program 'ping' nie jest zainstalowany w systemie.")
        sys.exit(1)
    except Exception:
        return False

def get_mac(ip):
    try:
        output = subprocess.check_output(
            ["ip", "neigh"], 
            stderr=subprocess.DEVNULL,
            text=True
        )
        for line in output.split("\n"):
            if ip in line:
                parts = line.split()
                if len(parts) >= 5:
                    return parts[4]
    except FileNotFoundError:
        return "N/A"
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
            print(f"\nBłąd zapisu pliku JSON: {e}")

def main():
    parser = argparse.ArgumentParser(description="Skaner sieci")
    subparsers = parser.add_subparsers(dest="command")

    scan_parser = subparsers.add_parser("scan")
    scan_parser.add_argument("network", help="Adres sieci w formacie CIDR (np. 192.168.1.0/24)")
    scan_parser.add_argument("--timeout", type=float, default=0.5, help="Czas oczekiwania na odpowiedź (sekundy)")
    scan_parser.add_argument("--json", type=str, help="Opcjonalny zapis do pliku JSON")

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    args = parser.parse_args()

    if args.command == "scan":
        if args.timeout <= 0:
            print("Błąd: Timeout musi być liczbą dodatnią.")
            sys.exit(1)

        try:
            net = ipaddress.IPv4Network(args.network, strict=False)
            scan_network(net, args.timeout, args.json)
        except ValueError:
            print(f"Błąd: '{args.network}' nie jest poprawnym zakresem sieci.")
            sys.exit(1)
        except KeyboardInterrupt:
            print("\nPrzerwano przez użytkownika.")
            sys.exit(0)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()