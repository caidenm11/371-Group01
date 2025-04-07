import socket
import threading
import logging
from server.packet_maker import PacketMaker
from server.packet_maker import ServerPacketType, ClientPacketType
from Engine.player import Player
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
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def new_client(self, client_socket, addr):
        logging.info(f"Client connected: {addr}")
        try:
            player_name = client_socket.recv(1024).decode().strip()
            if not player_name:
                logging.warning("Empty player name received, closing connection")
                client_socket.close()
                return

            self.client_list.append(client_socket)
            self.client_name_map[client_socket] = player_name
            self.player_names.append(player_name)

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

    def heartbeat_loop(self, interval=5):
        while self.running:
            to_remove = []
            for sock in self.client_list[:]:
                try:
                    sock.sendall(b"__heartbeat__")
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
        message = ",".join(self.player_names)
        logging.info(f"[Broadcasting] Player list: {message}")
        for sock in self.client_list:
            try:
                sock.sendall(message.encode())
            except Exception as e:
                logging.warning(f"Failed to send player list: {e}")

    def broadcast(self, message):
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

    def _connection_loop(self):
        try:
            while self.running:
                result = self.accept_connection()
                if result:
                    client_socket, address = result
                    client_socket.send(str(self.user_count).encode())
                    self.user_count += 1
                    threading.Thread(target=self.new_client, daemon=True, args=(client_socket, address)).start()
        except Exception as e:
            logging.error(f"Connection loop error: {e}")
        finally:
            self.shutdown()

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
        start_broadcast(display_ip, self.port, len(self.players), 8, "LAN Party")

        threading.Thread(target=self._connection_loop, daemon=True).start()
        threading.Thread(target=self.heartbeat_loop, daemon=True).start()

    def shutdown(self):
        logging.info("Shutting down server.")
        self.running = False
        for client in self.client_list:
            client.close()
        self.server_socket.close()
