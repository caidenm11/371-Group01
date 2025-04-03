import socket
import threading
import logging
from server.packet_maker import PacketMaker
from server.packet_maker import ServerPacketType, ClientPacketType
from Engine.player import Player
from Engine.gameobject import GameObject
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')


class Server:
    def __init__(self, host='0.0.0.0', port=53333):
        self.host = host or socket.gethostname()
        self.port = port
        self.user_count = 0
        self.client_list = []
        self.players = {}
        self.objects = {}
        self.stands = {}
        self.next_object_id = 100
        self.running = True
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

    def broadcast(self, message):
        for sock in self.client_list:
            sock.send(message.encode())

    def accept_connection(self):
        try:
            client_socket, address = self.server_socket.accept()
            return client_socket, address
        except socket.timeout:
            return None

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
                    self.user_count += 1

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

