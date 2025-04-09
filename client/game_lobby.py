import pygame
import sys
import socket
import threading
import uuid

from client.button import Button
from client.config import SCREEN_WIDTH, SCREEN_HEIGHT, FONT_COLOR, HOVER_COLOR, load_background, create_font, \
    TOTAL_PLAYERS
from server.packet_maker import ClientPacketType, ServerPacketType
from client.game import start_game

import time


class GameLobby:
    def __init__(self, player_name, server_ip, server_port):
        pygame.init()
        pygame.font.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Game Lobby")
        if not player_name:
            player_name = "Player_" + str(uuid.uuid4())[:6]  # e.g., Player_4f92d3

        self.font = create_font(30)
        self.small_font = create_font(20)
        self.background = load_background("assets/multiplayer-bg.jpg")

        self.player_name = player_name
        self.players = []
        self.start_button = Button(None, (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100), "Start Game", self.font, FONT_COLOR,
                                   HOVER_COLOR)

        self.start_game_requested = False;
        self.start_game_signal = False

        self.server_ip = server_ip
        self.server_port = server_port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.server_ip, self.server_port))
        self.client_socket.sendall(b"lobby")  # Tell server we're a lobby client
        time.sleep(0.1)  # Slight delay to avoid packet mix-up
        self.client_socket.sendall(self.player_name.encode())  # Then send the player name

        threading.Thread(target=self.receive_data, daemon=True).start()

    def receive_data(self):
        while True:
            try:
                data = self.client_socket.recv(1024).decode()
                if not data:
                    break
                lines = data.strip().split("\n")
                for line in lines:
                    if line == "__heartbeat__":
                        continue
                    elif line.startswith(str(ServerPacketType.START_GAME)):
                        print("[Lobby] Received START_GAME signal!")
                        self.start_game_signal = True  # set the flag
                        return
                    else:
                        self.update_players(line)
            except Exception as e:
                print(f"Error receiving data: {e}")
                break

    def update_players(self, data):
        self.players = [name.strip() for name in data.split(',') if name.strip()]

    def draw_lobby(self):
        self.screen.blit(self.background, (0, 0))
        title = self.font.render("Game Lobby", True, FONT_COLOR)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 50))

        player_count_text = self.font.render(f"Players: {len(self.players)}/{TOTAL_PLAYERS}", True, FONT_COLOR)
        self.screen.blit(player_count_text, (50, 50))

        for i, player in enumerate(self.players):
            player_text = self.small_font.render(player, True, FONT_COLOR)
            self.screen.blit(player_text, (50, 100 + i * 30))

        self.start_button.changeColor(pygame.mouse.get_pos())
        self.start_button.update(self.screen)

    def run(self):
        clock = pygame.time.Clock()
        running = True

        while running:
            if self.start_game_signal:
                # This needs to send the IP and Port or else it just defaults
                start_game(self.server_ip, self.server_port)
                return

            self.draw_lobby()
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.start_button.checkForInput(event.pos) and not self.start_game_requested:
                        try:
                            self.client_socket.sendall(f"{ClientPacketType.REQUEST_START_GAME}:\n".encode())
                            self.start_game_requested = True
                        except Exception as e:
                            print("Failed to send start game request:", e)

            clock.tick(60)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    lobby = GameLobby("Player1", "127.0.0.1", 53333)
    lobby.run()
