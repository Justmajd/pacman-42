from collections import deque
from typing import Any, Callable, overload

from mazegenerator import MazeGenerator

from src.config import GameConfig
from src.contracts import LevelData, Position


NORTH = 1
EAST = 2
SOUTH = 4
WEST = 8

_DIRECTIONS: tuple[tuple[int, int, int], ...] = (
    (0, -1, NORTH),
    (1, 0, EAST),
    (0, 1, SOUTH),
    (-1, 0, WEST),
)

GeneratorFactory = Callable[..., Any]
_SEED_NOT_PROVIDED = object()


def _is_valid_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _validate_dimensions(width: object, height: object) -> None:
    if (
        not isinstance(width, int)
        or isinstance(width, bool)
        or width <= 0
    ):
        raise ValueError(f"Level width must be a positive int, got {width!r}")
    if (
        not isinstance(height, int)
        or isinstance(height, bool)
        or height <= 0
    ):
        raise ValueError(
            f"Level height must be a positive int, got {height!r}"
        )


def _validate_coordinate(
    coordinate: object,
    name: str,
    width: int,
    height: int,
) -> Position:
    if not isinstance(coordinate, (tuple, list)):
        raise ValueError(f"'{name}' must contain exactly 2 integers")
    if len(coordinate) != 2:
        raise ValueError(f"'{name}' must contain exactly 2 integers")

    x, y = coordinate
    if not _is_valid_int(x) or not _is_valid_int(y):
        raise ValueError(f"Coordinates in '{name}' must be ints")
    if not (0 <= x < width and 0 <= y < height):
        raise ValueError(
            f"Coordinate ({x}, {y}) in '{name}' is out of bounds "
            f"({width}x{height})"
        )
    return x, y


def _validate_wall_grid(
    width: int,
    height: int,
    walls: object,
) -> tuple[tuple[int, ...], ...]:
    if not isinstance(walls, (tuple, list)):
        raise ValueError("'walls' must be a list or tuple of rows")
    if len(walls) != height:
        raise ValueError(
            f"Wall-grid height {len(walls)} does not match level height "
            f"{height}"
        )

    normalized_rows: list[tuple[int, ...]] = []
    for row_index, row in enumerate(walls):
        if not isinstance(row, (tuple, list)):
            raise ValueError(f"Wall row {row_index} must be a list or tuple")
        if len(row) != width:
            raise ValueError(
                f"Wall row {row_index} has length {len(row)}, expected "
                f"{width}"
            )

        normalized_row: list[int] = []
        for column_index, mask in enumerate(row):
            if not _is_valid_int(mask) or not 0 <= mask <= 15:
                raise ValueError(
                    f"Wall mask at ({column_index}, {row_index}) must be "
                    "a non-boolean int in 0..15"
                )
            normalized_row.append(mask)
        normalized_rows.append(tuple(normalized_row))

    normalized_walls = tuple(normalized_rows)

    for y in range(height):
        for x in range(width):
            mask = normalized_walls[y][x]
            if y == 0 and not mask & NORTH:
                raise ValueError(
                    f"Top boundary at ({x}, {y}) can be crossed"
                )
            if y == height - 1 and not mask & SOUTH:
                raise ValueError(
                    f"Bottom boundary at ({x}, {y}) can be crossed"
                )
            if x == 0 and not mask & WEST:
                raise ValueError(
                    f"Left boundary at ({x}, {y}) can be crossed"
                )
            if x == width - 1 and not mask & EAST:
                raise ValueError(
                    f"Right boundary at ({x}, {y}) can be crossed"
                )

            if x + 1 < width:
                right_mask = normalized_walls[y][x + 1]
                if bool(mask & EAST) != bool(right_mask & WEST):
                    raise ValueError(
                        f"Reciprocal east/west walls disagree between "
                        f"({x}, {y}) and ({x + 1}, {y})"
                    )
            if y + 1 < height:
                below_mask = normalized_walls[y + 1][x]
                if bool(mask & SOUTH) != bool(below_mask & NORTH):
                    raise ValueError(
                        f"Reciprocal north/south walls disagree between "
                        f"({x}, {y}) and ({x}, {y + 1})"
                    )

    return normalized_walls


