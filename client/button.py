import pygame


class Button():
    def __init__(self, image, pos, text_input, font, base_color, hovering_color):
        self.image = image
        self.x_pos = pos[0]
        self.y_pos = pos[1]
        self.font = font
        self.base_color, self.hovering_color = base_color, hovering_color
        self.text_input = text_input
        self.text = self.font.render(self.text_input, True, self.base_color)
        if self.image is None:
            self.image = self.text
        self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))
        self.text_rect = self.text.get_rect(center=(self.x_pos, self.y_pos))

    def update(self, screen):
        padding_x = 60
        padding_y = 30

        rect_width = self.text_rect.width + padding_x
        rect_height = self.text_rect.height + padding_y

        surface = pygame.Surface((rect_width, rect_height), pygame.SRCALPHA)
        surface.fill((50, 50, 50, 180))

        rect_surface = surface.get_rect(center=(self.x_pos, self.y_pos))
        text_surface = self.text.get_rect(center=(self.x_pos, self.y_pos + 5))  # 👈 Fix here

        screen.blit(surface, rect_surface)
        screen.blit(self.text, text_surface)

    def checkForInput(self, position):
        if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top,
                                                                                          self.rect.bottom):
            return True
        return False

    def changeColor(self, position):
        if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top,
                                                                                          self.rect.bottom):
            self.text = self.font.render(self.text_input, True, self.hovering_color)
        else:
            self.text = self.font.render(self.text_input, True, self.base_color)
