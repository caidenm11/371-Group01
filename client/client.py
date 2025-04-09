import socket
import threading
import client.game as game_var
from enum import IntEnum


# Actions the client sends to server
class ClientPacketType(IntEnum):
    MOVE_PLAYER = 1  # ClientPacketType.MOVE:<Player ID>:<Keys>
    PICKUP_ITEM = 2  # ClientPacketType.PICKUP_ITEM:<Player ID>:<Object ID>
    DROP_ITEM = 3  # ClientPacketType.DROP_ITEM:<Player ID>:<Object ID>
    CHEST_DROP = 4  # ClientPacketType.CHEST_DROP:<Player ID>:<Chest ID>
    DESPAWN_ITEM = 5 


# Actions the client receives from server
class ServerPacketType(IntEnum):
    MOVE_PLAYER = 1  # ServerPacketType.MOVE_PLAYER:<Player ID>:<x>:<y>:<state>
    SPAWN_PLAYER = 2  # ServerPacketType.SPAWN_PLAYER:<Player ID>:<x>:<y>
    PICKUP_ITEM = 3  # ServerPacketType.PICKUP_ITEM:<Player ID>:<Object ID>
    DROP_ITEM = 4  # ServerPacketType.DROP_ITEM:<Player ID>:<Object ID>:<x>:<y>
    SPAWN_ITEM = 5  # ServerPacketType.SPAWN_ITEM:<Object ID>:<x>:<y>:<armor type>
    DESPAWN_ITEM = 6  # ServerPacketType.DESPAWN_ITEM:<Object ID>
    SPAWN_CHEST = 7 # ServerPacketType.SPAWN_CHEST:<Player ID>:<Chest ID>:<x>:<y>
    OBJECT_IN_CHEST = 8 # ServerPacketType.OBJECT_IN_CHEST:<Chest ID>:<Object ID>
    WIN_PLAYER = 9 # ServerPacketType.WIN_PLAYER:<Player ID>


def ServerPacketMaker(action, player_id=None, chest_id=None, object_id=None, keys=None, state=None, armor_type=None):
    packet = [str(action.value)]
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
    if armor_type is not None:
        packet.append(str(armor_type))
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
    try:
        action = int(parts[0])
    except ValueError:
        print(f"Skipping non-packet message: {data}")
        return

    if action == ServerPacketType.MOVE_PLAYER:
        player_id = int(parts[1])
        x = float(parts[2])
        y = float(parts[3])

        if player_id in game_var.players:
            player = game_var.players[player_id]
            player.pos.x = x
            player.pos.y = y
            print(f"Player {player_id} moved to ({x}, {y})")

    elif action == ServerPacketType.SPAWN_PLAYER:
        player_id = int(parts[1])
        x = float(parts[2])
        y = float(parts[3])

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
        armor_type = int(parts[4])

        if object_id not in game_var.objects:
            game_var.objects[object_id] = game_var.GameObject(object_id, x, y, armor_type)
        print(f"Spawned Item {object_id} at ({x}, {y})")

    elif action == ServerPacketType.START_GAME:
        print("[CLIENT] Game start received from server!")
        # Added handling for the START_GAME packet from the game lobby
        game_var.start_game()
    elif action == ServerPacketType.PICKUP_ITEM:
        player_id = int(parts[1])
        object_id = float(parts[2])
        player = game_var.players[player_id]
        held_object = game_var.objects[object_id]

        player.inventory[0] = held_object
        held_object.held_by = player_id
        # held_object.rect.topleft.x = player.x
        # held_object.rect.topleft.y = player.y - 50

    elif action == ServerPacketType.SPAWN_CHEST:
        player_id = int(parts[1])
        chest_id = int(parts[2])
        x = float(parts[3])
        y = float(parts[4])

        # If the chest doesn't exist yet, add it to the dictionary
        if chest_id not in game_var.chests:
            game_var.chests[chest_id] = game_var.Chest(chest_id, x, y)
        print(f"Spawned Chest {chest_id} at ({x}, {y})")

    elif action == ServerPacketType.DROP_ITEM:
        player_id = int(parts[1])
        object_id = float(parts[2])
        x = float(parts[3])
        y = float(parts[4])

        # Update the object's position
        if object_id in game_var.objects:
            game_var.objects[object_id].pos.x = x
            game_var.objects[object_id].pos.y = y
            print(f"Dropped Item {object_id} at ({x}, {y})")
    elif action == ServerPacketType.DESPAWN_ITEM:
        object_id = int(parts[1])
        if object_id in game_var.objects:
            del game_var.objects[object_id]
            print(f"Item {object_id} despawned")


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
    # client_socket.send(message)
    # if client_socket:
    #     try:
    #         data = ServerPacketMaker(ClientPacketType.MOVE_PLAYER, player_id, keys=data)
    #         message = data.encode("utf-8")
    #         client_socket.send(message)
    #     except OSError as e:
    #         print(f"[ERROR] Failed to send movement: {e}")

def send_object_pickup(data):
    data = ServerPacketMaker(ServerPacketType.PICKUP_ITEM, player_id, object_id=data)
    message = data.encode("utf-8")
    client_socket.send(message)

def send_object_drop(data):
    packet = ServerPacketMaker(ClientPacketType.DROP_ITEM, player_id, object_id=data)
    message = packet.encode("utf-8")
    client_socket.send(message)

def send_chest_drop(chest_id, object_id):
    packet = ServerPacketMaker(ClientPacketType.CHEST_DROP, player_id=player_id, chest_id=chest_id, object_id=object_id)
    message = packet.encode("utf-8")
    client_socket.send(message)

def send_item_despawn(object_id):
    packet = ServerPacketMaker(ClientPacketType.DESPAWN_ITEM, player_id=player_id, object_id=object_id)
    message = packet.encode("utf-8")
    client_socket.send(message)

def close_client():
    global client_socket
    client_socket.close()
