import socket

from server.server import Server
import threading
import time
import sys


def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Doesn't need to succeed — just a dummy external connection to get our IP
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"
    finally:
        s.close()


def main():
    server = Server(host="0.0.0.0")
    local_ip = get_local_ip()
    print(f"\n🌐 Server started! Local IP for clients on same Wi-Fi: {local_ip}:53333")
    print("📡 Clients should connect using this IP.\n")
    server_thread = threading.Thread(target=server.start)
    server_thread.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Keyboard interrupt detected. Shutting down server.")
    finally:
        server.shutdown()
        server_thread.join()
        sys.exit(0)


if __name__ == "__main__":
    main()
