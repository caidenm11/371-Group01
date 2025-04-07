from multiprocessing import Process
import sys
import pygame
from client.button import Button
from server.server_ui import server_ui
from client.config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, BUTTON_WIDTH, BUTTON_HEIGHT, BUTTON_SPACING,
    FONT_COLOR, HOVER_COLOR, MAIN_MENU_BG, load_background,
    create_font, TITLE_FONT_SIZE, NORMAL_FONT_SIZE
)
from client.ui_utils import draw_centered_text


class MainMenu:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Game")

        self.font = create_font(TITLE_FONT_SIZE)
        self.small_font = create_font(NORMAL_FONT_SIZE)

        self.background = load_background(MAIN_MENU_BG)

        self.server_process = None
        self.server_started = False

        self._create_buttons()

    def _create_buttons(self):
        self.start_button = Button(None, (SCREEN_WIDTH // 2, 400), "Start Server",
                                  self.font, FONT_COLOR, HOVER_COLOR)
        self.connect_button = Button(None, (SCREEN_WIDTH // 2, 520), "Connect to Server",
                                     self.font, FONT_COLOR, HOVER_COLOR)
        self.exit_button = Button(None, (SCREEN_WIDTH // 2, 640), "Exit Game",
                                  self.font, FONT_COLOR, HOVER_COLOR)

        self.buttons = [self.start_button, self.connect_button, self.exit_button]

    def run_server(self):
        """Start the server in a separate process"""
        self.server_process = Process(target=server_ui)
        self.server_process.start()
        self.server_started = True

    def is_server_running(self):
        return self.server_process is not None and self.server_process.is_alive()

    def update_server_button(self):
        """ Show server status on the button """
        if not self.is_server_running() and self.server_started:
            self.server_started = False
            self.start_button.base_color = FONT_COLOR
            self.start_button.hovering_color = HOVER_COLOR
            self.start_button.set_text("Start Server")

    def run(self):
        """Main menu loop"""
        splash = self.small_font.render("Main Menu!", True, "yellow")

        running = True
        while running:
            # Clear screen and draw background
            self.screen.blit(self.background, (0, 0))
            self.screen.blit(splash, (SCREEN_WIDTH // 2 - splash.get_width() // 2, 60))

            self.update_server_button()

            mouse_pos = pygame.mouse.get_pos()

            # Draw buttons
            for button in self.buttons:
                if button == self.start_button and self.server_started:
                    # Render "Server Running" as static gray
                    button.text = button.font.render("Server Running", True, "white")
                    button.image = pygame.Surface((BUTTON_WIDTH, BUTTON_HEIGHT), pygame.SRCALPHA)
                    button.image.fill(pygame.Color("gray"))
                    button.update(self.screen)
                else:
                    button.changeColor(mouse_pos)
                    button.update(self.screen)

            pygame.display.flip()

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.start_button.checkForInput(event.pos) and not self.server_started:
                        self.run_server()
                    elif self.connect_button.checkForInput(event.pos):
                        from client.multiplayermenu import multiplayer_menu
                        multiplayer_menu()
                    elif self.exit_button.checkForInput(event.pos):
                        running = False

        pygame.quit()
        sys.exit()


def main_menu():
    menu = MainMenu()
    menu.run()


if __name__ == "__main__":
    main_menu()