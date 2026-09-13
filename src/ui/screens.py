from dataclasses import dataclass, field
from src.contracts import GameState, Direction
from src.ui.menu import Menu
from src.input import key_to_direction
from src.rendering.shapes import PACMAN_TRANSITION, PACMAN_RIGHT
import pygame

FONT_PATH = "assets/fonts/PressStart2P.ttf"

@dataclass
class MainMenuScreen:
    menu: Menu
    font: pygame.font.Font = field(default_factory=lambda: pygame.font.Font(FONT_PATH, 20))
    title_font: pygame.font.Font = field(default_factory=lambda: pygame.font.Font(FONT_PATH, 100))

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return None
        direction = key_to_direction(event.key)
        if direction == Direction.UP:
            self.menu.move_up()
        if direction == Direction.DOWN:
            self.menu.move_down()
        if event.key == pygame.K_RETURN:
            option = self.menu.selected_option()
            if option == "Start":
                return GameState.PLAYING
            elif option == "Highscores":
                return GameState.HIGHSCORES
            elif option == "Instructions":
                return GameState.INSTRUCTIONS
            elif option == "Exit":
                return GameState.EXIT

    def render(self, screen):
        screen.fill((0, 0, 0))

        pa_surface = self.title_font.render("PA", True, (255, 255, 255))
        man_surface = self.title_font.render("MAN", True, (255, 255, 255))
        icon_size = pa_surface.get_height()

        total_width = pa_surface.get_width() + icon_size + man_surface.get_width()
        start_x = (screen.get_width() - total_width) // 2

        menu_height = len(self.menu.options) * 40
        menu_start_y = (screen.get_height() - menu_height) // 2
        title_y = menu_start_y - icon_size - 60
        screen.blit(pa_surface, (start_x - 10, title_y))

        icon_x = start_x + pa_surface.get_width()
        pixel_size = icon_size // len(PACMAN_RIGHT)
        for row_idx, row in enumerate(PACMAN_RIGHT):
            for col_idx, cell in enumerate(row):
                if cell == '#':
                    pygame.draw.rect(screen, (255, 255, 0),
                                    pygame.Rect(icon_x + col_idx * pixel_size - 10,
                                                title_y + row_idx * pixel_size,
                                                pixel_size, pixel_size))

        screen.blit(man_surface, (icon_x + icon_size + 10, title_y))

        for index, label in enumerate(self.menu.options):
            if index == self.menu.selected_index:
                color = (255, 255, 0)
            else:
                color = (255, 255, 255)

            text_surface = self.font.render(label, True, color)
            x = (screen.get_width() - text_surface.get_width()) // 2
            screen.blit(text_surface, (x, menu_start_y + index * 40))


@dataclass
class PauseScreen:
    menu: Menu
    blurred_background: pygame.Surface | None = None
    font: pygame.font.Font = field(default_factory=lambda: pygame.font.Font(FONT_PATH, 20))

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return None

        direction = key_to_direction(event.key)

        if direction == Direction.UP:
            self.menu.move_up()
        if direction == Direction.DOWN:
            self.menu.move_down()
        if event.key == pygame.K_RETURN:
            option = self.menu.selected_option()
            if option == "Resume":
                return GameState.PLAYING
            elif option == "Main Menu":
                return GameState.MENU

    def render(self, screen):
        if self.blurred_background is not None:
            screen.blit(self.blurred_background, (0, 0))

        total_height = len(self.menu.options) * 40
        menu_start_y = (screen.get_height() - total_height) // 2

        for index, label in enumerate(self.menu.options):
            if index == self.menu.selected_index:
                color = (255, 255, 0)
            else:
                color = (255, 255, 255)

            text_surface = self.font.render(label, True, color)
            x = (screen.get_width() - text_surface.get_width()) // 2
            screen.blit(text_surface, (x, menu_start_y + index * 40))

    def capture_background(self, surface):
        self.blurred_background = pygame.transform.gaussian_blur(surface, 8)


NAME_MAX_LENGTH = 8


