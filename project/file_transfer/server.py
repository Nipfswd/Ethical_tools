import socket
import os

def start_server(host='0.0.0.0', port=12345):
    """Start the file transfer server."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)

    print(f"Server started on {host}:{port}")
    while True:
        conn, addr = server_socket.accept()
        print(f"Connection from {addr}")
        with conn:
            file_name = conn.recv(1024).decode()
            if not file_name:
                break
            print(f"Receiving file: {file_name}")

            with open(file_name, 'wb') as f:
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    f.write(data)
            print(f"File {file_name} received.")

if __name__ == "__main__":
    start_server()
