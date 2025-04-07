from client.game import run_main_menu
from server.server_old import start_server
import threading

server_thread = threading.Thread(target=start_server, daemon=True)
server_thread.start()

run_main_menu()