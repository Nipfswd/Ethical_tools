import socket

def start_server(host='0.0.0.0', port=12345, protocol='TCP'):
    """Start a server to listen for incoming connections."""
    if protocol.upper() == 'UDP':
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_socket.bind((host, port))
        print(f"UDP server listening on {host}:{port}")
        
        while True:
            data, addr = server_socket.recvfrom(1024)
            print(f"Received from {addr}: {data.decode()}")
    else:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((host, port))
        server_socket.listen(1)
        print(f"TCP server listening on {host}:{port}")
        
        while True:
            conn, addr = server_socket.accept()
            print(f"Connection from {addr}")
            data = conn.recv(1024).decode()
            print(f"Received: {data}")
            conn.sendall(b"Message received")
            conn.close()


def connect_to_server(host, port, message="", protocol='TCP'):
    """Connect to a server and send a message."""
    if protocol.upper() == 'UDP':
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client_socket.sendto(message.encode(), (host, port))
        response, addr = client_socket.recvfrom(1024)
        print(f"Response from {addr}: {response.decode()}")
    else:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, port))
        client_socket.sendall(message.encode())
        response = client_socket.recv(1024).decode()
        print(f"Response: {response}")
        client_socket.close()


if __name__ == "__main__":
    mode = input("Choose mode (server/client): ").strip().lower()
    protocol = input("Choose protocol (TCP/UDP): ").strip().upper()

    if mode == 'server':
        port = int(input("Enter port to listen on: "))
        start_server(protocol=protocol, port=port)
    elif mode == 'client':
        host = input("Enter server IP: ")
        port = int(input("Enter server port: "))
        message = input("Enter message to send: ")
        connect_to_server(host, port, message, protocol=protocol)
    else:
        print("Invalid mode. Choose 'server' or 'client'.")
