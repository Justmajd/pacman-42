import pygame
from src.contracts import LevelData, Direction, GameSnapshot
from src.rendering.shapes import (
    PACMAN_CLOSED, PACMAN_RIGHT, PACMAN_LEFT, PACMAN_UP, PACMAN_DOWN,
    PACMAN_RIGHT_OPENED, PACMAN_LEFT_OPENED,
    PACMAN_UP_OPENED, PACMAN_DOWN_OPENED,
    PACMAN_GAMEOVER,
    GHOST1, GHOST2, GHOST_EYES, GHOST_EYES_PUPIL, GHOST_FRIGHTENED_FACE,
    PACGUMS, SUPER_PACGUMS
)


class Renderer:
    def __init__(self, window_width: int,
                 window_height: int, window_title: str):
        pygame.init()

        self.screen = pygame.display.set_mode((window_width, window_height))
        pygame.display.set_caption(window_title)

        pygame.font.init()

        self.clock = pygame.time.Clock()
        self.is_running = True

        self.window_width: int = window_width
        self.window_height: int = window_height

        self.background_surface = None

        self.font = pygame.font.SysFont(None, 24)

        self.top_strip = 50
        self.bottom_strip = 50

        self.death_animation_start = None

        self.ghost_color = {
            0: (255, 0, 0),
            1: (255, 184, 255),
            2: (0, 255, 255),
            3: (255, 140, 0)
        }

    def process_events(self) -> list[pygame.event.Event]:
        events = pygame.event.get()

        for event in events:
            if event.type == pygame.QUIT:
                self.is_running = False
        return events

    def load_level(self, level_data: LevelData) -> None:
        self.background_surface = pygame.Surface(self.screen.get_size())
        self.background_surface.fill((0, 0, 0))

        self.tile_size = min(self.window_width // level_data.width, (self.window_height - self.top_strip - self.bottom_strip) // level_data.height)

        width, height = level_data.width, level_data.height
        walls = level_data.walls
        line_width = max(2, self.tile_size // 20)
        wall_color = (0, 0, 255)

        def cell_bit(r: int, c: int, bit: int) -> bool:
            return 0 <= r < height and 0 <= c < width and (walls[r][c] & bit) != 0

        def is_solid_block(r: int, c: int) -> bool:
            return 0 <= r < height and 0 <= c < width and walls[r][c] == 15

        def has_h_edge(row: int, col: int) -> bool:
            if is_solid_block(row - 1, col) and is_solid_block(row, col):
                return False
            return cell_bit(row - 1, col, 4) or cell_bit(row, col, 1)

        def has_v_edge(row: int, col: int) -> bool:
            if is_solid_block(row, col - 1) and is_solid_block(row, col):
                return False
            return cell_bit(row, col - 1, 2) or cell_bit(row, col, 8)

        edge_h = [
            [has_h_edge(row, col) for col in range(width)]
            for row in range(height + 1)
        ]
        edge_v = [
            [has_v_edge(row, col) for col in range(width + 1)]
            for row in range(height)
        ]

        for row in range(height + 1):
            col = 0
            while col < width:
                if edge_h[row][col]:
                    start_col = col
                    while col < width and edge_h[row][col]:
                        col += 1
                    y = self.top_strip + row * self.tile_size
                    x1 = start_col * self.tile_size
                    x2 = col * self.tile_size
                    pygame.draw.line(self.background_surface, wall_color, (x1, y), (x2, y), line_width)
                else:
                    col += 1

        for col in range(width + 1):
            row = 0
            while row < height:
                if edge_v[row][col]:
                    start_row = row
                    while row < height and edge_v[row][col]:
                        row += 1
                    x = col * self.tile_size
                    y1 = self.top_strip + start_row * self.tile_size
                    y2 = self.top_strip + row * self.tile_size
                    pygame.draw.line(self.background_surface, wall_color, (x, y1), (x, y2), line_width)
                else:
                    row += 1

    def render(self, snapshot: GameSnapshot) -> None:
        if self.background_surface is not None:
            self.screen.blit(self.background_surface, (0, 0))
        else:
            self.screen.fill((0, 0, 0))

        interp_x, interp_y = snapshot.player_pos
        pixel_x = interp_x * self.tile_size
        pixel_y = self.top_strip + (interp_y * self.tile_size)

        is_moving = snapshot.player_is_moving

        if snapshot.player_is_dying:
            if self.death_animation_start is None:
                self.death_animation_start = pygame.time.get_ticks()

            elapsed = pygame.time.get_ticks() - self.death_animation_start
            frame_index = min(elapsed // 100, len(PACMAN_GAMEOVER) - 1)
            sprite_to_draw = PACMAN_GAMEOVER[frame_index]
            pixel_size = self.tile_size // len(sprite_to_draw[0])

            for row_idx, row in enumerate(sprite_to_draw):
                for col_idx, cell in enumerate(row):
                    if cell == '#':
                        pygame.draw.rect(self.screen, (255, 255, 0),
                                        pygame.Rect(pixel_x + col_idx * pixel_size,
                                                    pixel_y + row_idx * pixel_size,
                                                    pixel_size, pixel_size))
        else:
            self.death_animation_start = None
            tick = pygame.time.get_ticks() // 150

            if snapshot.player_direction == Direction.NONE:
                half_open, wide_open = PACMAN_CLOSED, PACMAN_CLOSED
            elif snapshot.player_direction == Direction.RIGHT:
                half_open, wide_open = PACMAN_RIGHT, PACMAN_RIGHT_OPENED
            elif snapshot.player_direction == Direction.LEFT:
                half_open, wide_open = PACMAN_LEFT, PACMAN_LEFT_OPENED
            elif snapshot.player_direction == Direction.UP:
                half_open, wide_open = PACMAN_UP, PACMAN_UP_OPENED
            elif snapshot.player_direction == Direction.DOWN:
                half_open, wide_open = PACMAN_DOWN, PACMAN_DOWN_OPENED

            if not is_moving:
                sprite_to_draw = half_open
            else:
                phase = tick % 4
                if phase == 0:
                    sprite_to_draw = PACMAN_CLOSED
                elif phase == 2:
                    sprite_to_draw = wide_open
                else:
                    sprite_to_draw = half_open

            pixel_size = self.tile_size // len(sprite_to_draw)

            for row_idx, row in enumerate(sprite_to_draw):
                for col_idx, cell in enumerate(row):
                    if cell == '#':
                        pygame.draw.rect(self.screen, (255, 255, 0),
                                        pygame.Rect(pixel_x + col_idx * pixel_size,
                                                    pixel_y + row_idx * pixel_size,
                                                    pixel_size, pixel_size))
        

        pacgum_pixel_size = max(1, self.tile_size // 22)
        pacgum_width = len(PACGUMS[0]) * pacgum_pixel_size
        pacgum_height = len(PACGUMS) * pacgum_pixel_size
        for pacgums_pos in snapshot.pacgums:
            x, y = pacgums_pos
            origin_x = x * self.tile_size + (self.tile_size - pacgum_width) // 2
            origin_y = self.top_strip + y * self.tile_size + (self.tile_size - pacgum_height) // 2

            for row_idx, row in enumerate(PACGUMS):
                for col_idx, cell in enumerate(row):
                    if cell == '#':
                        pygame.draw.rect(self.screen, (255, 255, 255),
                                        pygame.Rect(origin_x + col_idx * pacgum_pixel_size,
                                                    origin_y + row_idx * pacgum_pixel_size,
                                                    pacgum_pixel_size, pacgum_pixel_size))

        super_pacgum_pixel_size = max(1, self.tile_size // 16)
        super_pacgum_width = len(SUPER_PACGUMS[0]) * super_pacgum_pixel_size
        super_pacgum_height = len(SUPER_PACGUMS) * super_pacgum_pixel_size
        for super_pacgums_pos in snapshot.super_pacgums:
            x, y = super_pacgums_pos
            origin_x = x * self.tile_size + (self.tile_size - super_pacgum_width) // 2
            origin_y = self.top_strip + y * self.tile_size + (self.tile_size - super_pacgum_height) // 2

            for row_idx, row in enumerate(SUPER_PACGUMS):
                for col_idx, cell in enumerate(row):
                    if cell == '#':
                        pygame.draw.rect(self.screen, (255, 255, 255),
                                        pygame.Rect(origin_x + col_idx * super_pacgum_pixel_size,
                                                    origin_y + row_idx * super_pacgum_pixel_size,
                                                    super_pacgum_pixel_size, super_pacgum_pixel_size))

        for ghost in snapshot.ghosts:
            if not ghost.is_active:
                continue

            interp_x, interp_y = ghost.position
            pixel_x = interp_x * self.tile_size
            pixel_y = self.top_strip + (interp_y * self.tile_size)
            pixel_size = self.tile_size // 14

            if ghost.is_frightened:
                flashing = ghost.frightened_time_remaining <= 2.0
                if flashing and (pygame.time.get_ticks() // 200) % 2 == 0:
                    color = (255, 255, 255)
                    face_color = (255, 0, 0)
                else:
                    color = (0, 0, 128)
                    face_color = (255, 182, 174)
            else:
                color = self.ghost_color[ghost.id]

            if not ghost.is_eaten:
                if tick % 2 != 0:
                            sprite_to_draw = GHOST1
                else:
                    sprite_to_draw = GHOST2
                
                for row_idx, row in enumerate(sprite_to_draw):
                    for col_idx, cell in enumerate(row):
                        if cell == '#':
                            pygame.draw.rect(self.screen, color,
                                            pygame.Rect(pixel_x + col_idx * pixel_size,
                                                        pixel_y + row_idx * pixel_size,
                                                        pixel_size, pixel_size))

            if not ghost.is_frightened or ghost.is_eaten:
                eyes_col_offset = 2
                eyes_row_offset = 3
                pupil_col_offset = eyes_col_offset + 1
                pupil_row_offset = eyes_row_offset + 2

                if ghost.direction == Direction.RIGHT or ghost.direction == Direction.NONE:
                    pupil_col_offset += 3
                    eyes_col_offset += 2
                elif ghost.direction == Direction.LEFT:
                    pupil_col_offset -= 2
                    eyes_col_offset -= 1
                elif ghost.direction == Direction.UP:
                    pupil_row_offset -= 3
                    eyes_row_offset -= 1
                elif ghost.direction == Direction.DOWN:
                    pupil_row_offset += 3
                    eyes_row_offset += 1

                for row_idx, row in enumerate(GHOST_EYES):
                    for col_idx, cell in enumerate(row):
                        if cell == '#':
                            pygame.draw.rect(
                                self.screen, (255, 255, 255),
                                pygame.Rect(
                                    pixel_x + (eyes_col_offset + col_idx) * pixel_size,
                                    pixel_y + (eyes_row_offset + row_idx) * pixel_size,
                                    pixel_size, pixel_size,
                                ),
                            )

                for row_idx, row in enumerate(GHOST_EYES_PUPIL):
                    for col_idx, cell in enumerate(row):
                        if cell == '#':
                            pygame.draw.rect(
                                self.screen, (0, 0, 255),
                                pygame.Rect(
                                    pixel_x + (pupil_col_offset + col_idx) * pixel_size,
                                    pixel_y + (pupil_row_offset + row_idx) * pixel_size,
                                    pixel_size, pixel_size,
                                ),
                            )
            else:
                face_col_offset = 1
                face_row_offset = 4

                for row_idx, row in enumerate(GHOST_FRIGHTENED_FACE):
                    for col_idx, cell in enumerate(row):
                        if cell == '#':
                            pygame.draw.rect(
                                self.screen, face_color,
                                pygame.Rect(
                                    pixel_x + (face_col_offset + col_idx) * pixel_size,
                                    pixel_y + (face_row_offset + row_idx) * pixel_size,
                                    pixel_size, pixel_size,
                                ),
                            )

        score = f"{snapshot.score}"
        score_surface = self.font.render(score, True, (255, 255, 255))
        self.screen.blit(score_surface, (10, 10))

        level = f"Level: {snapshot.level}"
        level_surface = self.font.render(level, True, (255, 255, 255))
        level_max_width = self.font.size("Level: 10")[0]
        x = self.window_width - level_max_width - 10
        self.screen.blit(level_surface, (x, 10))

        minutes = int(snapshot.time) // 60
        seconds = int(snapshot.time) % 60
        time = f"{minutes}:{seconds:02d}"
        time_surface = self.font.render(time, True, (255, 255, 255))
        x = (self.window_width - time_surface.get_width()) // 2
        self.screen.blit(time_surface, (x, 10))

        lives_radius = 15
        lives_center = (30, self.window_height - self.bottom_strip // 2)
        icon_size = lives_radius * 2
        icon_pixel_size = icon_size // 13
        icon_x = lives_center[0] - icon_size // 2
        icon_y = lives_center[1] - icon_size // 2
        for row_idx, row in enumerate(PACMAN_RIGHT):
            for col_idx, cell in enumerate(row):
                if cell == '#':
                    pygame.draw.rect(
                        self.screen, (255, 255, 0),
                        pygame.Rect(
                            icon_x + col_idx * icon_pixel_size,
                            icon_y + row_idx * icon_pixel_size,
                            icon_pixel_size, icon_pixel_size,
                        ),
                    )
        lives = f"x {snapshot.lives}"
        lives_surface = self.font.render(lives, True, (255, 255, 255))
        x = lives_center[0] + lives_radius + 10
        y = lives_center[1] - (lives_surface.get_height() // 2)
        self.screen.blit(lives_surface, (x, y))
        

        pygame.display.flip()
        self.clock.tick(60)

    def cleanup(self) -> None:
        pygame.quit()