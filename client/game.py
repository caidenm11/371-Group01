import pygame
import time
import queue
from client.client import start_client, close_client, send_key, send_object_pickup, send_object_drop, send_chest_drop, send_item_despawn
import client.client as client_var

players = {}
objects = {}
chests = {}

object_list = [1, 2, 3, 4]
screen = pygame.display.set_mode((1280, 720))

win_background = pygame.image.load("resources/win_screen.png")
win_background = pygame.transform.scale(win_background, (1280, 720))

event_queue = queue.Queue()

class Player:
    def __init__(self, player_id, x=0, y=0, color="red"):
        self.id = player_id        
        self.x = x
        self.y = y
        self.pos = pygame.Vector2(x, y)
        self.color = color  # Placeholder for unique player colors
        self.inventory = []  # List of held object IDs
        self.image = pygame.image.load(f"resources/player_{player_id}.png")
        self.image = pygame.transform.scale(self.image, (70, 70))
        
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
        self.pickup_pending = False

class Chest:
    def __init__(self, object_id, x, y, color="yellow"):  # Placeholder for object visuals
        self.id = object_id
        self.pos = pygame.Vector2(x, y)
        self.color = color
        self.image = pygame.image.load("resources/chest.png")
        self.image = pygame.transform.scale(self.image, (100, 100))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.held_by = None  # None means it's on the ground
        self.stored_items = {}  # Dictionary to hold items in the chest

def draw_win_screen(player_id):
    screen.fill("black")
    screen.blit(win_background, (0, 0))
    pygame.display.flip()

    font = pygame.font.Font(None,100)
    text = font.render(f"Player {player_id} Wins!", True, (225,225,255))
    text_rect = text.get_rect(center=(screen.get_width()//2, screen.get_height()//2+200))

    screen.blit(text, text_rect)
    pygame.display.flip()

def start_game(host="0.0.0.0", port=53333):
    # 🛠️ Change this to your server's IP if running over Wi-Fi or LAN

    # pygame setup
    global players
    global objects
    global chests
    pygame.init()
    
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 74)

    # Try to connect
    try:
        start_client(host)
    except Exception as e:
        print(f"❌ Failed to connect to server at {host}: {e}")
        pygame.quit()
        return
    running = True
    dt = 0


    # players = {i: Player(i, screen.get_width() / 2, screen.get_height() / 2) for i in range(4)} 
    # putting the chests in the 4 corners of the screen
    # chests = {i: Chest(i, 0 if i % 2 == 0 else screen.get_width() - 100, 0 if i < 2 else screen.get_height() - 100) for i in range(4)}

    while running:
        # Checking the win condition
        while not event_queue.empty():
            action, data = event_queue.get()
            if action == "WIN_PLAYER":
                draw_win_screen(data)
                print(f"Player {data} wins!")

                waiting = True
                while waiting:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            exit()
                        # MAYBE do this if you want to enter the game again
                        # elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                        #     waiting = False
        
        # poll for events
        # pygame.QUIT event means the user clicked X to close your window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # fill the screen with a color to wipe away anything from last frame
        screen.fill("light blue")

        for player in players.values():
            #player.draw(screen)
            screen.blit(player.image, player.pos)

        for chest in chests.values():
            screen.blit(chest.image, chest.rect.topleft)

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
        if keys[pygame.K_j]:
            if local_player and len(local_player.inventory) > 0:
                dropped_item = local_player.inventory[0]  # Don't pop yet
                send_object_drop(dropped_item.id)
                print(f"Requested drop of item {dropped_item.id} by player {local_player.id}")

        if movement:  # Only send if there's a movement command
            send_key(movement)

        
        # collision detection for player touching an object
        local_player = players.get(int(client_var.player_id))
        if local_player:
            player_rect = pygame.Rect(local_player.pos.x - 40, local_player.pos.y - 40, 80, 80)
            for obj in list(objects.values()):
                if (obj.held_by is None and not obj.pickup_pending and len(local_player.inventory) == 0
                and player_rect.colliderect(obj.rect)):
                    print(f"Local player wants to pick up: {obj}")
                    obj.pickup_pending = True
                    send_object_pickup(obj.id)
                    break
                  
        # update position of objects held by players
        for player in players.values():
            if len(player.inventory) > 0:
                player.inventory[0].rect.center = (player.pos.x - 40, player.pos.y - 50)

        for obj in objects.values():
            if obj.held_by is not None:
                obj.rect.topleft = (players[obj.held_by].pos.x, players[obj.held_by].pos.y - 50)

        # draw all objects
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
