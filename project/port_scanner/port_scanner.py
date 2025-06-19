import socket
import threading
import json
from queue import Queue, Empty
import hashlib
import ipaddress
import argparse
import sys
import time
import os
import glob
import importlib.util

# ANSI color codes for output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    RESET = '\033[0m'

COMMON_SERVICES = {
    20: "FTP-data", 21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP",
    53: "DNS", 80: "HTTP", 110: "POP3", 119: "NNTP", 123: "NTP",
    143: "IMAP", 161: "SNMP", 194: "IRC", 443: "HTTPS", 465: "SMTPS",
    587: "SMTP (submission)", 993: "IMAPS", 995: "POP3S", 3306: "MySQL",
    3389: "RDP", 5432: "PostgreSQL", 5900: "VNC", 8080: "HTTP-alt"
}

open_ports = []
closed_ports = []
errors = []

lock = threading.Lock()
PLUGINS = []

def hash_banner(banner):
    return hashlib.sha256(banner.encode()).hexdigest() if banner else ''

def safe_print(*args, **kwargs):
    if not args.silent:
        print(*args, **kwargs)

def print_color(text, color):
    if not args.silent:
        print(f"{color}{text}{Colors.RESET}")

def load_plugins():
    plugin_files = glob.glob(os.path.join('scan_plugins', '*.py'))
    for pf in plugin_files:
        name = os.path.basename(pf)[:-3]
        spec = importlib.util.spec_from_file_location(name, pf)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        if hasattr(mod, 'on_open_port'):
            PLUGINS.append(mod.on_open_port)
    if PLUGINS:
        safe_print(f"Loaded {len(PLUGINS)} plugin(s): {', '.join(p.__module__ for p in PLUGINS)}")

def run_plugins(ip, port, scan_data):
    for plugin in PLUGINS:
        try:
            extra = plugin(ip, port, scan_data)
            if extra:
                scan_data.update(extra)
        except Exception as e:
            with lock:
                print_color(f"Plugin error on {ip}:{port} - {e}", Colors.RED)

def scan_port(target, port):
    try:
        family = socket.AF_INET6 if args.ipv6 else socket.AF_INET
        sock = socket.socket(family, socket.SOCK_STREAM)
        sock.settimeout(1.0)
        result = sock.connect_ex((target, port))
        if result == 0:
            banner = ''
            try:
                sock.sendall(b'\r\n')
                banner = sock.recv(1024).decode(errors='ignore').strip()
            except:
                pass
            service = COMMON_SERVICES.get(port, "")
            banner_hash = hash_banner(banner)
            scan_data = {
                'ip': target,
                'port': port,
                'service': service,
                'banner': banner,
                'banner_hash': banner_hash
            }
            run_plugins(target, port, scan_data)
            with lock:
                print_color(f"[{target}] [+] Port {port} open: {service} {banner} (SHA256: {banner_hash[:8]}...)", Colors.GREEN)
                open_ports.append(scan_data)
        else:
            with lock:
                closed_ports.append({'ip': target, 'port': port})
                if not args.open_only:
                    print_color(f"[{target}] [-] Port {port} closed", Colors.YELLOW)
        sock.close()
    except socket.timeout:
        with lock:
            errors.append({'ip': target, 'port': port, 'error': 'timeout'})
            if not args.open_only:
                print_color(f"[{target}] [!] Port {port} timeout", Colors.RED)
    except Exception as e:
        with lock:
            errors.append({'ip': target, 'port': port, 'error': str(e)})
            if not args.open_only:
                print_color(f"[{target}] [!] Port {port} error: {e}", Colors.RED)

def worker():
    while True:
        try:
            target, port = q.get(timeout=1)
        except Empty:
            break
        scan_port(target, port)
        q.task_done()
        print_progress()

def parse_ip_range(ip_range):
    if '-' in ip_range and not '/' in ip_range:
        base = ip_range.rsplit('.', 1)[0]
        start_end = ip_range.rsplit('.', 1)[1]
        start, end = start_end.split('-')
        start = int(start)
        end = int(end)
        ips = [f"{base}.{i}" for i in range(start, end + 1)]
    else:
        try:
            net = ipaddress.ip_network(ip_range, strict=False)
            ips = [str(ip) for ip in net.hosts()]
        except ValueError:
            ips = [ip_range]
    return ips

def print_progress():
    elapsed = time.time() - start_time
    left = q.qsize()
    done = total_ports - left
    rate = done / elapsed if elapsed > 0 else 0
    eta = left / rate if rate > 0 else float('inf')
    if not args.silent:
        print(f"Ports left: {left} | Elapsed: {elapsed:.1f}s | ETA: {eta:.1f}s    ", end='\r', flush=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Modular Pro Port Scanner')
    parser.add_argument('target', help='Target IP, hostname, or IP range (CIDR or dash range)')
    parser.add_argument('--start-port', type=int, default=1, help='Start port number')
    parser.add_argument('--end-port', type=int, default=1024, help='End port number')
    parser.add_argument('--threads', type=int, default=100, help='Number of threads')
    parser.add_argument('--output', default=None, help='Output JSON filename (default: <target>_scan_results.json)')
    parser.add_argument('--outdir', default='.', help='Output directory (default: current)')
    parser.add_argument('--open-only', action='store_true', help='Show only open ports')
    parser.add_argument('--silent', action='store_true', help='Suppress console output except final summary')
    parser.add_argument('--ipv6', action='store_true', help='Enable IPv6 scanning')
    args = parser.parse_args()

    try:
        targets = parse_ip_range(args.target)
    except Exception as e:
        print_color(f"Invalid target or IP range: {e}", Colors.RED)
        sys.exit(1)

    load_plugins()

    q = Queue()
    total_ports = len(targets) * (args.end_port - args.start_port + 1)
    start_time = time.time()

    safe_print(f"Scanning targets: {targets}")
    safe_print(f"Ports {args.start_port}-{args.end_port}, threads: {args.threads}")

    for _ in range(args.threads):
        t = threading.Thread(target=worker, daemon=True)
        t.start()

    for ip in targets:
        for port in range(args.start_port, args.end_port + 1):
            q.put((ip, port))

    try:
        q.join()
    except KeyboardInterrupt:
        print_color("\nScan interrupted by user. Saving partial results...", Colors.RED)

    duration = time.time() - start_time

    safe_print("\nScan complete.")
    safe_print(f"Duration: {duration:.2f} seconds")
    safe_print(f"Open ports: {len(open_ports)}")
    if not args.open_only:
        safe_print(f"Closed ports: {len(closed_ports)}")
        safe_print(f"Errors: {len(errors)}")

    os.makedirs(args.outdir, exist_ok=True)
    out_file = os.path.join(args.outdir, args.output or f"{args.target}_scan_results.json")

    results = {
        'target': args.target,
        'duration_seconds': duration,
        'open_ports': open_ports,
    }
    if not args.open_only:
        results['closed_ports'] = closed_ports
        results['errors'] = errors

    with open(out_file, 'w') as f:
        json.dump(results, f, indent=4)

    safe_print(f"Results saved to {out_file}")
