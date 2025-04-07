from multiprocessing import Process

import sys

import pygame
from client.button import Button
from server.server_ui import server_ui

# --- Constants ---
SCREEN_WIDTH = 1512
SCREEN_HEIGHT = 982
BUTTON_WIDTH = 420
BUTTON_HEIGHT = 90
BUTTON_SPACING = 100
BUTTON_COLOR = {
    "start": "green",
    "connect": "dodgerblue",
    "exit": "red"
}
FONT_COLOR = "Dark gray"
SPLASH_TEXT = "Main Menu!"
HOVER_COLOR = "white"
BACKGROUND = pygame.image.load("assets/background_mainmenu.jpg")
BACKGROUND = pygame.transform.scale(BACKGROUND, (SCREEN_WIDTH, SCREEN_HEIGHT))
server_process = None


def run_server():
    global server_process
    server_process = Process(target=server_ui)
    server_process.start()


def main_menu():
    global server_process
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Game")

    font_path = "assets/Silver.ttf"
    font = pygame.font.Font(font_path, 64)
    small_font = pygame.font.Font(font_path, 36)

    # Create buttons
    start_button = Button(None, (SCREEN_WIDTH // 2, 400), "Start Server", font, FONT_COLOR, HOVER_COLOR)
    connect_button = Button(None, (SCREEN_WIDTH // 2, 520), "Connect to Server", font, FONT_COLOR, HOVER_COLOR)
    exit_button = Button(None, (SCREEN_WIDTH // 2, 640), "Exit Game", font, FONT_COLOR, HOVER_COLOR)
    buttons = [start_button, connect_button, exit_button]

    splash = small_font.render(SPLASH_TEXT, True, "yellow") #title
    server_started = False

    while True:
        screen.blit(BACKGROUND, (0, 0))
        screen.blit(splash, (SCREEN_WIDTH // 2 - splash.get_width() // 2, 60))

        mouse_pos = pygame.mouse.get_pos()

        # Check if the server has exited
        if server_started and (not server_process.is_alive()):
            server_started = False
            start_button.base_color = FONT_COLOR
            start_button.hovering_color = HOVER_COLOR
            start_button.text = start_button.font.render("Start Server", True, FONT_COLOR)

        for button in buttons:
            if button == start_button and server_started:
                # Render "Server Running" as static gray
                button.text = button.font.render("Server Running", True, "white")
                button.image = pygame.Surface((BUTTON_WIDTH, BUTTON_HEIGHT), pygame.SRCALPHA)
                button.image.fill(pygame.Color("gray"))
                button.update(screen)
            else:
                button.changeColor(mouse_pos)
                button.update(screen)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if start_button.checkForInput(event.pos) and not server_started:
                    run_server()
                    server_started = True
                elif exit_button.checkForInput(event.pos):
                    pygame.quit()
                    sys.exit()


def draw_centered_text(screen, text, font, rect, color):
    rendered_text = font.render(text, True, color)
    text_rect = rendered_text.get_rect(center=rect.center)
    screen.blit(rendered_text, text_rect)


if __name__ == "__main__":
    main_menu()
