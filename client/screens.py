import pygame
import sys
from abc import ABC, abstractmethod
from client.config import SCREEN_WIDTH, SCREEN_HEIGHT, create_font, NORMAL_FONT_SIZE


class Screen(ABC):
    """Base class for all screens in the game"""

    def __init__(self, background_path=None):

        if not pygame.get_init():
            pygame.init()
        if not pygame.font.get_init():
            pygame.font.init()

        self.screen = pygame.display.get_surface()
        if not self.screen:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

        self.background = None
        if background_path:
            self.load_background(background_path)

        self.font = create_font(NORMAL_FONT_SIZE)

        self.buttons = []

    def load_background(self, path):
        from client.config import load_background
        self.background = load_background(path)

    def handle_common_events(self, event):
        if event.type == pygame.QUIT:
            self.quit()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return True  # Screen should handle this (exit/back)
        return False

    def update_buttons(self, mouse_pos):
        for button in self.buttons:
            button.changeColor(mouse_pos)
            button.update(self.screen)

    def draw_background(self):
        if self.background:
            self.screen.blit(self.background, (0, 0))

    def quit(self):
        pygame.quit()
        sys.exit()

    @abstractmethod
    def process_input(self, events):
        pass

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def render(self):
        pass

    def run(self):
        """Main loop for the screen"""
        clock = pygame.time.Clock()
        running = True

        while running:

            events = pygame.event.get()
            for event in events:
                if self.handle_common_events(event):
                    running = False

            result = self.process_input(events)
            if result is False:  # Screen wants to exit
                running = False

            self.update()

            self.draw_background()
            self.render()

            pygame.display.flip()

            clock.tick(60)

        return True
