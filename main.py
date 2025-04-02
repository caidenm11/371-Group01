from client.game import start_game
from server.server_old import start_server
import threading

server_thread = threading.Thread(target=start_server, daemon=True)
server_thread.start()

start_game()