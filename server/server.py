import socket
import threading
import logging
import random
import time
from server.packet_maker import PacketMaker
from server.packet_maker import ServerPacketType, ClientPacketType
from Engine.player import Player
from Engine.gameobject import GameObject
from Engine.chest import Chest
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')


class Server:
    def __init__(self, host='0.0.0.0', port=53333):
        self.host = host or socket.gethostname()
        self.port = port
        self.user_count = 0
        self.client_list = []
        self.players = {}
        self.objects = {}
        self.chests = {}
        self.next_object_id = 100
        self.running = True
        self.object_spawn_thread = threading.Thread(target=self.spawn_items_loop, daemon=True)
        self.object_spawn_thread.start()
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def new_client(self, client_socket, addr):
        logging.info(f"Client connected: {addr}")
        buffer = ""
        try:
            while self.running:
                data = client_socket.recv(1024).decode()
                if not data:
                    break
                buffer += data
                while "\n" in buffer:
                    msg, buffer = buffer.split("\n", 1)
                    self.process_packet(msg)
        except Exception as e:
            logging.error(f"Client error {addr}: {e}")
        finally:
            client_socket.close()
            self.client_list.remove(client_socket)
            logging.info(f"Client disconnected: {addr}")

    def process_packet(self, packet):
        parts = packet.split(":")
        action = int(parts[0])

        if action == ClientPacketType.MOVE_PLAYER:
            player_id, keys = int(parts[1]), parts[2]
            if player_id not in self.players:
                self.players[player_id] = Player(player_id)
            player = self.players.get(player_id)
            if player:
                player.move(keys)
                update_msg = PacketMaker.make(ServerPacketType.MOVE_PLAYER, player_id, x=player.x, y=player.y)
                self.broadcast(update_msg)

        elif action == ClientPacketType.PICKUP_ITEM:
            player_id, object_id = int(parts[1]),int( parts[2])
            player = self.players.get(player_id)
            obj = self.objects.get(object_id)

            if player and obj and obj.held_by is None:
                player.inventory.append(obj)
                obj.held_by = player_id

                update_msg = PacketMaker.make(ServerPacketType.PICKUP_ITEM, player_id, object_id)
                self.broadcast(update_msg)

        elif action == ClientPacketType.DROP_ITEM:
            player_id, object_id = int(parts[1]), int(parts[2])
            player = self.players.get(player_id)
            obj = self.objects.get(object_id)

            if player and obj:
                # Drop the object in front of the player
                obj.x = player.x 
                obj.y = player.y - 50
                obj.held_by = None

                update_msg = PacketMaker.make(
                    ServerPacketType.DROP_ITEM,
                    player_id=player_id,
                    object_id=object_id,
                    x=obj.x,
                    y=obj.y
                )
                self.broadcast(update_msg)

        elif action == ClientPacketType.DESPAWN_ITEM:
            object_id = int(parts[2])  # or adjust if only 2 parts
            if object_id in self.objects:
                del self.objects[object_id]
                print(f"Server: Despawning item {object_id}")
                update_msg = PacketMaker.make(ServerPacketType.DESPAWN_ITEM, object_id=object_id)
                self.broadcast(update_msg)

    def broadcast(self, message):
        for sock in self.client_list:
            sock.send(message.encode())

    def accept_connection(self):
        try:
            client_socket, address = self.server_socket.accept()
            return client_socket, address
        except socket.timeout:
            return None
        
    def spawn_items_loop(self):
        armor_types = [1, 2, 3, 4]  # helmet, chestplate, pants, boots
        screen_width, screen_height = 1280, 720

        while self.running:
        # wait until at least two clients are connected
            while self.running and len(self.client_list) < 2:
                time.sleep(1)

            object_id = self.next_object_id
            self.next_object_id += 1

            x = random.randint(0, screen_width - 40)
            y = random.randint(0, screen_height - 40)
            armor_type = random.choice(armor_types)

            new_obj = GameObject(object_id, x, y, armor_type)
            self.objects[object_id] = new_obj

            packet = PacketMaker.make(
                ServerPacketType.SPAWN_ITEM,
                object_id=object_id,
                x=x,y=y,
                armor_type=armor_type
            )

            self.broadcast(packet)
            logging.info(f"Spawned item {object_id} at ({x},{y})")

            # random item spawns at random x,y every 5 seconds
            time.sleep(5)

    def chest_init(self, chest_id):
        x = 0 if chest_id % 2 == 0 else 1280 - 100
        y = 0 if chest_id < 2 else 720 - 100
        self.chests[chest_id] = Chest(chest_id=chest_id, player_id=chest_id, x=x, y=y)
    
    def player_init(self, player_id):
        x = 200 if player_id % 2 == 0 else 1280 - 200
        y = 200 if player_id < 2 else 720 - 200
        self.players[player_id] = Player(player_id=player_id, x=x, y=y)

    def broadcast_chests(self, count):
        for i in range(count):
            packet = PacketMaker.make(ServerPacketType.SPAWN_CHEST, player_id=i, chest_id=i, x=self.chests[i].x, y=self.chests[i].y)
            self.broadcast(packet)

    def broadcast_players(self, count):
        for i in range(count):
            packet = PacketMaker.make(ServerPacketType.SPAWN_PLAYER, player_id=i, x=self.players[i].x, y=self.players[i].y)
            self.broadcast(packet)


    def start(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(4)
        self.server_socket.settimeout(1.0)
        logging.info(f"Server started on {self.host}:{self.port}")

        try:
            while self.running:
                result = self.accept_connection()
                if result:
                    client_socket, address = result
                    self.client_list.append(client_socket)
                    client_socket.send(str(self.user_count).encode())

                    self.player_init(self.user_count)
                    self.chest_init(self.user_count)

                    self.user_count += 1

                    self.broadcast_players(self.user_count)
                    self.broadcast_chests(self.user_count)

                    threading.Thread(target=self.new_client, daemon=True, args=(client_socket, address)).start()
        except KeyboardInterrupt:
            logging.info("Server interrupt received.")
        finally:
            self.shutdown()

    def shutdown(self):
        logging.info("Shutting down server.")
        self.running = False
        for client in self.client_list:
            client.close()
        self.server_socket.close()

