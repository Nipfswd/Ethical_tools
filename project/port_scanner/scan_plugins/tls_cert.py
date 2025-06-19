# scan_plugins/tls_cert.py

import socket
import ssl

def on_open_port(ip, port, scan_data):
    ssl_ports = {443, 8443, 9443}
    if port not in ssl_ports:
        return {}

    try:
        context = ssl.create_default_context()
        with socket.create_connection((ip, port), timeout=2) as sock:
            with context.wrap_socket(sock, server_hostname=ip) as ssock:
                cert = ssock.getpeercert()
                subject = dict(x[0] for x in cert['subject'])
                cn = subject.get('commonName', '')
                return {'tls_cert_cn': cn}
    except Exception:
        return {}
