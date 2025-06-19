# scan_plugins/reverse_dns.py

import socket

def on_open_port(ip, port, scan_data):
    try:
        hostname, _, = socket.gethostbyaddr(ip)
        return {'hostname': hostname}
    except socket.herror:
        return {}