@dataclass
class GameOverScreen:
    menu: Menu
    font: pygame.font.Font = field(default_factory=lambda: pygame.font.Font(FONT_PATH, 20))
    title_font: pygame.font.Font = field(default_factory=lambda: pygame.font.Font(FONT_PATH, 56))
    name: str = ""
    entering_name: bool = True

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return None

        if self.entering_name:
            if event.key == pygame.K_RETURN and self.name:
                self.entering_name = False
            elif event.key in (pygame.K_RETURN, pygame.K_ESCAPE):
                self.name = ""
                self.entering_name = False
            elif event.key == pygame.K_BACKSPACE:
                self.name = self.name[:-1]
            elif event.unicode.isalnum() and len(self.name) < NAME_MAX_LENGTH:
                self.name += event.unicode.upper()
            return None

        direction = key_to_direction(event.key)

        if direction == Direction.UP:
            self.menu.move_up()
        if direction == Direction.DOWN:
            self.menu.move_down()
        if event.key == pygame.K_RETURN:
            option = self.menu.selected_option()
            if option == "Retry":
                return GameState.PLAYING
            elif option == "Main Menu":
                return GameState.MENU

    def reset(self):
        self.name = ""
        self.entering_name = True

    def render(self, screen, score):
        screen.fill((0, 0, 0))

        title_surface = self.title_font.render("GAME OVER", True, (255, 0, 0))
        title_x = (screen.get_width() - title_surface.get_width()) // 2
        title_y = 100
        screen.blit(title_surface, (title_x, title_y))

        score_surface = self.font.render(f"SCORE {score}", True, (255, 255, 255))
        score_x = (screen.get_width() - score_surface.get_width()) // 2
        score_y = title_y + title_surface.get_height() + 40
        screen.blit(score_surface, (score_x, score_y))

        if self.entering_name:
            prompt_surface = self.font.render("ENTER YOUR NAME", True, (255, 255, 255))
            prompt_x = (screen.get_width() - prompt_surface.get_width()) // 2
            prompt_y = score_y + 80
            screen.blit(prompt_surface, (prompt_x, prompt_y))

            name_surface = self.font.render(self.name + "_", True, (255, 255, 0))
            name_x = (screen.get_width() - name_surface.get_width()) // 2
            name_y = prompt_y + 40
            screen.blit(name_surface, (name_x, name_y))
            return

        menu_start_y = score_y + 80
        for index, label in enumerate(self.menu.options):
            if index == self.menu.selected_index:
                color = (255, 255, 0)
            else:
                color = (255, 255, 255)

            text_surface = self.font.render(label, True, color)
            x = (screen.get_width() - text_surface.get_width()) // 2
            screen.blit(text_surface, (x, menu_start_y + index * 40))


@dataclass
class VictoryScreen:
    menu: Menu
    font: pygame.font.Font = field(default_factory=lambda: pygame.font.Font(FONT_PATH, 20))
    title_font: pygame.font.Font = field(default_factory=lambda: pygame.font.Font(FONT_PATH, 48))
    name: str = ""
    entering_name: bool = True

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return None

        if self.entering_name:
            if event.key == pygame.K_RETURN and self.name:
                self.entering_name = False
            elif event.key in (pygame.K_RETURN, pygame.K_ESCAPE):
                self.name = ""
                self.entering_name = False
            elif event.key == pygame.K_BACKSPACE:
                self.name = self.name[:-1]
            elif event.unicode.isalnum() and len(self.name) < NAME_MAX_LENGTH:
                self.name += event.unicode.upper()
            return None

        direction = key_to_direction(event.key)

        if direction == Direction.UP:
            self.menu.move_up()
        if direction == Direction.DOWN:
            self.menu.move_down()
        if event.key == pygame.K_RETURN:
            option = self.menu.selected_option()
            if option == "Retry":
                return GameState.PLAYING
            elif option == "Main Menu":
                return GameState.MENU

    def reset(self):
        self.name = ""
        self.entering_name = True

    def render(self, screen, score):
        screen.fill((0, 0, 0))

        title_surface = self.title_font.render("YOU WIN", True, (255, 255, 0))
        title_x = (screen.get_width() - title_surface.get_width()) // 2
        title_y = 100
        screen.blit(title_surface, (title_x, title_y))

        score_surface = self.font.render(f"SCORE {score}", True, (255, 255, 255))
        score_x = (screen.get_width() - score_surface.get_width()) // 2
        score_y = title_y + title_surface.get_height() + 40
        screen.blit(score_surface, (score_x, score_y))

        if self.entering_name:
            prompt_surface = self.font.render("ENTER YOUR NAME", True, (255, 255, 255))
            prompt_x = (screen.get_width() - prompt_surface.get_width()) // 2
            prompt_y = score_y + 80
            screen.blit(prompt_surface, (prompt_x, prompt_y))

            name_surface = self.font.render(self.name + "_", True, (255, 255, 0))
            name_x = (screen.get_width() - name_surface.get_width()) // 2
            name_y = prompt_y + 40
            screen.blit(name_surface, (name_x, name_y))
            return

        menu_start_y = score_y + 80
        for index, label in enumerate(self.menu.options):
            if index == self.menu.selected_index:
                color = (255, 255, 0)
            else:
                color = (255, 255, 255)

            text_surface = self.font.render(label, True, color)
            x = (screen.get_width() - text_surface.get_width()) // 2
            screen.blit(text_surface, (x, menu_start_y + index * 40))


@dataclass
class Transition:
    elapsed: float = 0.0
    covering: bool = True
    frame_duration: float = 0.04
    finished: bool = False

    def update(self, dt):
        self.elapsed += dt
        if self.covering and self.elapsed >= 17 * self.frame_duration:
            self.covering = False
            self.elapsed = 0.0
        if not self.covering and self.elapsed >= 17 * self.frame_duration:
            self.finished = True

    def render(self, screen):
        frame_index = int(self.elapsed / self.frame_duration)
        frame_index = min(frame_index, 16)
        if not self.covering:
            frame_index = 16 - frame_index

        frame = PACMAN_TRANSITION[frame_index]

        pixel_width = screen.get_width() / 24
        pixel_height = screen.get_height() / 24

        for row_idx, row in enumerate(frame):
            for col_idx, cell in enumerate(row):
                if cell == '#':
                    x1 = round(col_idx * pixel_width)
                    x2 = round((col_idx + 1) * pixel_width)
                    y1 = round(row_idx * pixel_height)
                    y2 = round((row_idx + 1) * pixel_height)
                    pygame.draw.rect(screen, (255, 255, 0),
                                    pygame.Rect(x1, y1,
                                                x2 - x1,
                                                y2 - y1))
                    