import pygame

from src.contracts import Direction

_KEY_DIRECTIONS: dict[int, Direction] = {
    pygame.K_UP: Direction.UP,
    pygame.K_DOWN: Direction.DOWN,
    pygame.K_LEFT: Direction.LEFT,
    pygame.K_RIGHT: Direction.RIGHT,
    pygame.K_w: Direction.UP,
    pygame.K_s: Direction.DOWN,
    pygame.K_a: Direction.LEFT,
    pygame.K_d: Direction.RIGHT,
}


def key_to_direction(key: int) -> Direction | None:
    return _KEY_DIRECTIONS.get(key)
