import pygame
import sys

import pygame
from client.button import Button
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
FONT_COLOR = "black"
SPLASH_TEXT = "Main Menu!"
HOVER_COLOR = "white"
BACKGROUND = pygame.image.load("assets/background_mainmenu.jpg")
BACKGROUND = pygame.transform.scale(BACKGROUND, (SCREEN_WIDTH, SCREEN_HEIGHT))


def dummy_game_screen():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Game Screen")
    font = pygame.font.Font(None, 72)
    running = True

    while running:
        screen.fill("darkblue")
        text = font.render("Game Running!", True, "white")
        screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - text.get_height() // 2))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

    pygame.quit()


def load_assets():
    pass


def main_menu():
    load_assets()

    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("VocaCraft")

    font_path = "assets/Silver.ttf"
    font = pygame.font.Font(font_path, 64)
    small_font = pygame.font.Font(font_path, 36)

    # # Button positions
    # center_x = SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2
    # start_y = SCREEN_HEIGHT // 2 - BUTTON_SPACING
    # connect_y = SCREEN_HEIGHT // 2
    # exit_y = SCREEN_HEIGHT // 2 + BUTTON_SPACING
    #
    # start_button = pygame.Rect(center_x, start_y, BUTTON_WIDTH, BUTTON_HEIGHT)
    # connect_button = pygame.Rect(center_x, connect_y, BUTTON_WIDTH, BUTTON_HEIGHT)
    # exit_button = pygame.Rect(center_x, exit_y, BUTTON_WIDTH, BUTTON_HEIGHT)

    # Create buttons
    start_button = Button(None, (SCREEN_WIDTH // 2, 400), "Start Server", font, FONT_COLOR, HOVER_COLOR)
    connect_button = Button(None, (SCREEN_WIDTH // 2, 520), "Connect to Server", font, FONT_COLOR, HOVER_COLOR)
    exit_button = Button(None, (SCREEN_WIDTH // 2, 640), "Exit Game", font, FONT_COLOR, HOVER_COLOR)

    buttons = [start_button, connect_button, exit_button]

    splash = small_font.render(SPLASH_TEXT, True, "yellow")

    while True:
        # screen.fill(BACKGROUND_COLOR)
        screen.blit(BACKGROUND, (0, 0))  # Draw the background image

        # Draw splash text
        screen.blit(splash, (SCREEN_WIDTH // 2 - splash.get_width() // 2, 60))

        mouse_pos = pygame.mouse.get_pos()

        for button in buttons:
            button.changeColor(mouse_pos)
            button.update(screen)

        # Draw text on buttons

        # Draw text on buttons
        # draw_centered_text(screen, "Start Server", font, start_button, FONT_COLOR)
        # draw_centered_text(screen, "Connect to Server", font, connect_button, FONT_COLOR)
        # draw_centered_text(screen, "Exit Game", font, exit_button, FONT_COLOR)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        #
        # if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        #     if start_button.collidepoint(event.pos):
        #         print("🖥️ Start Server clicked (TODO)")
        #         elif connect_button.collidepoint(event.pos):
        #             dummy_game_screen()
        #         elif exit_button.collidepoint(event.pos):
        #             pygame.quit()
        #             sys.exit()


def draw_centered_text(screen, text, font, rect, color):
    rendered_text = font.render(text, True, color)
    text_rect = rendered_text.get_rect(center=rect.center)
    screen.blit(rendered_text, text_rect)


if __name__ == "__main__":
    main_menu()
