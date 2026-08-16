import pygame

from src.input import key_to_direction
from src.contracts import Direction


def test_arrow_keys_map_to_directions() -> None:
    assert key_to_direction(pygame.K_UP) == Direction.UP
    assert key_to_direction(pygame.K_DOWN) == Direction.DOWN
    assert key_to_direction(pygame.K_LEFT) == Direction.LEFT
    assert key_to_direction(pygame.K_RIGHT) == Direction.RIGHT


def test_wasd_keys_map_to_directions() -> None:
    assert key_to_direction(pygame.K_w) == Direction.UP
    assert key_to_direction(pygame.K_s) == Direction.DOWN
    assert key_to_direction(pygame.K_a) == Direction.LEFT
    assert key_to_direction(pygame.K_d) == Direction.RIGHT


def test_unmapped_key_returns_none() -> None:
    assert key_to_direction(pygame.K_SPACE) is None
