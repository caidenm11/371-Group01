import pygame
import random

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1000, 600))
clock = pygame.time.Clock()
running = True
dt = 0

# player setup
player_pos = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)
player_radius = 40

# object setup
object_list = ["helmet", "chestplate", "pants", "boots", "sword"]
object_size = 50
# set random spawnpoint for object
object_pos = pygame.Vector2(random.randint(0, screen.get_width() - object_size),
                            random.randint(0, screen.get_height() - object_size))

# list of player's collected parts
collected_parts = []

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

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # WASD movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        player_pos.y -= 300 * dt
    if keys[pygame.K_s]:
        player_pos.y += 300 * dt
    if keys[pygame.K_a]:
        player_pos.x -= 300 * dt
    if keys[pygame.K_d]:
        player_pos.x += 300 * dt

    # collision detection for player touching an object
    player_rect = pygame.Rect(player_pos.x - player_radius, 
                              player_pos.y - player_radius, 
                              player_radius * 2, 
                              player_radius * 2)
    if player_rect.colliderect(part.rect):
        if part.name not in collected_parts:
            collected_parts.append(part.name)
            print(f"Collected: {collected_parts}") # for debugging
        current_armor = (current_armor + 1) % len(object_list)
        part = Part(object_list[current_armor])
        
    # fill the screen with a color to wipe away anything from last frame
    screen.fill((183, 234, 255))
    screen.blit(part.image, part.rect.topleft)  # Draw object

    pygame.draw.circle(screen, "purple", player_pos, player_radius)

    # flip() the display to put your work on screen
    pygame.display.flip()

    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    dt = clock.tick(60) / 1000

pygame.quit()