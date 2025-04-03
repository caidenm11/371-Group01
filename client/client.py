import socket
import threading
import client.game as game_var
from enum import IntEnum


# Actions the client sends to server
class ClientPacketType(IntEnum):
    MOVE_PLAYER = 1  # ClientPacketType.MOVE:<Player ID>:<Keys>
    PICKUP_ITEM = 2  # ClientPacketType.PICKUP_ITEM:<Player ID>:<Object ID>
    DROP_ITEM = 3  # ClientPacketType.DROP_ITEM:<Player ID>:<Object ID>


# Actions the client receives from server
class ServerPacketType(IntEnum):
    MOVE_PLAYER = 1  # ServerPacketType.MOVE_PLAYER:<Player ID>:<x>:<y>:<state>
    SPAWN_PLAYER = 2  # ServerPacketType.SPAWN_PLAYER:<Player ID>:<x>:<y>
    PICKUP_ITEM = 3  # ServerPacketType.PICKUP_ITEM:<Player ID>:<Object ID>
    DROP_ITEM = 4  # ServerPacketType.DROP_ITEM:<Player ID>:<Object ID>:<x>:<y>
    SPAWN_ITEM = 5  # ServerPacketType.SPAWN_ITEM:<Object ID>:<x>:<y>
    DESPAWN_ITEM = 6  # ServerPacketType.DESPAWN_ITEM:<Object ID>
    SPAWN_CHEST = 7 # ServerPacketType.SPAWN_CHEST:<Player ID>:<Chest ID>:<x>:<y>


def ServerPacketMaker(action, player_id=None, chest_id=None, object_id=None, keys=None, state=None):
    packet = [str(action)]
    if player_id is not None:
        packet.append(str(player_id))
    if chest_id is not None:
        packet.append(str(chest_id))
    if object_id is not None:
        packet.append(str(object_id))
    if keys is not None:
        packet.append(str(keys))
    if state is not None:
        packet.append(str(state))
    return ":".join(packet) + "\n"  # Append delimiter for TCP streaming


host = socket.gethostname()
port = 53333

client_socket = None

message = None

player_id = 0


def buffered_recv(sock):
    buffer = ""
    while True:
        try:
            data = sock.recv(1024).decode()
            if not data:
                break
            buffer += data
            while "\n" in buffer:
                msg, buffer = buffer.split("\n", 1)
                yield msg
        except ConnectionResetError:
            print("Connection reset by peer.")
            break
        except Exception as e:
            print(f"Socket error: {e}")
            break


def server_listener(client_socket, address):
    for message in buffered_recv(client_socket):
        print(f"Received: {message}")
        process_packet(message)

    client_socket.close()


def process_packet(data):
    parts = data.split(":")
    action = int(parts[0])  # Packet type

    if action == ServerPacketType.MOVE_PLAYER:
        player_id = int(parts[1])
        x = float(parts[2])
        y = float(parts[3])

        # Ensure valid player ID exists in the dictionary
        if player_id in game_var.players:
            game_var.players[player_id].pos.x = x
            game_var.players[player_id].pos.y = y
            print(f"Player {player_id} moved to ({x}, {y})")

    elif action == ServerPacketType.SPAWN_PLAYER:
        player_id = int(parts[1])
        x = float(parts[2])
        y = float(parts[3])

        # If the player doesn't exist yet, add them to the dictionary
        if player_id not in game_var.players:
            game_var.players[player_id] = game_var.Player(player_id, x, y)
        else:
            game_var.players[player_id].pos.x = x
            game_var.players[player_id].pos.y = y

        print(f"Spawned Player {player_id} at ({x}, {y})")

    elif action == ServerPacketType.SPAWN_ITEM:
        object_id = int(parts[1])
        x = float(parts[2])
        y = float(parts[3])

        # Add the new object to the dictionary
        if object_id not in game_var.objects:
            game_var.objects[object_id] = game_var.GameObject(object_id, x, y)
        print(f"Spawned Item {object_id} at ({x}, {y})")

    else:
        print(f"Unknown packet type: {action}")


def start_client(host="0.0.0.0", port=53333):
    global client_socket
    global player_id
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    print(f"[CLIENT] Connected from local socket: {client_socket.getsockname()}")

    player_id = client_socket.recv(1024).decode()
    # print(client_id)
    client_thread = threading.Thread(target=server_listener, daemon=True, args=(client_socket, None))
    client_thread.start()




def send_key(data):
    global client_socket
    global player_id
    data = ServerPacketMaker(ServerPacketType.MOVE_PLAYER, player_id, keys=data)
    message = data.encode("utf-8")
    client_socket.send(message)


def close_client():
    global client_socket
    client_socket.close()
