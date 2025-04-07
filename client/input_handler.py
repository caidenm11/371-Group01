import pygame


class TextInput:

    def __init__(self, rect, placeholder="", initial_value="",
                 font=None, active_color=(70, 70, 70), inactive_color=(30, 30, 30),
                 text_color="white", placeholder_color=(150, 150, 150),
                 allowed_chars=None, max_length=None, border_radius=8):
        self.rect = rect
        self.placeholder = placeholder
        self.value = initial_value
        self.font = font
        self.active_color = active_color
        self.inactive_color = inactive_color
        self.text_color = text_color
        self.placeholder_color = placeholder_color
        self.allowed_chars = allowed_chars
        self.max_length = max_length
        self.border_radius = border_radius
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
            return self.active

        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                # Handle backspace
                self.value = self.value[:-1]
                return True
            elif event.key in (pygame.K_RETURN, pygame.K_TAB):
                # Enter/Tab deactivates and moves to next field
                self.active = False
                return True
            else:
                # Add character if it passes validation
                if self.allowed_chars and event.unicode not in self.allowed_chars:
                    return False

                if self.max_length and len(self.value) >= self.max_length:
                    return False

                self.value += event.unicode
                return True

        return False

    def draw(self, screen):
        # Draw background
        color = self.active_color if self.active else self.inactive_color
        pygame.draw.rect(screen, color, self.rect, border_radius=self.border_radius)

        # Draw text or placeholder
        if self.value or self.active:
            text_color = self.text_color
            text = self.value
        else:
            text_color = self.placeholder_color
            text = self.placeholder

        # Render and position text
        if self.font:
            text_surface = self.font.render(text, True, text_color)
            screen.blit(text_surface, (self.rect.x + 10, self.rect.y + 10))

    def set_value(self, value):
        self.value = value

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)


class InputManager:

    def __init__(self):
        self.inputs = {}
        self.active_input = None

    def add_input(self, name, input_field):
        self.inputs[name] = input_field

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Check if any input was clicked
            clicked = False
            for name, input_field in self.inputs.items():
                if input_field.is_clicked(event.pos):
                    self.active_input = name
                    input_field.active = True
                    clicked = True
                else:
                    input_field.active = False

            if not clicked:
                self.active_input = None

        elif event.type == pygame.KEYDOWN and self.active_input:
            # Pass event to active input
            self.inputs[self.active_input].handle_event(event)

            # Tab navigation between fields
            if event.key == pygame.K_TAB:
                self._activate_next_input()

    def _activate_next_input(self):
        input_names = list(self.inputs.keys())
        if not input_names or not self.active_input:
            return

        current_index = input_names.index(self.active_input)
        next_index = (current_index + 1) % len(input_names)

        self.inputs[self.active_input].active = False
        self.active_input = input_names[next_index]
        self.inputs[self.active_input].active = True

    def draw_all(self, screen):
        for input_field in self.inputs.values():
            input_field.draw(screen)

    def get_values(self):
        return {name: input_field.value for name, input_field in self.inputs.items()}

    def get_value(self, name):
        if name in self.inputs:
            return self.inputs[name].value
        return None
