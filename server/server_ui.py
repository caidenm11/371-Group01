import pygame
import sys
import socket
import threading
import logging
from server.server import Server


# Config
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
LOG_AREA_HEIGHT = 480
BUTTON_HEIGHT = 60
FONT_SIZE = 24
IP_DISPLAY_HEIGHT = 40
MAX_LOG_LINES = 100

log_lines = []

running = True


class PygameLogHandler(logging.Handler):
    def emit(self, record):
        msg = self.format(record)
        if len(log_lines) >= MAX_LOG_LINES:
            log_lines.pop(0)
        log_lines.append(msg)


def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Doesn't need to succeed, just gets the local IP
        s.connect(("10.255.255.255", 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip


def server_ui():
    global running
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Server UI")
    font = pygame.font.Font(None, FONT_SIZE)

    # Setup logging
    handler = PygameLogHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s]: %(message)s'))
    logging.getLogger().addHandler(handler)
    logging.getLogger().setLevel(logging.INFO)

    # Start server (binds socket before starting thread)
    server = Server(host="0.0.0.0", port=53333)
    server.start()  # This now binds and starts the loop in a thread

    # Get actual IP and bound port
    bound_ip, bound_port = server.server_socket.getsockname()
    display_ip = get_local_ip()

    stop_button = pygame.Rect(0, SCREEN_HEIGHT - BUTTON_HEIGHT, SCREEN_WIDTH, BUTTON_HEIGHT)

    running = True
    while running:
        screen.fill((30, 30, 30))

        # Display IP and port
        ip_info = f"Server running on {display_ip}:{bound_port}"
        ip_surface = font.render(ip_info, True, (255, 255, 255))
        screen.blit(ip_surface, (20, 10))

        # Draw log area
        log_start_y = IP_DISPLAY_HEIGHT + 10
        log_area = pygame.Rect(20, log_start_y, SCREEN_WIDTH - 40, LOG_AREA_HEIGHT)
        pygame.draw.rect(screen, (50, 50, 50), log_area)

        log_y = log_area.top + 5
        visible_logs = log_lines[-(LOG_AREA_HEIGHT // (FONT_SIZE + 2)):]
        for line in visible_logs:
            text_surface = font.render(line, True, (200, 200, 200))
            screen.blit(text_surface, (log_area.left + 10, log_y))
            log_y += FONT_SIZE + 2

        # Stop button
        pygame.draw.rect(screen, (200, 50, 50), stop_button)
        stop_text = font.render("Stop Server", True, (255, 255, 255))
        screen.blit(stop_text, (
            stop_button.centerx - stop_text.get_width() // 2,
            stop_button.centery - stop_text.get_height() // 2
        ))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if stop_button.collidepoint(event.pos):
                    logging.info("Stopping server...")
                    server.shutdown()
                    running = False

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    server_ui()
