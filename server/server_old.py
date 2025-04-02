import socket
import threading
import logging
from enum import IntEnum

from Engine.player import Player


# Actions that server receives from clients
class ClientPacketType(IntEnum):
    MOVE_PLAYER = 1  # ClientPacketType.MOVE:<Player ID>:<Keys>
    PICKUP_ITEM = 2  # ClientPacketType.PICKUP_ITEM:<Player ID>:<Object ID>
    DROP_ITEM = 3  # ClientPacketType.DROP_ITEM:<Player ID>:<Object ID>


# Actions that server sends to clients
class ServerPacketType(IntEnum):
    MOVE_PLAYER = 1  # ServerPacketType.MOVE_PLAYER:<Player ID>:<x>:<y>:<state>
    SPAWN_PLAYER = 2  # ServerPacketType.SPAWN_PLAYER:<Player ID>:<x>:<y>
    PICKUP_ITEM = 3  # ServerPacketType.PICKUP_ITEM:<Player ID>:<Object ID>
    DROP_ITEM = 4  # ServerPacketType.DROP_ITEM:<Player ID>:<Object ID>:<x>:<y>
    SPAWN_ITEM = 5  # ServerPacketType.SPAWN_ITEM:<Object ID>:<x>:<y>
    DESPAWN_ITEM = 6  # ServerPacketType.DESPAWN:<Object ID>


# For making packets to send to client
def ClientPacketMaker(action, player_id=None, object_id=None, x=None, y=None, state=None):
    packet = [str(action)]
    if player_id is not None:
        packet.append(str(player_id))
    if object_id is not None:
        packet.append(str(object_id))
    if x is not None and y is not None:
        packet.append(str(x))
        packet.append(str(y))
    if state is not None:
        packet.append(str(state))
    return ":".join(packet) + "\n"  # Append delimiter


user_count = 0
client_list = []

# Game state should be moved to another file but could probably stay here for now
players = {}  # {player_id: Player instance}
objects = {}  # {object_id: GameObject instance}
next_object_id = 100  # Starting ID for objects


def buffered_recv(socket):
    buffer = ""
    while True:
        data = socket.recv(1024).decode()
        if not data:
            break
        buffer += data
        while "\n" in buffer:  # Process only full messages
            msg, buffer = buffer.split("\n", 1)
            yield msg


def new_client(client_socket, addr):
    global client_list
    logging.info(f"New client connected: {addr}")
    while True:
        data = client_socket.recv(1024).decode()
        if not data:
            break
        # client_socket.send("back to you TCP".encode())
        logging.info(str(data))
        # print(str(data))
        for socket in client_list:
            if socket != client_socket:
                socket.send(data.encode())

    client_socket.close()


# Server-side spawning of a player
def spawn_player(player_id, x, y):
    # Spawn the player and send the spawn packet to all clients
    players[player_id] = Player(player_id, x, y)
    ClientPacketMaker(ServerPacketType.SPAWN_PLAYER, player_id, x=x, y=y)


# Server-side spawning of an item
def spawn_item(object_id, x, y):
    # Spawn the item and send the spawn packet to all clients
    objects[object_id] = GameObject(object_id, x, y)
    ClientPacketMaker(ServerPacketType.SPAWN_ITEM, object_id, x=x, y=y)


# Server-side despawning of an item
def despawn_item(object_id):
    # Remove the object and send the despawn packet to all clients
    if object_id in objects:
        del objects[object_id]
        ClientPacketMaker(ServerPacketType.DESPAWN_ITEM, object_id=object_id)


# Process incoming packets
def process_packet(data):
    global next_object_id

    packets = data.split("\n")

    for packet in packets:
        if not packet:
            continue

        print(f"Received packet: {packet}")
        parts = packet.split(":")
        action = int(parts[0])

        if action == ClientPacketType.MOVE_PLAYER:
            player_id = int(parts[1])
            keys = parts[2]

            # Ensure player exists
            if player_id not in players:
                players[player_id] = Player(player_id)

            players[player_id].move(keys)

            # Send updated position to all clients
            update_msg = ClientPacketMaker(ServerPacketType.MOVE_PLAYER, player_id, x=players[player_id].x,
                                           y=players[player_id].y)
            for socket in client_list:
                socket.send(update_msg.encode())

        elif action == ClientPacketType.PICKUP_ITEM:
            player_id = int(parts[1])
            object_id = int(parts[2])

            if player_id in players and object_id in objects:
                obj = objects[object_id]
                if obj.held_by is None:  # Ensure it's not already picked up
                    obj.held_by = player_id
                    players[player_id].inventory.append(object_id)

                    # Notify all clients
                    update_msg = ClientPacketMaker(ServerPacketType.PICKUP_ITEM, player_id, object_id)
                    for socket in client_list:
                        socket.send(update_msg.encode())

        elif action == ClientPacketType.DROP_ITEM:
            player_id = int(parts[1])
            object_id = int(parts[2])

            if player_id in players and object_id in objects:
                obj = objects[object_id]
                if obj.held_by == player_id:
                    obj.held_by = None
                    players[player_id].inventory.remove(object_id)

                    # Notify all clients
                    update_msg = ClientPacketMaker(ServerPacketType.DROP_ITEM, player_id, object_id,
                                                   x=players[player_id].x, y=players[player_id].y)
                    for socket in client_list:
                        socket.send(update_msg.encode())

        else:
            print(f"Unknown packet type: {action}")


def start_server():
    global user_count
    host = socket.gethostname()
    port = 53333

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(4)

    while True:
        client_socket, address = server_socket.accept()

        print("Client address: " + str(address))
        client_list.append(client_socket)
        client_socket.send(str(user_count).encode())
        user_count += 1
        client_thread = threading.Thread(target=new_client, daemon=True, args=(client_socket, address))
        client_thread.start()
