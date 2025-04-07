import socket
import threading
import time

# Identifiers
BROADCAST_PORT = 54545
LISTEN_TIMEOUT = 5  # seconds
GAME_IDENTIFIER = "GAME_IDENTIFIER"  # Replace with the game name
BUFFER_SIZE = 1024


class LANGameDiscovery:
    def __init__(self, listen_port=BROADCAST_PORT, identifier=GAME_IDENTIFIER):
        self.listen_port = listen_port
        self.identifier = identifier
        self.running = False
        self.found_servers = {}
        self.lock = threading.Lock()

    def parse_message(self, message):
        try:
            parts = message.split(":")
            if parts[0] != self.identifier or len(parts) < 6:
                return None
            return {
                "ip": parts[1],
                "port": int(parts[2]),
                "players": int(parts[3]),
                "max_players": int(parts[4]),
                "name": parts[5],
            }
        except Exception:
            return None

    def listen(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.bind(("", self.listen_port))
        sock.settimeout(1.0)

        self.running = True
        start_time = time.time()

        while self.running and (time.time() - start_time < LISTEN_TIMEOUT):
            try:
                data, addr = sock.recvfrom(BUFFER_SIZE)
                message = data.decode()
                parsed = self.parse_message(message)
                if parsed:
                    parsed["ip"] = addr[0]
                    key = f"{parsed['ip']}:{parsed['port']}"
                    with self.lock:
                        self.found_servers[key] = parsed
            except socket.timeout:
                continue

        sock.close()

    def discover(self, timeout=LISTEN_TIMEOUT):
        listener_thread = threading.Thread(target=self.listen)
        listener_thread.start()
        listener_thread.join(timeout)
        self.running = False
        with self.lock:
            return list(self.found_servers.values())


if __name__ == "__main__":
    discoverer = LANGameDiscovery()
    found = discoverer.discover(timeout=5)
    print("Discovered LAN Games:")
    for server in found:
        print(server)
