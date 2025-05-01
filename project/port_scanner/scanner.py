import socket

def scan_ports(target, port_range=(1, 65535)):
    """Scan for open ports on the target system."""
    open_ports = []
    print(f"Scanning ports on {target}...")
    
    for port in range(port_range[0], port_range[1] + 1):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)  # Set timeout for connection
                if s.connect_ex((target, port)) == 0:
                    print(f"Port {port} is open.")
                    open_ports.append(port)
        except Exception as e:
            print(f"Error scanning port {port}: {e}")

    return open_ports


if __name__ == "__main__":
    target = input("Enter the target IP address or hostname: ")
    port_range = (1, 1000)  # Customize port range
    open_ports = scan_ports(target, port_range)
    if open_ports:
        print(f"Open ports: {open_ports}")
    else:
        print("No open ports found.")
