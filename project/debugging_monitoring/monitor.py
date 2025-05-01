import socket

def connect_to_service(target, port, message=""):
    """Connect to a service, send a message, and observe the response."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5)  # Timeout for connection
            print(f"Connecting to {target}:{port}...")
            s.connect((target, port))
            print(f"Connected to {target}:{port}")
            
            if message:
                print(f"Sending message: {message}")
                s.sendall(message.encode())
            
            response = s.recv(4096).decode()
            print(f"Response from {target}:{port}: {response}")
            return response
    except Exception as e:
        print(f"Error: {e}")
        return None


if __name__ == "__main__":
    target = input("Enter the target IP address or hostname: ")
    port = int(input("Enter the target port: "))
    message = input("Enter the message to send (leave blank for no message): ")
    connect_to_service(target, port, message)
