import socket
import threading

def handle_client(client_socket, client_address):
    """Handle communication with a connected client."""
    print(f"Client {client_address} connected.")
    try:
        while True:
            message = client_socket.recv(1024).decode()
            if not message:
                break
            print(f"Message from {client_address}: {message}")
            client_socket.sendall(f"Server received: {message}".encode())
    except Exception as e:
        print(f"Error with client {client_address}: {e}")
    finally:
        client_socket.close()
        print(f"Client {client_address} disconnected.")

def start_server(host="0.0.0.0", port=12345):
    """Start the chat server."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Chat server started on {host}:{port}")

    try:
        while True:
            client_socket, client_address = server_socket.accept()
            client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
            client_thread.start()
    except KeyboardInterrupt:
        print("Shutting down server...")
    finally:
        server_socket.close()

if __name__ == "__main__":
    port = int(input("Enter port to listen on: "))
    start_server(port=port)
