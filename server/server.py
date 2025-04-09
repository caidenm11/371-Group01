import socket
import threading
import logging
import random
import time
import math
from server.packet_maker import PacketMaker
from server.packet_maker import ServerPacketType, ClientPacketType
from Engine.player import Player
from Engine.chest import Chest
from Engine.gameobject import GameObject
from server.broadcast_announcer import start_broadcast, get_local_ip
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')


class Server:
    def __init__(self, host='0.0.0.0', port=53333):
        self.host = host or socket.gethostname()
        self.port = port
        self.user_count = 0
        self.client_list = []
        self.players = {}
        self.player_names = []
        self.objects = {}
        self.chests = {}
        self.client_name_map = {}
        self.next_object_id = 100
        self.running = True
        self.object_spawn_thread = threading.Thread(target=self.spawn_items_loop, daemon=True)
        self.object_spawn_thread.start()
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.object_locks = {}

    def is_near_chest(self, obj, chest, chest_size=100, obj_size=50, radius=60):
        """
        Checks if the object's center is within `radius` pixels of the chest's center.
        """
        chest_center_x = chest.x + chest_size // 2
        chest_center_y = chest.y + chest_size // 2

        obj_center_x = obj.x + obj_size // 2
        obj_center_y = obj.y + obj_size // 2

        dx = chest_center_x - obj_center_x
        dy = chest_center_y - obj_center_y
        distance = math.hypot(dx, dy)

        return distance < radius

    def new_client(self, client_socket, addr, role):
        logging.info(f"Client connected: {addr}")
        try:
            # player_name = client_socket.recv(1024).decode().strip()
            # if not player_name:
            #     logging.warning("Empty player name received, closing connection")
            #     client_socket.close()
            #     return
            #
            # self.client_list.append(client_socket)
            # self.client_name_map[client_socket] = player_name
            # self.player_names.append(player_name)
            #
            # threading.Thread(target=self.handle_client, daemon=True, args=(client_socket, addr)).start()
            # self.broadcast_player_list()
            if role == "lobby":
                player_name = client_socket.recv(1024).decode().strip()
            else:
                # For game clients, assign a default name automatically.
                player_name = f"Player_{self.user_count - 1}"

            self.client_list.append(client_socket)
            self.client_name_map[client_socket] = player_name
            self.player_names.append(player_name)

            # Start listening for further data from the client.
            threading.Thread(target=self.handle_client, daemon=True, args=(client_socket, addr)).start()
            self.broadcast_player_list()

        except Exception as e:
            logging.error(f"Initial client setup error {addr}: {e}")

    def handle_client(self, client_socket, addr):
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
            if client_socket in self.client_list:
                self.client_list.remove(client_socket)
            if client_socket in self.client_name_map:
                name = self.client_name_map.pop(client_socket)
                if name in self.player_names:
                    self.player_names.remove(name)
            self.broadcast_player_list()

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
        elif action == ClientPacketType.REQUEST_START_GAME:
            logging.info("Received game start request. Broadcasting to all clients.")

            # self.broadcast_players()
            # self.broadcast_chests()

            start_msg = PacketMaker.make(ServerPacketType.START_GAME)
            self.broadcast(start_msg)
        elif action == ClientPacketType.PICKUP_ITEM:
            player_id, object_id = int(parts[1]),int( parts[2])
            player = self.players.get(player_id)
            obj = self.objects.get(object_id)

            lock = self.object_locks.get(object_id)
            if player and obj and lock:
                with lock:
                    if obj.held_by is None:
                        player.inventory.append(obj)
                        obj.held_by = player_id

                        update_msg = PacketMaker.make(ServerPacketType.PICKUP_ITEM, player_id, object_id)
                        self.broadcast(update_msg)

        elif action == ClientPacketType.DROP_ITEM:
            player_id, object_id = int(parts[1]), int(parts[2])
            player = self.players.get(player_id)
            obj = self.objects.get(object_id)
            chest = self.chests.get(player_id)

            if player and obj:
                # Drop the object in front of the player
                obj.x = player.x 
                obj.y = player.y - 50
                obj.held_by = None

                if self.is_near_chest(obj, chest):
                    print(f"Object {object_id} is close enough to chest {player_id}")

                    # Check if the chest doesn't already have the object
                    if obj.armor_type not in [o.armor_type for o in chest.stored_items.values()]:
                        chest.stored_items[object_id] = obj

                    obj.held_by = None
                    player.inventory = [o for o in player.inventory if o.object_id != object_id]

                    # Remove from world
                    if object_id in self.objects:
                        del self.objects[object_id]
                    
                    # Notify clients about the collection
                    msg = PacketMaker.make(ServerPacketType.OBJECT_IN_CHEST, chest_id=player_id, object_id=object_id)
                    self.broadcast(msg)

                    despawn_msg = PacketMaker.make(ServerPacketType.DESPAWN_ITEM, object_id=object_id)
                    self.broadcast(despawn_msg)

                    if len(chest.stored_items) == 4:
                        # Notify the player that they won
                        print(f"Player {player_id} has won the game!")
                        win_msg = PacketMaker.make(ServerPacketType.WIN_PLAYER, player_id=player_id)
                        self.broadcast(win_msg)

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

    def heartbeat_loop(self, interval=5):
        # This function sends a heartbeat message to all clients to check if they are still connected
        while self.running:
            to_remove = []
            for sock in self.client_list[:]:
                try:
                    sock.sendall(b"__heartbeat__\n")
                except Exception as e:
                    logging.warning(f"Heartbeat failed, removing client: {e}")
                    to_remove.append(sock)

            for sock in to_remove:
                if sock in self.client_list:
                    self.client_list.remove(sock)
                if sock in self.client_name_map:
                    name = self.client_name_map.pop(sock)
                    if name in self.player_names:
                        self.player_names.remove(name)
            if to_remove:
                self.broadcast_player_list()

            threading.Event().wait(interval)

    def broadcast_player_list(self):
        # Broadcast the list of players to all clients
        message = ",".join(self.player_names) + "\n"
        logging.info(f"[Broadcasting] Player list: {message}")
        for sock in self.client_list:
            try:
                sock.sendall(message.encode())
            except Exception as e:
                logging.warning(f"Failed to send player list: {e}")

        

        # if action == ClientPacketType.SPAWN_ITEM:
        #     player_id, object_id = int(parts[1]), parts[2]
        #     object = self.objects.get(object_id)
        #     if object:
        #         update_msg = PacketMaker.make(ServerPacketType.PICKUP_ITEM, player_id, object_id, x=player.x, y=player.y - 50)
        #         self.broadcast(update_msg)

    def broadcast(self, message):
        # Broadcast a message to all clients
        for sock in self.client_list:
            try:
                sock.send(message.encode())
            except:
                pass

    def accept_connection(self):
        try:
            client_socket, address = self.server_socket.accept()
            return client_socket, address
        except socket.timeout:
            return None
        
    def chest_init(self, chest_id):
        x = 0 if chest_id % 2 == 0 else 1280 - 100
        y = 0 if chest_id < 2 else 720 - 100
        self.chests[chest_id] = Chest(chest_id=chest_id, player_id=chest_id, x=x, y=y)
        print(f"Adding chest: {chest_id} at position ({x}, {y})")
    
    def player_init(self, player_id):
        x = 200 if player_id % 2 == 0 else 1280 - 200
        y = 200 if player_id < 2 else 720 - 200
        self.players[player_id] = Player(player_id=player_id, x=x, y=y)
        print(f"Adding player: {player_id} at position ({x}, {y})")

    def broadcast_chests(self):
        for i in range(self.user_count):
            packet = PacketMaker.make(ServerPacketType.SPAWN_CHEST, player_id=i, chest_id=i, x=self.chests[i].x, y=self.chests[i].y)
            print("Boadcast chest: " + packet)
            self.broadcast(packet)

    def broadcast_players(self):
        for i in range(self.user_count):
            packet = PacketMaker.make(ServerPacketType.SPAWN_PLAYER, player_id=i, x=self.players[i].x, y=self.players[i].y)
            print("Boadcast player: " + packet)
            self.broadcast(packet)
        
    def _connection_loop(self):
        try:
            while self.running:
                result = self.accept_connection()
                if result:
                    client_socket, address = result

                    # Receive role string: 'lobby' or 'game'
                    role = client_socket.recv(1024).decode().strip()
                    print(f"[SERVER] Connection from {address} with role: {role}")

                    if role == "game":
                        client_socket.send(str(self.user_count).encode())

                        self.player_init(self.user_count)
                        self.chest_init(self.user_count)

                        print("user_count: " + str(self.user_count))

                        self.user_count += 1

                    # Start the client listener thread regardless of role
                    # threading.Thread(target=self.new_client, daemon=True, args=(client_socket, address)).start()
                    # NO
                    threading.Thread(target=self.new_client, daemon=True, args=(client_socket, address, role)).start()

        except Exception as e:
            logging.error(f"Connection loop error: {e}")
        finally:
            self.shutdown()
        
    def spawn_items_loop(self):
        armor_types = [1, 2, 3, 4]  # helmet, chestplate, pants, boots
        screen_width, screen_height = 1280, 720

        while self.running:
        # wait until at least two clients are connected
            while self.running and len(self.client_list) < 2:
                time.sleep(1)

            object_id = self.next_object_id
            self.object_locks[object_id] = threading.Lock()
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

            self.broadcast_players()
            self.broadcast_chests()

            # random item spawns at random x,y every 5 seconds
            time.sleep(5)

    # def start(self):
    #     self.server_socket.bind((self.host, self.port))
    #     self.server_socket.listen(4)
    #     self.server_socket.settimeout(1.0)
    #     logging.info(f"Server started on {self.host}:{self.port}")

    #     try:
    #         while self.running:
    #             result = self.accept_connection()
    #             if result:
    #                 client_socket, address = result
    #                 client_socket.send(str(self.user_count).encode())

    #                 self.player_init(self.user_count)
    #                 self.chest_init(self.user_count)

    #                 self.user_count += 1

    #                 threading.Thread(target=self.new_client, daemon=True, args=(client_socket, address)).start()
    #     except Exception as e:
    #         logging.error(f"Connection loop error: {e}")
    #     finally:
    #         self.shutdown()

    def start(self):
        while True:
            try:
                self.server_socket.bind((self.host, self.port))
                break
            except OSError:
                logging.warning(f"Port {self.port} in use. Trying {self.port + 1}")
                self.port += 1

        self.server_socket.listen(4)
        self.server_socket.settimeout(1.0)
        logging.info(f"Server started on {self.host}:{self.port}")

        display_ip = get_local_ip()
        # This sends the broadcast to the local network so when you press refresh, you can find this packet and display the server.
        start_broadcast(display_ip, self.port, len(self.players), 8, "LAN Party")

        threading.Thread(target=self._connection_loop, daemon=True).start()
        threading.Thread(target=self.heartbeat_loop, daemon=True).start()

    def shutdown(self):
        logging.info("Shutting down server.")
        self.running = False
        for client in self.client_list:
            client.close()
        self.server_socket.close()
   

