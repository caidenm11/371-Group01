import socket
import threading
import argparse


# Too lazy to grab something else and pygame doesn't work on Ipad...
def listen_to_server(sock):
    try:
        while True:
            data = sock.recv(1024).decode()
            if not data:
                print("Server disconnected.")
                break
            print(f"[Server]: {data}")
    except Exception as e:
        print(f"Listener error: {e}")
    finally:
        sock.close()


def start_basic_client(host="127.0.0.1", port=53333):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))

        # Receive initial data from server (e.g. player ID)
        initial = sock.recv(1024).decode()
        print(f"✅ Connected to server at {host}:{port}")
        print(f"🎮 Server says: {initial}")

        # Start listener thread
        listener = threading.Thread(target=listen_to_server, args=(sock,), daemon=True)
        listener.start()

        # Send messages from terminal
        while True:
            msg = input("You: ")
            if msg.lower() in ("exit", "quit"):
                break
            sock.send(msg.encode())

    except ConnectionRefusedError:
        print(f"❌ Could not connect to server at {host}:{port}")
    except Exception as e:
        print(f"💥 Error: {e}")
    finally:
        sock.close()
        print("🔌 Disconnected.")


def main():
    parser = argparse.ArgumentParser(description="Connect to the game server.")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Server IP address")
    args = parser.parse_args()
    start_basic_client(host=args.host)


if __name__ == "__main__":
    main()
