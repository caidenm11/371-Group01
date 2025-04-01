# Example file showing a circle moving on screen
import pygame
import random
import time
from client.client import start_client, send_key, close_client
import client.client as client_var

players_pos = None

def start_game():
    # pygame setup
    global players_pos
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    clock = pygame.time.Clock()
    running = True
    dt = 0

    start_client()

    players_pos = [pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2) for _ in range(4)]
    print(players_pos)

    # object setup
    object_list = ["helmet", "chestplate", "pants", "boots", "sword"]
    object_size = 50
    
    # list of player's collected parts
    collected_parts = [[],[],[],[]]

    following_part = None
    follow_start_time = None

    winner = None

    class Part(pygame.sprite.Sprite):
        def __init__(self, name):
            super().__init__()
            self.name = name
            self.image = pygame.image.load(f"resources/{name}.png")
            self.image = pygame.transform.scale(self.image, (object_size, object_size))
            self.rect = self.image.get_rect()
            self.respawn()

        def respawn(self):
            self.rect.topleft = (random.randint(0, screen.get_width() - object_size),
                                random.randint(0, screen.get_height() - object_size))
    # index of next item to spawn
    current_armor = 0
    part = Part(object_list[current_armor])

    font = pygame.font.Font(None, 74)  # Font for win message

    while running:
        # poll for events
        # pygame.QUIT event means the user clicked X to close your window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            players_pos[int(client_var.client_id) - 1].y -= 300 * dt
            pos = str(players_pos[int(client_var.client_id) - 1].x) + ' ' + str(players_pos[int(client_var.client_id) - 1].y)
            send_key(pos)
        if keys[pygame.K_s]:
            players_pos[int(client_var.client_id) - 1].y += 300 * dt
            pos = str(players_pos[int(client_var.client_id) - 1].x) + ' ' + str(players_pos[int(client_var.client_id) - 1].y)
            send_key(pos)
        if keys[pygame.K_a]:
            players_pos[int(client_var.client_id) - 1].x -= 300 * dt
            pos = str(players_pos[int(client_var.client_id) - 1].x) + ' ' + str(players_pos[int(client_var.client_id) - 1].y)
            send_key(pos)
        if keys[pygame.K_d]:
            players_pos[int(client_var.client_id) - 1].x += 300 * dt
            pos = str(players_pos[int(client_var.client_id) - 1].x) + ' ' + str(players_pos[int(client_var.client_id) - 1].y)
            send_key(pos)

        # collision detection for player touching an object
        for player in players_pos:
            player_rect = pygame.Rect(player.x - 40, player.y - 40, 40 * 2, 40 * 2)
            if player_rect.colliderect(part.rect):
                if part.name not in collected_parts[int(client_var.client_id) - 1]:
                    collected_parts[int(client_var.client_id) - 1].append(part.name)
                    print(f"Player {[int(client_var.client_id) - 1]} Collected: {collected_parts}") # for debugging
                    # Start following logic
                    following_part = part
                    follow_start_time = time.time()                
                break
        
        player_index = int(client_var.client_id) - 1
        if following_part:
            following_part.rect.center = (players_pos[player_index].x, players_pos[player_index].y - 50)

            if time.time() - follow_start_time >= 3:
                following_part = None
                current_armor = (current_armor + 1) % len(object_list)
                part = Part(object_list[current_armor])

        for i in range(4):
            if len(collected_parts[i]) == 5:
                winner = i + 1
                running = False
                break

        # fill the screen with a color to wipe away anything from last frame
        screen.fill((183, 234, 255))
        if following_part:
            screen.blit(following_part.image, following_part.rect.topleft)
        else:
            screen.blit(part.image, part.rect.topleft)

        for player in players_pos:
            pygame.draw.circle(screen, "red", player, 40)

        # flip() the display to put your work on screen
        pygame.display.flip()  

        # limits FPS to 60
        # dt is delta time in seconds since last frame, used for framerate-
        # independent physics.
        dt = clock.tick(60) / 1000

    if winner:
        screen.fill((0,0,0))
        win_text = font.render(f"Player {winner} Wins!", True, (255, 255, 255))
        screen.blit(win_text, (screen.get_width() // 2 - 200, screen.get_height() // 2))
        pygame.display.flip()
        time.sleep(3)  # Show message for 3 seconds

    close_client()
    pygame.quit()