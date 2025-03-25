# Example file showing a circle moving on screen
import pygame
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

    while running:
        # poll for events
        # pygame.QUIT event means the user clicked X to close your window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # fill the screen with a color to wipe away anything from last frame
        screen.fill("purple")

        for player in players_pos:
            pygame.draw.circle(screen, "red", player, 40)

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

        # flip() the display to put your work on screen
        pygame.display.flip()

        # limits FPS to 60
        # dt is delta time in seconds since last frame, used for framerate-
        # independent physics.
        dt = clock.tick(60) / 1000

    close_client()
    pygame.quit()