def _position_collection(
    value: object,
    name: str,
    width: int,
    height: int,
) -> tuple[Position, ...]:
    if not isinstance(value, (tuple, list, set, frozenset)):
        raise ValueError(f"'{name}' must be a collection of coordinates")
    return tuple(
        _validate_coordinate(position, name, width, height)
        for position in value
    )


def _reachable_cells(
    walls: tuple[tuple[int, ...], ...],
    width: int,
    height: int,
    start: Position,
) -> frozenset[Position]:
    reachable: set[Position] = {start}
    pending: deque[Position] = deque([start])

    while pending:
        x, y = pending.popleft()
        current_mask = walls[y][x]
        for dx, dy, wall_bit in _DIRECTIONS:
            neighbor = x + dx, y + dy
            nx, ny = neighbor
            if not (0 <= nx < width and 0 <= ny < height):
                continue
            if current_mask & wall_bit:
                continue
            if neighbor not in reachable:
                reachable.add(neighbor)
                pending.append(neighbor)

    return frozenset(reachable)


def _manhattan_distance(first: Position, second: Position) -> int:
    return abs(first[0] - second[0]) + abs(first[1] - second[1])


def validate_level_data(level: LevelData) -> None:
    """Validate every invariant required by the gameplay consumers."""

    _validate_dimensions(level.width, level.height)
    width, height = level.width, level.height
    walls = _validate_wall_grid(width, height, level.walls)

    player_spawn = _validate_coordinate(
        level.player_spawn, "player_spawn", width, height
    )
    ghost_spawns = _position_collection(
        level.ghost_spawns, "ghost_spawns", width, height
    )
    if len(ghost_spawns) != 4:
        raise ValueError(
            f"'ghost_spawns' must contain exactly four entries, got "
            f"{len(ghost_spawns)}"
        )
    if len(set(ghost_spawns)) != 4:
        raise ValueError("'ghost_spawns' must contain four distinct cells")

    pacgums = _position_collection(
        level.pacgums, "pacgums", width, height
    )
    super_pacgums = _position_collection(
        level.super_pacgums, "super_pacgums", width, height
    )
    pacgum_set = set(pacgums)
    super_pacgum_set = set(super_pacgums)
    ghost_set = set(ghost_spawns)

    if not pacgum_set:
        raise ValueError("Level must contain at least one pacgum")
    if not super_pacgum_set:
        raise ValueError("Level must contain at least one super-pacgum")

    if player_spawn in ghost_set:
        raise ValueError(
            f"Player spawn {player_spawn} overlaps with a ghost spawn"
        )
    if pacgum_set & super_pacgum_set:
        raise ValueError("Pacgums and super-pacgums overlap")

    all_spawns = {player_spawn} | ghost_set
    if pacgum_set & all_spawns:
        raise ValueError("Pacgums overlap with a player or ghost spawn")
    if player_spawn in super_pacgum_set:
        raise ValueError(
            "Super-pacgums overlap with the player spawn"
        )
    if super_pacgum_set != ghost_set:
        raise ValueError(
            "Each ghost spawn must share its cell with one super-pacgum"
        )

    all_positions = {
        "player_spawn": (player_spawn,),
        "ghost_spawns": ghost_spawns,
        "pacgums": tuple(pacgum_set),
        "super_pacgums": tuple(super_pacgum_set),
    }
    for name, positions in all_positions.items():
        for x, y in positions:
            if walls[y][x] == 15:
                raise ValueError(
                    f"{name} contains isolated 15 cell at ({x}, {y})"
                )

    reachable = _reachable_cells(walls, width, height, player_spawn)
    for name, positions in all_positions.items():
        for position in positions:
            if position not in reachable:
                raise ValueError(
                    f"{name} position {position} is not reachable from "
                    f"player spawn {player_spawn}"
                )

    usable_reachable = {
        position
        for position in reachable
        if walls[position[1]][position[0]] != 15
    }
    expected_pickup_cells = usable_reachable - {player_spawn}
    actual_pickup_cells = pacgum_set | super_pacgum_set
    if actual_pickup_cells != expected_pickup_cells:
        missing = expected_pickup_cells - actual_pickup_cells
        extra = actual_pickup_cells - expected_pickup_cells
        raise ValueError(
            "Pickups must cover every reachable non-spawn cell "
            f"(missing={len(missing)}, extra={len(extra)})"
        )


