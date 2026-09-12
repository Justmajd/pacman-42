from dataclasses import replace

import pytest

from src.config import GameConfig, LevelConfig
from src.contracts import LevelData
from src.maze_adapter import MazeGeneratorProvider, validate_level_data


def open_walls(
    width: int = 7,
    height: int = 7,
    isolated: frozenset[tuple[int, int]] = frozenset(),
) -> list[list[int]]:
    walls = [[0 for _ in range(width)] for _ in range(height)]
    for y in range(height):
        for x in range(width):
            if y == 0:
                walls[y][x] |= 1
            if x == width - 1:
                walls[y][x] |= 2
            if y == height - 1:
                walls[y][x] |= 4
            if x == 0:
                walls[y][x] |= 8

    for x, y in isolated:
        walls[y][x] = 15
        for dx, dy, bit in (
            (0, -1, 4),
            (1, 0, 8),
            (0, 1, 1),
            (-1, 0, 2),
        ):
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height:
                walls[ny][nx] |= bit
    return walls


class FakeMazeGenerator:
    def __init__(
        self,
        size: tuple[int, int],
        perfect: bool,
        seed: int | None,
        maze: list[list[int]],
        entry: tuple[int, int] = (1, 1),
        exit_cell: tuple[int, int] | None = None,
    ) -> None:
        self.size = size
        self.perfect = perfect
        self.seed = seed
        self._maze = maze
        self._entry = entry
        self._exit = exit_cell or (size[0] - 2, size[1] - 2)
        self.exit_was_read = False

    @property
    def maze(self) -> list[list[int]]:
        return self._maze

    @property
    def maze_entry(self) -> tuple[int, int]:
        return self._entry

    @property
    def maze_exit(self) -> tuple[int, int]:
        self.exit_was_read = True
        return self._exit


def make_config(
    *,
    pacgum_count: int = 6,
    seed: int = 42,
    width: int = 7,
    height: int = 7,
) -> GameConfig:
    levels = tuple(
        LevelConfig(width=width, height=height)
        for _ in range(10)
    )
    return GameConfig(
        levels=levels,
        pacgum_count=pacgum_count,
        seed=seed,
    )


def make_provider(
    config: GameConfig | None = None,
    maze: list[list[int]] | None = None,
    entry: tuple[int, int] = (1, 1),
    exit_cell: tuple[int, int] | None = None,
) -> tuple[
    MazeGeneratorProvider,
    list[tuple[tuple[int, int], bool, int | None]],
    list[FakeMazeGenerator],
]:
    selected_config = config or make_config()
    if maze is None:
        selected_maze = open_walls(
            selected_config.levels[0].width,
            selected_config.levels[0].height,
        )
    else:
        selected_maze = maze
    calls: list[tuple[tuple[int, int], bool, int | None]] = []
    generators: list[FakeMazeGenerator] = []

    def factory(
        *,
        size: tuple[int, int],
        perfect: bool,
        seed: int | None,
    ) -> FakeMazeGenerator:
        calls.append((size, perfect, seed))
        generator = FakeMazeGenerator(
            size=size,
            perfect=perfect,
            seed=seed,
            maze=selected_maze,
            entry=entry,
            exit_cell=exit_cell,
        )
        generators.append(generator)
        return generator

    return MazeGeneratorProvider(selected_config, factory), calls, generators


def test_factory_receives_dimensions_mode_and_resolved_seed() -> None:
    config = make_config(seed=123)
    provider, calls, _ = make_provider(config)

    provider.build_level(1, config.seed)
    provider.build_level(2, config.seed)

    assert calls == [
        ((7, 7), False, 42),
        ((7, 7), False, 124),
    ]


def test_level_one_always_uses_seed_42() -> None:
    default_config = make_config()
    default_provider, default_calls, _ = make_provider(default_config)
    default_provider.build_level(1)

    custom_config = make_config(seed=987)
    custom_provider, custom_calls, _ = make_provider(custom_config)
    custom_provider.build_level(1)

    assert default_config.seed == 42
    assert default_calls[0][2] == 42
    assert custom_calls[0][2] == 42


def test_none_seed_is_forwarded_for_package_randomness() -> None:
    provider, calls, _ = make_provider()

    provider.build_level(2, None)

    assert calls[0][2] is None


def test_package_output_becomes_immutable_level_data_and_reads_exit() -> None:
    provider, _, generators = make_provider()

    level = provider.build_level(1, 42)

    assert isinstance(level, LevelData)
    assert isinstance(level.walls, tuple)
    assert all(isinstance(row, tuple) for row in level.walls)
    assert all(isinstance(mask, int) for row in level.walls for mask in row)
    assert generators[0].exit_was_read


