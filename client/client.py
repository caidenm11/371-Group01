import socket
import threading
import client.game as game_var

host = socket.gethostname()
port = 53333

client_socket = None

message = None

client_id = 0

def server_listener(client_socket, address):
    while True:
        data = client_socket.recv(1024).decode()
        if not data:
            break
        #client_socket.send("back to you TCP".encode())
        print(str(data))
        # Parse the incoming message
        parts = data.split()
        player_id = int(parts[0])  # Extract player ID (1-based index)
        x = float(parts[1])  # Extract X position
        y = float(parts[2])  # Extract Y position

        # Update the player's position
        if 1 <= player_id <= 4:  # Ensure valid player ID
            game_var.players_pos[player_id - 1].x = x
            game_var.players_pos[player_id - 1].y = y

        print(f"Player {player_id} position updated: {game_var.players_pos[player_id - 1]}")
    
    client_socket.close()

def start_client():
    global client_socket
    global client_id
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    client_id = client_socket.recv(1024).decode()
    #print(client_id)
    client_thread = threading.Thread(target=server_listener, daemon=True, args=(client_socket, None))
    client_thread.start()

def send_key(data):
    global client_socket
    global client_id
    data = str(client_id) + ' ' + data
    message = data.encode("utf-8")
    client_socket.send(message)

def close_client():
    global client_socket
    client_socket.close()