class MazeGeneratorProvider:
    def __init__(
        self,
        config: GameConfig,
        generator_factory: GeneratorFactory = MazeGenerator,
    ) -> None:
        self.config = config
        self.pacgum_count = config.pacgum_count
        self.generator_factory = generator_factory

    def _level_config(self, level_number: int) -> tuple[int, int]:
        if not _is_valid_int(level_number) or level_number < 1:
            raise ValueError(
                f"Level number must be a positive int, got {level_number!r}"
            )
        if level_number > len(self.config.levels):
            raise ValueError(
                f"Level number {level_number} is not configured; only "
                f"{len(self.config.levels)} levels are available"
            )

        level_config = self.config.levels[level_number - 1]
        width, height = level_config.width, level_config.height
        _validate_dimensions(width, height)
        return width, height

    @staticmethod
    def _resolve_seed(seed: int | None, level_number: int) -> int | None:
        if level_number == 1:
            return 42
        if seed is None:
            return None
        if isinstance(seed, bool) or not isinstance(seed, int):
            raise ValueError(
                f"Seed must be an int or None, got {seed!r}"
            )
        return seed + level_number - 1

    @overload
    def build_level(self, level_number: int) -> LevelData:
        ...

    @overload
    def build_level(
        self,
        level_number: int,
        seed: int | None,
    ) -> LevelData:
        ...

    def build_level(
        self,
        level_number: int,
        seed: object = _SEED_NOT_PROVIDED,
    ) -> LevelData:
        width, height = self._level_config(level_number)
        if not _is_valid_int(self.pacgum_count):
            raise ValueError(
                "Configured pacgum_count must be a positive int"
            )
        if self.pacgum_count < 1:
            raise ValueError(
                "Configured pacgum_count must be a positive int"
            )

        if seed is _SEED_NOT_PROVIDED:
            base_seed: int | None = self.config.seed
        elif seed is None or (
            isinstance(seed, int) and not isinstance(seed, bool)
        ):
            base_seed = seed
        else:
            raise ValueError(
                f"Seed must be an int or None, got {seed!r}"
            )

        resolved_seed = self._resolve_seed(base_seed, level_number)
        generator = self.generator_factory(
            size=(width, height),
            perfect=False,
            seed=resolved_seed,
        )

        walls = _validate_wall_grid(width, height, generator.maze)
        maze_entry = _validate_coordinate(
            generator.maze_entry,
            "maze_entry",
            width,
            height,
        )
        _validate_coordinate(generator.maze_exit, "maze_exit", width, height)

        if walls[maze_entry[1]][maze_entry[0]] == 15:
            raise ValueError(
                f"maze_entry {maze_entry} is an isolated 15 cell"
            )

        reachable = _reachable_cells(walls, width, height, maze_entry)
        usable_cells = {
            position
            for position in reachable
            if walls[position[1]][position[0]] != 15
        }
        center = (width // 2, height // 2)
        player_spawn = min(
            usable_cells,
            key=lambda position: (
                _manhattan_distance(position, center),
                position[1],
                position[0],
            ),
        )

        remaining_cells = usable_cells - {player_spawn}
        if len(remaining_cells) < 5:
            raise ValueError(
                "Maze has fewer than four valid reachable corner cells "
                "and one pacgum cell"
            )
        corners = (
            (0, 0),
            (width - 1, 0),
            (0, height - 1),
            (width - 1, height - 1),
        )
        super_pacgum_list: list[Position] = []
        for corner in corners:
            selected = min(
                remaining_cells,
                key=lambda position: (
                    _manhattan_distance(position, corner),
                    position[1],
                    position[0],
                ),
            )
            super_pacgum_list.append(selected)
            remaining_cells.remove(selected)

        ghost_spawns: tuple[
            Position,
            Position,
            Position,
            Position,
        ] = (
            super_pacgum_list[0],
            super_pacgum_list[1],
            super_pacgum_list[2],
            super_pacgum_list[3],
        )

        pacgum_list = sorted(
            remaining_cells,
            key=lambda position: (position[1], position[0]),
        )
        pacgums = frozenset(pacgum_list)
        super_pacgums = frozenset(super_pacgum_list)

        level = LevelData(
            width=width,
            height=height,
            walls=walls,
            player_spawn=player_spawn,
            ghost_spawns=ghost_spawns,
            pacgums=pacgums,
            super_pacgums=super_pacgums,
        )
        validate_level_data(level)
        return level