def test_generated_positions_are_distinct_and_reachable() -> None:
    provider, _, _ = make_provider()

    first = provider.build_level(1, 42)
    second = provider.build_level(1, 42)

    assert first == second
    non_super_positions = (
        [first.player_spawn]
        + list(first.ghost_spawns)
        + list(first.pacgums)
    )
    assert len(non_super_positions) == len(set(non_super_positions))
    assert set(first.ghost_spawns) == set(first.super_pacgums)
    validate_level_data(first)


def test_player_starts_in_center_and_corner_items_are_grouped() -> None:
    provider, _, _ = make_provider()

    level = provider.build_level(1, 42)

    assert level.player_spawn == (3, 3)
    assert level.ghost_spawns == (
        (0, 0),
        (6, 0),
        (0, 6),
        (6, 6),
    )
    assert level.super_pacgums == {
        (0, 0),
        (6, 0),
        (0, 6),
        (6, 6),
    }


def test_isolated_cells_are_never_used_for_spawns_or_pickups() -> None:
    isolated_cell = (3, 3)
    maze = open_walls(isolated=frozenset({isolated_cell}))
    provider, _, _ = make_provider(maze=maze)

    level = provider.build_level(1, 42)

    used_positions = (
        {level.player_spawn}
        | set(level.ghost_spawns)
        | set(level.pacgums)
        | set(level.super_pacgums)
    )
    assert isolated_cell not in used_positions


def test_pickups_fill_every_reachable_non_spawn_cell() -> None:
    provider, _, _ = make_provider(make_config(pacgum_count=6))

    level = provider.build_level(1, 42)

    expected_pickup_count = (
        7 * 7
        - 1
    )
    pickups = level.pacgums | level.super_pacgums
    assert len(pickups) == expected_pickup_count
    assert pickups == {
        (x, y)
        for y in range(7)
        for x in range(7)
        if (x, y) != level.player_spawn
    }


@pytest.mark.parametrize(
    "bad_maze",
    [
        open_walls(7, 6),
        [row if index != 1 else row[:-1]
         for index, row in enumerate(open_walls())],
        [
            [
                16 if (x, y) == (1, 1) else value
                for x, value in enumerate(row)
            ]
            for y, row in enumerate(open_walls())
        ],
        [
            [
                True if (x, y) == (1, 1) else value
                for x, value in enumerate(row)
            ]
            for y, row in enumerate(open_walls())
        ],
        [
            [value & ~1 if (x, y) == (1, 0) else value
             for x, value in enumerate(row)]
            for y, row in enumerate(open_walls())
        ],
        [
            [value | 2 if (x, y) == (1, 1) else value
             for x, value in enumerate(row)]
            for y, row in enumerate(open_walls())
        ],
    ],
)
def test_invalid_package_wall_output_is_rejected(
    bad_maze: list[list[int]],
) -> None:
    provider, _, _ = make_provider(maze=bad_maze)

    with pytest.raises(ValueError):
        provider.build_level(1, 42)


def test_invalid_configured_dimensions_are_rejected() -> None:
    config = make_config(width=0)
    provider, _, _ = make_provider(config)

    with pytest.raises(ValueError, match="positive int"):
        provider.build_level(1, config.seed)


def test_disconnected_entry_component_without_four_ghost_cells_is_rejected(
) -> None:
    maze = open_walls()

    def close_edge(x: int, y: int, nx: int, ny: int) -> None:
        if nx == x + 1:
            maze[y][x] |= 2
            maze[ny][nx] |= 8
        elif nx == x - 1:
            maze[y][x] |= 8
            maze[ny][nx] |= 2
        elif ny == y + 1:
            maze[y][x] |= 4
            maze[ny][nx] |= 1
        else:
            maze[y][x] |= 1
            maze[ny][nx] |= 4

    for neighbor in ((1, 0), (1, 2), (0, 1)):
        close_edge(1, 1, *neighbor)
    for neighbor in ((2, 0), (3, 1), (2, 2)):
        close_edge(2, 1, *neighbor)

    provider, _, _ = make_provider(maze=maze)

    with pytest.raises(ValueError, match="fewer than four"):
        provider.build_level(1, 42)


def test_validation_rejects_disconnected_or_overlapping_level_data() -> None:
    provider, _, _ = make_provider()
    level = provider.build_level(1, 42)

    disconnected_walls = [list(row) for row in level.walls]
    for row in disconnected_walls:
        row[0] |= 2
        row[1] |= 8
    disconnected = replace(
        level,
        walls=tuple(tuple(row) for row in disconnected_walls),
    )
    with pytest.raises(ValueError, match="not reachable"):
        validate_level_data(disconnected)

    overlapping = replace(
        level,
        pacgums=frozenset({level.ghost_spawns[0]}),
    )
    with pytest.raises(ValueError, match="overlap"):
        validate_level_data(overlapping)

    missing_pickup = replace(
        level,
        pacgums=frozenset(set(level.pacgums) - {min(level.pacgums)}),
    )
    with pytest.raises(ValueError, match="cover every reachable"):
        validate_level_data(missing_pickup)
