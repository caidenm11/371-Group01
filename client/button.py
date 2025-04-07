import pygame


class Button:
    DEFAULT_PADDING_X = 60
    DEFAULT_PADDING_Y = 30
    DEFAULT_BACKGROUND_COLOR = (50, 50, 50, 180)

    def __init__(self, image, pos, text_input, font, base_color, hovering_color):
        self.image = image
        self.x_pos = pos[0]
        self.y_pos = pos[1]
        self.font = font
        self.base_color = base_color
        self.hovering_color = hovering_color
        self.text_input = text_input
        self.text = self.font.render(self.text_input, True, self.base_color)

        if self.image is None:
            self.image = self.text

        self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))
        self.text_rect = self.text.get_rect(center=(self.x_pos, self.y_pos))

        self._is_hovered = False
        self.enabled = True

    def update(self, screen):
        rect_width = self.text_rect.width + self.DEFAULT_PADDING_X
        rect_height = self.text_rect.height + self.DEFAULT_PADDING_Y

        surface = pygame.Surface((rect_width, rect_height), pygame.SRCALPHA)
        surface.fill(self.DEFAULT_BACKGROUND_COLOR)

        rect_surface = surface.get_rect(center=(self.x_pos, self.y_pos))
        text_surface = self.text.get_rect(center=(self.x_pos, self.y_pos + 5))

        screen.blit(surface, rect_surface)
        screen.blit(self.text, text_surface)

    def is_hovered(self, position):
        return (position[0] in range(self.rect.left, self.rect.right) and
                position[1] in range(self.rect.top, self.rect.bottom))

    def checkForInput(self, position):
        return self.enabled and self.is_hovered(position)

    def changeColor(self, position):
        if not self.enabled:
            return

        self._is_hovered = self.is_hovered(position)
        color = self.hovering_color if self._is_hovered else self.base_color
        self.text = self.font.render(self.text_input, True, color)

    def set_text(self, new_text):
        self.text_input = new_text
        self.text = self.font.render(self.text_input, True, self.base_color)
        self.text_rect = self.text.get_rect(center=(self.x_pos, self.y_pos))

    def disable(self):
        self.enabled = False

    def enable(self):
        self.enabled = True
