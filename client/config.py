import pygame

# Screen settings
SCREEN_WIDTH = 1512
SCREEN_HEIGHT = 982

# UI settings
BUTTON_WIDTH = 420
BUTTON_HEIGHT = 90
BUTTON_SPACING = 100
FONT_COLOR = "Dark gray"
HOVER_COLOR = "white"

# Paths
FONT_PATH = "assets/Silver.ttf"
MAIN_MENU_BG = "assets/background_mainmenu.jpg"
MULTIPLAYER_BG = "assets/multiplayer-bg.jpg"

# Server list settings
MAX_VISIBLE_SERVERS = 6
DOUBLE_CLICK_TIME = 0.4  # seconds

# Font sizes
TITLE_FONT_SIZE = 64
NORMAL_FONT_SIZE = 36
INPUT_FONT_SIZE = 48
SERVER_LIST_FONT_SIZE = 36

# Colors
BUTTON_COLORS = {
    "start": "green",
    "connect": "dodgerblue",
    "exit": "red"
}
BOX_COLOR = (30, 30, 30)
ACTIVE_BOX_COLOR = (70, 70, 70)
SERVER_LIST_BG = (30, 30, 30)
SERVER_LIST_HOVER = (50, 50, 70)
SERVER_LIST_SELECTED = (70, 70, 90)

TOTAL_PLAYERS = 4


def load_background(path, width=SCREEN_WIDTH, height=SCREEN_HEIGHT):
    bg = pygame.image.load(path)
    return pygame.transform.scale(bg, (width, height))


def create_font(size):
    return pygame.font.Font(FONT_PATH, size)
