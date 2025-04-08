import pygame
from client.config import SCREEN_WIDTH
# This file contains utility functions for rendering text and creating UI elements in Pygamem used in mainmenu/multiplayermenu.

def draw_centered_text(screen, text, font, rect, color):
    rendered_text = font.render(text, True, color)
    text_rect = rendered_text.get_rect(center=rect.center)
    screen.blit(rendered_text, text_rect)


def create_text_input(screen, rect, active_box, box_id, value, placeholder, font,
                      box_color, active_color, placeholder_color="white"):
    color = active_color if active_box == box_id else box_color
    pygame.draw.rect(screen, color, rect, border_radius=8)

    # Determine text and color
    text = value if value or active_box == box_id else placeholder
    text_color = "white" if value or active_box == box_id else placeholder_color

    # Render text
    text_surface = font.render(text, True, text_color)
    screen.blit(text_surface, (rect.x + 10, rect.y + 10))

    return rect


def create_title(text, font, color="white"):
    title = font.render(text, True, color)
    return title, (SCREEN_WIDTH // 2 - title.get_width() // 2)
