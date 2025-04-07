import pygame
import sys
import socket
import time
from client.button import Button
from client.game import run_main_menu, start_game
from server.broadcast_discoverer import LANGameDiscovery
# By far needs the most refactoring, but it works for now ...



# Settings
SCREEN_WIDTH = 1512
SCREEN_HEIGHT = 982
BUTTON_WIDTH = 400
BUTTON_HEIGHT = 60
FONT_COLOR = "Dark gray"
HOVER_COLOR = "white"
BACKGROUND = pygame.image.load("assets/multiplayer-bg.jpg")
BACKGROUND = pygame.transform.scale(BACKGROUND, (SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.init()
pygame.font.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Server Browser")
font = pygame.font.Font("assets/Silver.ttf", 36)
small_font = pygame.font.Font("assets/Silver.ttf", 28)
input_font = pygame.font.Font("assets/Silver.ttf", 48)

# Server List
discovered_servers = []
scroll_offset = 0
max_visible = 6
selected_index = None


def multiplayer_menu():
    # yeah this is a mess but it runs main, should probably refactor that...
    main()


def validate_ip(ip):
    try:
        socket.inet_aton(ip)
        return True
    except socket.error:
        return False


def try_connect(ip_text, port_text):
    port_str = str(port_text)
    if validate_ip(ip_text) and port_str.isdigit():
        start_game(ip_text, int(port_str))
        return True
    return False


def text_input_popup(mode="connect"):
    box_color, active_color = (30, 30, 30), (70, 70, 70)
    active_box = None
    name, ip, port = "", "", ""

    connect_button = Button(None, (SCREEN_WIDTH // 2 + 120, 600), "Connect" if mode == "connect" else "Add",
                            input_font, "Dark gray", "white")
    back_button = Button(None, (SCREEN_WIDTH // 2 - 120, 600), "Back",
                         input_font, "Dark gray", "white")

    name_box = pygame.Rect(550, 320, 400, 60)
    ip_box = pygame.Rect(550, 400, 300, 60)
    port_box = pygame.Rect(900, 400, 150, 60)

    running = True
    while running:
        screen.blit(BACKGROUND, (0, 0))
        title = font.render("Direct Connect" if mode == "connect" else "Add Server", True, "white")
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 200))

        # --- Name box (Add Server only)
        if mode == "add":
            pygame.draw.rect(screen, active_color if active_box == "name" else box_color, name_box, border_radius=8)
            name_surface = input_font.render(name if name or active_box == "name" else "Name", True,
                                             "white" if name or active_box == "name" else (150, 150, 150))
            screen.blit(name_surface, (name_box.x + 10, name_box.y + 10))

        # --- IP box
        pygame.draw.rect(screen, active_color if active_box == "ip" else box_color, ip_box, border_radius=8)
        ip_surface = input_font.render(ip if ip or active_box == "ip" else "Enter IP", True,
                                       "white" if ip or active_box == "ip" else (150, 150, 150))
        screen.blit(ip_surface, (ip_box.x + 10, ip_box.y + 10))

        # --- Colon separator
        colon_surface = input_font.render(":", True, "white")
        screen.blit(colon_surface, (870, 410))

        # --- Port box
        pygame.draw.rect(screen, active_color if active_box == "port" else box_color, port_box, border_radius=8)
        port_surface = input_font.render(port if port or active_box == "port" else "Port", True,
                                         "white" if port or active_box == "port" else (150, 150, 150))
        screen.blit(port_surface, (port_box.x + 10, port_box.y + 10))

        # --- Buttons
        for btn in [connect_button, back_button]:
            btn.changeColor(pygame.mouse.get_pos())
            btn.update(screen)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None
                elif event.key == pygame.K_RETURN:
                    if mode == "connect" and ip and port:
                        return ip, port
                    elif mode == "add" and name and ip and port:
                        return name, ip, port
                elif active_box == "ip":
                    if event.key == pygame.K_BACKSPACE:
                        ip = ip[:-1]
                    elif event.unicode in "0123456789.":
                        ip += event.unicode
                elif active_box == "port":
                    if event.key == pygame.K_BACKSPACE:
                        port = port[:-1]
                    elif event.unicode.isdigit():
                        port += event.unicode
                elif active_box == "name":
                    if event.key == pygame.K_BACKSPACE:
                        name = name[:-1]
                    else:
                        name += event.unicode

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if mode == "add" and name_box.collidepoint(event.pos):
                    active_box = "name"
                elif ip_box.collidepoint(event.pos):
                    active_box = "ip"
                elif port_box.collidepoint(event.pos):
                    active_box = "port"
                elif connect_button.checkForInput(event.pos):
                    if mode == "connect" and ip and port:
                        return ip, port
                    elif mode == "add" and name and ip and port:
                        return name, ip, port
                elif back_button.checkForInput(event.pos):
                    return None  # Exit to previous screen
                else:
                    active_box = None


def refresh_lan_servers():
    discoverer = LANGameDiscovery()
    return discoverer.discover(timeout=3)


def render_server_list():
    global scroll_offset
    y_start = 150
    spacing = 80
    mouse_pos = pygame.mouse.get_pos()
    visible = discovered_servers[scroll_offset:scroll_offset + max_visible]

    for i, server in enumerate(visible):
        index = scroll_offset + i
        rect = pygame.Rect(100, y_start + i * spacing, 1000, BUTTON_HEIGHT)
        is_hovered = rect.collidepoint(mouse_pos)
        bg_color = (70, 70, 90) if index == selected_index else (50, 50, 70) if is_hovered else (30, 30, 30)
        text_color = "white" if index == selected_index or is_hovered else FONT_COLOR
        pygame.draw.rect(screen, bg_color, rect, border_radius=8)
        text = f"{server['name']} ({server['ip']}:{server['port']})"
        screen.blit(font.render(text, True, text_color), (rect.x + 20, rect.y + 10))
        server["rect"] = rect


def main():
    global scroll_offset, selected_index
    global discovered_servers, selected_index, scroll_offset
    last_click_time = 0
    DOUBLE_CLICK_TIME = 0.4  # seconds

    clock = pygame.time.Clock()
    # BUTTONS
    add_button = Button(None, (1300, 150), "Add Server", font, FONT_COLOR, HOVER_COLOR)
    refresh_button = Button(None, (1300, 250), "Refresh", font, FONT_COLOR, HOVER_COLOR)
    connect_button = Button(None, (1300, 350), "Direct Connect", font, FONT_COLOR, HOVER_COLOR)
    exit_button = Button(None, (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60), "Exit", font, FONT_COLOR, HOVER_COLOR)
    connect_selected_button = Button(None, (1300, 550), "Join Selected", font, FONT_COLOR, HOVER_COLOR)

    running = True
    while running:
        screen.blit(BACKGROUND, (0, 0))
        screen.blit(font.render("Multiplayer Servers", True, FONT_COLOR), (SCREEN_WIDTH // 2 - 200, 40))
        render_server_list()

        for btn in [add_button, refresh_button, connect_button, exit_button, connect_selected_button]:
            btn.changeColor(pygame.mouse.get_pos())
            btn.update(screen)

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if connect_button.checkForInput(event.pos):
                    result = text_input_popup("connect")
                    if result:
                        ip, port = result
                        if try_connect(ip, port):
                            running = False
                elif add_button.checkForInput(event.pos):
                    result = text_input_popup("add")
                    if result:
                        name, ip, port = result
                        discovered_servers.append({"name": name, "ip": ip, "port": int(port)})
                elif refresh_button.checkForInput(event.pos):
                    discovered_servers = refresh_lan_servers()
                    selected_index = None
                    scroll_offset = 0
                elif connect_selected_button.checkForInput(event.pos):
                    if selected_index is not None:
                        server = discovered_servers[selected_index]
                        ip, port = server["ip"], server["port"]
                        if try_connect(ip, port):
                            running = False
                elif exit_button.checkForInput(event.pos):
                    #     run the main menu
                    run_main_menu()
                    # running = False
                for i, server in enumerate(discovered_servers):
                    if "rect" in server and server["rect"].collidepoint(event.pos):
                        if selected_index == i and time.time() - last_click_time < DOUBLE_CLICK_TIME:
                            if try_connect(server["ip"], str(server["port"])):
                                running = False
                        else:
                            selected_index = i
                            last_click_time = time.time()
            elif event.type == pygame.MOUSEWHEEL:
                scroll_offset = max(0, scroll_offset - event.y)

        clock.tick(60)
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
