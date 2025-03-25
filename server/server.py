import socket
import threading

user_count = 0
client_list = []

def new_client(client_socket, addr):
    global client_list
    while True:
        data = client_socket.recv(1024).decode()
        if not data:
            break
        #client_socket.send("back to you TCP".encode())
        print(str(data))
        for socket in client_list:
            if socket != client_socket:
                socket.send(data.encode())
    
    client_socket.close()
    

def start_server():
    global user_count
    host = socket.gethostname()
    port = 53333

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(4)

    while True:
        client_socket, address = server_socket.accept()

        print("Client address: " + str(address))
        client_list.append(client_socket)
        user_count += 1
        client_socket.send(str(user_count).encode())
        client_thread = threading.Thread(target=new_client, daemon=True, args=(client_socket,address))
        client_thread.start()
