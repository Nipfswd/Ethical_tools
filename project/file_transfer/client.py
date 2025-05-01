import socket
import os

def send_file(server_host, server_port, file_path):
    """Send a file to the server."""
    if not file_path or not os.path.exists(file_path):
        print("Invalid file path.")
        return

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((server_host, server_port))
        client_socket.sendall(os.path.basename(file_path).encode())

        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(1024), b''):
                client_socket.sendall(chunk)

        print(f"File {file_path} sent to {server_host}:{server_port}.")

if __name__ == "__main__":
    server_host = input("Enter the server IP address: ")
    server_port = int(input("Enter the server port: "))
    file_path = input("Enter the file path to send: ")
    send_file(server_host, server_port, file_path)
