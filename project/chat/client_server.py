import socket
import threading

def receive_messages(client_socket):
    """Receive messages from the server."""
    while True:
        try:
            message = client_socket.recv(1024).decode()
            if not message:
                break
            print(f"Server: {message}")
        except Exception as e:
            print(f"Error receiving messages: {e}")
            break

def start_client(server_host, server_port):
    """Start the chat client."""
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_host, server_port))
    print(f"Connected to chat server at {server_host}:{server_port}")

    # Start a thread to receive messages
    receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
    receive_thread.start()

    try:
        while True:
            message = input("You: ")
            if message.lower() == "exit":
                break
            client_socket.sendall(message.encode())
    except KeyboardInterrupt:
        print("Exiting chat...")
    finally:
        client_socket.close()

if __name__ == "__main__":
    server_host = input("Enter server IP: ")
    server_port = int(input("Enter server port: "))
    start_client(server_host, server_port)
