# Example file showing a circle moving on screen
import pygame
from client.client import start_client, send_key, close_client
import client.client as client_var

players = {}
objects = {}


class Player:
    def __init__(self, player_id, x, y, color="red"):
        self.id = player_id
        self.pos = pygame.Vector2(x, y)
        self.color = color  # Placeholder for unique player colors

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, self.pos, 40)


class GameObject:
    def __init__(self, object_id, x, y, color="blue"):  # Placeholder for object visuals
        self.id = object_id
        self.pos = pygame.Vector2(x, y)
        self.color = color

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.pos.x - 20, self.pos.y - 20, 40, 40))  # Draw square object


def start_game(host="0.0.0.0", port=53333):
    # 🛠️ Change this to your server's IP if running over Wi-Fi or LAN

    # pygame setup
    global players
    global objects
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    clock = pygame.time.Clock()

    # Try to connect
    try:
        start_client(host)
    except Exception as e:
        print(f"❌ Failed to connect to server at {host}: {e}")
        pygame.quit()
        return
    running = True
    dt = 0


    players = {i: Player(i, screen.get_width() / 2, screen.get_height() / 2) for i in range(4)}

    while running:
        # poll for events
        # pygame.QUIT event means the user clicked X to close your window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # fill the screen with a color to wipe away anything from last frame
        screen.fill("purple")

        for player in players.values():
            player.draw(screen)

        keys = pygame.key.get_pressed()
        movement = ""

        if keys[pygame.K_w]:
            movement += "w"
        if keys[pygame.K_s]:
            movement += "s"
        if keys[pygame.K_a]:
            movement += "a"
        if keys[pygame.K_d]:
            movement += "d"

        if movement:  # Only send if there's a movement command
            send_key(movement)

        # flip() the display to put your work on screen
        pygame.display.flip()

        # limits FPS to 60
        # dt is delta time in seconds since last frame, used for framerate-
        # independent physics.
        dt = clock.tick(60) / 1000

    close_client()
    pygame.quit()
