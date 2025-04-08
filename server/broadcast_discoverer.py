import socket
import time


class LANGameDiscovery:
    def __init__(self, port=54545, identifier="GAME_IDENTIFIER"):
        self.port = port
        self.identifier = identifier

    def discover(self, timeout=3):
        # Discover LAN games by sending a broadcast message and listening for responses
        found = []
        seen_addresses = set()

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        sock.bind(("", self.port))  # <-- Listen on any interface
        sock.settimeout(timeout)

        start = time.time()
        while time.time() - start < timeout:
            try:
                data, addr = sock.recvfrom(1024)
                msg = data.decode()
                if msg.startswith(self.identifier):
                    parts = msg.split(":")
                    if len(parts) >= 6:
                        _, ip, port, players, max_players, name = parts[:6]
                        key = (ip, port)
                        if key not in seen_addresses:
                            seen_addresses.add(key)
                            found.append({
                                "ip": ip,
                                "port": int(port),
                                "player_count": players,
                                "max_players": max_players,
                                "name": name,
                            })
            except socket.timeout:
                break
        sock.close()
        return found
