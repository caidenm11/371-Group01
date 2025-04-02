import argparse
from client.game import start_game


def main():
    parser = argparse.ArgumentParser(description="Start the client and connect to a server.")
    parser.add_argument("--host", type=str, default="0.0.0.0",
                        help="IP address of the server (default: 0.0.0.0)")

    args = parser.parse_args()
    start_game(host=args.host)


if __name__ == "__main__":
    main()

# NOTE: To connect from a client that's on the same wifi, find the server's local IP address and use that as the host.
#       To find the local IP address of the server, run `ipconfig` on Windows or `ifconfig` on Linux/Mac.
#       The local IP address is typically in the format 192.168.x.x or 10.x.x.x.
