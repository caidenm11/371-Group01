import socket
import threading
import time

# Identifiers
BROADCAST_PORT = 54545
BROADCAST_INTERVAL = 2  # seconds
GAME_IDENTIFIER = "GAME_IDENTIFIER"  # Replace with the game name


def get_local_ip():
    # Sends some data to a broadcast address to get the local IP
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip


def format_broadcast_message(ip, port, player_count, max_players, server_name):
    return f"{GAME_IDENTIFIER}:{ip}:{port}:{player_count}:{max_players}:{server_name}"


def broadcast_loop(ip, port, player_count, max_players, server_name):
    message = format_broadcast_message(ip, port, player_count, max_players, server_name).encode()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    print(f"[LAN BROADCAST] Broadcasting on UDP {BROADCAST_PORT} every {BROADCAST_INTERVAL}s...")

    while True:
        sock.sendto(message, ('<broadcast>', BROADCAST_PORT))
        time.sleep(BROADCAST_INTERVAL)


def start_broadcast(ip, port, player_count, max_players, server_name):
    thread = threading.Thread(target=broadcast_loop, args=(ip, port, player_count, max_players, server_name), daemon=True)
    thread.start()


# Example usage
if __name__ == "__main__":
    ip = get_local_ip()
    start_broadcast(ip, 53333, 1, 8, "Caiden's LAN Party")
    while True:
        time.sleep(1)
