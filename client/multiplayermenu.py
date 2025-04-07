import pygame
import sys
import socket
import time
from client.button import Button
from client.game import run_main_menu, start_game
from server.broadcast_discoverer import LANGameDiscovery
from client.config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FONT_COLOR, HOVER_COLOR,
    SERVER_LIST_BG, SERVER_LIST_HOVER, SERVER_LIST_SELECTED,
    MAX_VISIBLE_SERVERS, DOUBLE_CLICK_TIME, load_background,
    create_font, MULTIPLAYER_BG, NORMAL_FONT_SIZE, INPUT_FONT_SIZE
)
from client.ui_utils import create_text_input, create_title

# Still thinking this could be cleaned up more, the events are handled inside here, and we could probably clean that up quite a bit. Not very object oriented in that way.
class ServerBrowser:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Server Browser")

        self.font = create_font(NORMAL_FONT_SIZE)
        self.small_font = create_font(NORMAL_FONT_SIZE - 8)
        self.input_font = create_font(INPUT_FONT_SIZE)

        self.background = load_background(MULTIPLAYER_BG)

        self.discovered_servers = []
        self.scroll_offset = 0
        self.selected_index = None
        self.last_click_time = 0

        # Create UI elements
        self._create_buttons()

    def _create_buttons(self):
        """Create all buttons for the server browser"""
        self.add_button = Button(None, (1300, 150), "Add Server", self.font, FONT_COLOR, HOVER_COLOR)
        self.refresh_button = Button(None, (1300, 250), "Refresh", self.font, FONT_COLOR, HOVER_COLOR)
        self.connect_button = Button(None, (1300, 350), "Direct Connect", self.font, FONT_COLOR, HOVER_COLOR)
        self.connect_selected_button = Button(None, (1300, 550), "Join Selected", self.font, FONT_COLOR, HOVER_COLOR)
        self.exit_button = Button(None, (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60), "Exit", self.font, FONT_COLOR,
                                  HOVER_COLOR)

        self.buttons = [
            self.add_button, self.refresh_button, self.connect_button,
            self.exit_button, self.connect_selected_button
        ]

    def validate_ip(self, ip):
        try:
            socket.inet_aton(ip)
            return True
        except socket.error:
            return False

    def try_connect(self, ip_text, port_text):
        port_str = str(port_text)
        if self.validate_ip(ip_text) and port_str.isdigit():
            start_game(ip_text, int(port_str))
            return True
        return False

    def text_input_popup(self, mode="connect"):
        box_color, active_color = (30, 30, 30), (70, 70, 70)
        active_box = None
        name, ip, port = "", "", ""

        # Create buttons
        connect_text = "Connect" if mode == "connect" else "Add"
        connect_button = Button(None, (SCREEN_WIDTH // 2 + 120, 600), connect_text,
                                self.input_font, FONT_COLOR, HOVER_COLOR)
        back_button = Button(None, (SCREEN_WIDTH // 2 - 120, 600), "Back",
                             self.input_font, FONT_COLOR, HOVER_COLOR)

        # Create input boxes
        name_box = pygame.Rect(550, 320, 400, 60)
        ip_box = pygame.Rect(550, 400, 300, 60)
        port_box = pygame.Rect(900, 400, 150, 60)

        running = True
        while running:
            self.screen.blit(self.background, (0, 0))

            title_text = "Direct Connect" if mode == "connect" else "Add Server"
            title, title_pos = create_title(title_text, self.font)
            self.screen.blit(title, (title_pos, 200))

            # Draw input fields
            if mode == "add":
                create_text_input(self.screen, name_box, active_box, "name", name, "Name",
                                  self.input_font, box_color, active_color, (150, 150, 150))

            create_text_input(self.screen, ip_box, active_box, "ip", ip, "Enter IP",
                              self.input_font, box_color, active_color, (150, 150, 150))

            colon_surface = self.input_font.render(":", True, "white")
            self.screen.blit(colon_surface, (870, 410))

            create_text_input(self.screen, port_box, active_box, "port", port, "Port",
                              self.input_font, box_color, active_color, (150, 150, 150))

            # Draw buttons
            for btn in [connect_button, back_button]:
                btn.changeColor(pygame.mouse.get_pos())
                btn.update(self.screen)

            pygame.display.flip()

            # Handle events
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
                        return None
                    else:
                        active_box = None

    def refresh_lan_servers(self):
        discoverer = LANGameDiscovery()
        return discoverer.discover(timeout=3)

    def render_server_list(self):
        y_start = 150
        spacing = 80
        mouse_pos = pygame.mouse.get_pos()
        visible = self.discovered_servers[self.scroll_offset:self.scroll_offset + MAX_VISIBLE_SERVERS]

        for i, server in enumerate(visible):
            index = self.scroll_offset + i
            rect = pygame.Rect(100, y_start + i * spacing, 1000, 60)

            # Determine colors
            is_hovered = rect.collidepoint(mouse_pos)
            is_selected = index == self.selected_index

            bg_color = SERVER_LIST_SELECTED if is_selected else SERVER_LIST_HOVER if is_hovered else SERVER_LIST_BG
            text_color = "white" if is_selected or is_hovered else FONT_COLOR

            # Draw server entry
            pygame.draw.rect(self.screen, bg_color, rect, border_radius=8)
            text = f"{server['name']} ({server['ip']}:{server['port']})"
            self.screen.blit(self.font.render(text, True, text_color), (rect.x + 20, rect.y + 10))

            # Store rect for hit detection
            server["rect"] = rect

    def run(self):
        """Main loop for the server browser"""
        clock = pygame.time.Clock()
        running = True

        while running:
            # Draw background and title
            self.screen.blit(self.background, (0, 0))
            self.screen.blit(self.font.render("Multiplayer Servers", True, FONT_COLOR),
                             (SCREEN_WIDTH // 2 - 200, 40))

            # Draw server list
            self.render_server_list()

            # Draw buttons
            for btn in self.buttons:
                btn.changeColor(pygame.mouse.get_pos())
                btn.update(self.screen)

            pygame.display.flip()

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Handle button clicks
                    if self.connect_button.checkForInput(event.pos):
                        result = self.text_input_popup("connect")
                        if result:
                            ip, port = result
                            if self.try_connect(ip, port):
                                running = False
                    elif self.add_button.checkForInput(event.pos):
                        result = self.text_input_popup("add")
                        if result:
                            name, ip, port = result
                            self.discovered_servers.append({"name": name, "ip": ip, "port": int(port)})
                    elif self.refresh_button.checkForInput(event.pos):
                        self.discovered_servers = self.refresh_lan_servers()
                        self.selected_index = None
                        self.scroll_offset = 0
                    elif self.connect_selected_button.checkForInput(event.pos):
                        if self.selected_index is not None:
                            server = self.discovered_servers[self.selected_index]
                            ip, port = server["ip"], server["port"]
                            if self.try_connect(ip, port):
                                running = False
                    elif self.exit_button.checkForInput(event.pos):
                        run_main_menu()

                    # Handle server list selection
                    for i, server in enumerate(self.discovered_servers):
                        if "rect" in server and server["rect"].collidepoint(event.pos):
                            if (self.selected_index == i and
                                    time.time() - self.last_click_time < DOUBLE_CLICK_TIME):
                                # Double click to connect
                                if self.try_connect(server["ip"], str(server["port"])):
                                    running = False
                            else:
                                self.selected_index = i
                                self.last_click_time = time.time()

                elif event.type == pygame.MOUSEWHEEL:
                    # Handle scrolling
                    self.scroll_offset = max(0, self.scroll_offset - event.y)

            clock.tick(60)

        pygame.quit()
        sys.exit()


def multiplayer_menu():
    browser = ServerBrowser()
    browser.run()


if __name__ == "__main__":
    multiplayer_menu()
