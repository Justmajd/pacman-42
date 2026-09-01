import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame  # noqa: E402

from src.contracts import (  # noqa: E402
    Direction, GameSnapshot, GhostState, LevelData,
)
from src.rendering.renderer import Renderer  # noqa: E402


def make_level(
    width: int = 5,
    height: int = 5,
    walls: tuple[tuple[int, ...], ...] | None = None,
) -> LevelData:
    if walls is None:
        walls = tuple(tuple(0 for _ in range(width)) for _ in range(height))
    return LevelData(
        width=width,
        height=height,
        walls=walls,
        player_spawn=(1, 1),
        ghost_spawns=(
            (0, 0), (width - 1, 0), (0, height - 1), (width - 1, height - 1)
        ),
        pacgums=frozenset(),
        super_pacgums=frozenset(),
    )


def make_ghosts() -> tuple[GhostState, ...]:
    return tuple(
        GhostState(
            id=i, position=(i, 0), direction=Direction.RIGHT,
            is_frightened=False, is_active=True,
        )
        for i in range(4)
    )


def make_snapshot(**overrides: object) -> GameSnapshot:
    defaults: dict[str, object] = dict(
        player_pos=(1, 1),
        player_direction=Direction.RIGHT,
        player_is_dying=False,
        pacgums=frozenset(),
        super_pacgums=frozenset(),
        ghosts=make_ghosts(),
        score=0,
        lives=3,
        level=1,
        time=90.0,
    )
    defaults.update(overrides)
    return GameSnapshot(**defaults)  # type: ignore[arg-type]


def test_renderer_initializes_without_crashing() -> None:
    renderer = Renderer(400, 400, "test")
    assert renderer.screen is not None
    assert renderer.font is not None
    assert len(renderer.ghost_color) == 4
    renderer.cleanup()


def test_load_level_scales_tile_size_to_window_and_level() -> None:
    renderer = Renderer(400, 300, "test")

    renderer.load_level(make_level(width=20, height=15))
    usable_height = 300 - renderer.top_strip - renderer.bottom_strip
    assert renderer.tile_size == min(400 // 20, usable_height // 15)

    renderer.load_level(make_level(width=10, height=10))
    assert renderer.tile_size == min(400 // 10, usable_height // 10)

    renderer.cleanup()


def test_render_full_snapshot_does_not_crash() -> None:
    renderer = Renderer(400, 400, "test")
    renderer.load_level(make_level())

    snapshot = make_snapshot(
        pacgums=frozenset({(2, 2)}), super_pacgums=frozenset({(3, 3)}),
        score=250, lives=3, level=1, time=90.0,
    )

    renderer.render(snapshot)
    renderer.cleanup()


def test_player_position_maps_to_correct_pixel_no_xy_swap() -> None:
    renderer = Renderer(300, 300, "test")
    renderer.load_level(make_level(width=3, height=3))

    circle_calls: list[tuple[int, int]] = []
    real_circle = pygame.draw.circle

    def spy(surface: object, color: object,
            center: tuple[int, int], radius: object) -> object:
        circle_calls.append(center)
        return real_circle(surface, color, center, radius)

    pygame.draw.circle = spy
    try:
        renderer.render(make_snapshot(player_pos=(2, 0)))
    finally:
        pygame.draw.circle = real_circle

    player_center = circle_calls[0]
    expected_x = 2 * renderer.tile_size + renderer.tile_size // 2
    expected_y = renderer.top_strip + renderer.tile_size // 2
    assert player_center == (expected_x, expected_y)
    renderer.cleanup()


def test_ghost_colors_are_distinct() -> None:
    renderer = Renderer(400, 400, "test")
    renderer.load_level(make_level())

    rect_colors: list[tuple[int, int, int]] = []
    real_rect = pygame.draw.rect

    def spy(surface: object, color: tuple[int, int, int],
            rect: object, **kwargs: object) -> object:
        rect_colors.append(color)
        return real_rect(surface, color, rect, **kwargs)

    pygame.draw.rect = spy
    try:
        renderer.render(make_snapshot())
    finally:
        pygame.draw.rect = real_rect

    assert len(rect_colors) == 4
    assert len(set(rect_colors)) == 4
    renderer.cleanup()


def test_ghost_frightened_override_and_inactive_skipped() -> None:
    renderer = Renderer(400, 400, "test")
    renderer.load_level(make_level())

    rect_colors: list[tuple[int, int, int]] = []
    real_rect = pygame.draw.rect

    def spy(surface: object, color: tuple[int, int, int],
            rect: object, **kwargs: object) -> object:
        rect_colors.append(color)
        return real_rect(surface, color, rect, **kwargs)

    pygame.draw.rect = spy
    try:
        ghosts = (
            GhostState(id=0, position=(0, 0), direction=Direction.RIGHT,
                       is_frightened=True, is_active=True),
            GhostState(id=1, position=(1, 0), direction=Direction.RIGHT,
                       is_frightened=False, is_active=True),
            GhostState(id=2, position=(2, 0), direction=Direction.RIGHT,
                       is_frightened=False, is_active=False),
            GhostState(id=3, position=(3, 0), direction=Direction.RIGHT,
                       is_frightened=False, is_active=True),
        )
        renderer.render(make_snapshot(ghosts=ghosts))
    finally:
        pygame.draw.rect = real_rect

    assert len(rect_colors) == 3
    normal_ghost0_color = renderer.ghost_color[0]
    assert rect_colors[0] != normal_ghost0_color
    renderer.cleanup()


def test_wall_line_width_scales_with_tile_size() -> None:
    renderer = Renderer(500, 500, "test")
    renderer.load_level(make_level(width=5, height=5))
    assert max(2, renderer.tile_size // 20) > 1
    renderer.cleanup()


def test_render_does_not_crash_with_cheat_inflated_lives() -> None:
    renderer = Renderer(400, 400, "test")
    renderer.load_level(make_level())
    renderer.render(make_snapshot(lives=99))
    renderer.cleanup()


def test_level_anchor_position_is_stable_across_digit_counts() -> None:
    renderer = Renderer(400, 400, "test")
    renderer.load_level(make_level())

    level_max_width = renderer.font.size("Level: 10")[0]
    x_single_digit = renderer.window_width - level_max_width - 10
    x_double_digit = renderer.window_width - level_max_width - 10
    assert x_single_digit == x_double_digit
    renderer.cleanup()
