# Example file showing a circle moving on screen
import pygame
import random
from client.client import start_client, close_client, send_key, send_object_pickup
import client.client as client_var
from client.mainmenu import main_menu

players = {}
objects = {}
chests = {}
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

object_list = [1, 2, 3, 4]
screen = pygame.display.set_mode((1280, 720))

class Player:
    def __init__(self, player_id, x=0, y=0, color="red"):
        self.id = player_id        
        self.x = x
        self.y = y
        self.pos = pygame.Vector2(x, y)
        self.color = color  # Placeholder for unique player colors
        self.inventory = []  # List of held object IDs
        
    def draw(self, screen):
        pygame.draw.circle(screen, self.color, self.pos, 40)


class GameObject(pygame.sprite.Sprite):
    def __init__(self, object_id, x, y, armor_type):  # Placeholder for object visuals
        super().__init__()
        self.id = object_id
        self.pos = pygame.Vector2(x, y)
        self.armor_type = armor_type
        self.image = pygame.image.load(f"resources/{armor_type}.png")
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.held_by = None  # None means it's on the ground


class Chest:
    def __init__(self, object_id, x, y, color="yellow"):  # Placeholder for object visuals
        self.id = object_id
        self.pos = pygame.Vector2(x, y)
        self.color = color

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.pos.x - 20, self.pos.y - 20, 40, 40))  # Draw square object

def run_main_menu_screen(host="0.0.0.0", port=53333):
    global players
    global objects

    main_menu()
    
def start_game(host="0.0.0.0", port=53333):
    global players, objects

    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Knight Club")

    clock = pygame.time.Clock()

    try:
        start_client(host, port)
    except Exception as e:
        print(f"❌ Failed to connect to server at {host}:{port}: {e}")
        return

    players = {i: Player(i, screen.get_width() / 2, screen.get_height() / 2) for i in range(4)}

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        movement = ""
        if keys[pygame.K_w]: movement += "w"
        if keys[pygame.K_s]: movement += "s"
        if keys[pygame.K_a]: movement += "a"
        if keys[pygame.K_d]: movement += "d"
        if movement:
            send_key(movement)

        screen.fill("purple")
        for player in players.values():
            player.draw(screen)

        pygame.display.flip()
        clock.tick(60)

    close_client()
    pygame.quit()


def run_main_menu(host="0.0.0.0", port=53333):
    # 🛠️ Change this to your server's IP if running over Wi-Fi or LAN

    # pygame setup
    global players
    global objects
    # pygame.init()
    # screen = pygame.display.set_mode((1280, 720))
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    # Start the main menu
    main_menu()
    # Fill the screen black to start this screen

    pygame.init()
    
    clock = pygame.time.Clock()

    # Try to connect
    try:
        start_client(host)
    except Exception as e:
        print(f"❌ Failed to connect to server at {host}: {e}")
        # pygame.quit()
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
        screen.fill("light blue")

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

        # collision detection for player touching an object
        for player in players.values():
            player_rect = pygame.Rect(player.pos.x - 40, player.pos.y - 40, 40 * 2, 40 * 2)

            # check if player had collided with any game objects
            # if so, have the player pick it up
            for object in objects.values():
                if object.held_by is None and player_rect.colliderect(object.rect):
                    print(f"Player Picked up: {object}") # for debugging
                    player.inventory.append(object)
                    print(player.inventory[0])
                    object.held_by = player.id
                    # send that an object has been picked up
                    send_object_pickup(object.id)

        for player in players.values():
            if len(player.inventory) > 0:
                player.inventory[0].rect.center = (player.pos.x - 40, player.pos.y - 50)

        for obj in objects.values():
            if obj.held_by is not None:
                obj.rect.topleft = (players[obj.held_by].pos.x, players[obj.held_by].pos.y - 50)

        for obj in objects.values():
            screen.blit(obj.image, obj.rect.topleft)

        # flip() the display to put your work on screen
        pygame.display.flip()

        # limits FPS to 60
        # dt is delta time in seconds since last frame, used for framerate-
        # independent physics.
        dt = clock.tick(60) / 1000

    close_client()
    pygame.quit()
