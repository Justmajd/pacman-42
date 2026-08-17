import json
import logging
from pathlib import Path
from src.contracts import LevelData

logger = logging.getLogger(__name__)


def _is_valid_int(val: object) -> bool:
    return isinstance(val, int) and not isinstance(val, bool)


def _validate_coordinate(
    coord: object,
    name: str,
    width: int,
    height: int,
) -> tuple[int, int]:
    if not isinstance(coord, list):
        raise ValueError(f"Each entry in '{name}' must be a list")
    if len(coord) != 2:
        raise ValueError(
            f"Each entry in '{name}' must contain exactly 2 integers"
        )

    x, y = coord
    if not _is_valid_int(x) or not _is_valid_int(y):
        raise ValueError(
            f"Coordinates in '{name}' must be ints, not booleans"
        )

    if not (0 <= x < width) or not (0 <= y < height):
        raise ValueError(
            f"Coordinate ({x}, {y}) in '{name}' is out of bounds "
            f"({width}x{height})"
        )

    return (x, y)


class StubMazeProvider:
    def build_level(
        self,
        level_number: int,
        seed: int | None,
    ) -> LevelData:
        path = (
            Path(__file__).parent.parent
            / "tests/fixtures/stub_level.json"
        )
        with open(path, "r", encoding="utf-8") as file:
            content = json.load(file)

        if not isinstance(content, dict):
            raise ValueError("valid JSON, but wrong root type")

        try:
            width = content["width"]
        except KeyError:
            logger.warning("Missing 'width' in level, using default 15")
            width = 15

        if not _is_valid_int(width) or width < 7:
            logger.warning(
                "Invalid 'width' (%r) in level, fallback to 15",
                width,
            )
            width = 15

        try:
            height = content["height"]
        except KeyError:
            logger.warning("Missing 'height' in level, using default 15")
            height = 15

        if not _is_valid_int(height) or height < 7:
            logger.warning(
                "Invalid 'height' (%r) in level, fallback to 15",
                height,
            )
            height = 15

        try:
            walls = content["walls"]
        except KeyError:
            raise ValueError("Missing 'walls' in level definition")

        if not isinstance(walls, list):
            raise ValueError("'walls' must be a list")
        if len(walls) != height:
            raise ValueError(
                f"'walls' height ({len(walls)}) does not match "
                f"expected height ({height})"
            )

        walls_list = []
        for row in walls:
            if not isinstance(row, list):
                raise ValueError("A wall row is not a list")
            if len(row) != width:
                raise ValueError(
                    f"Wall row length ({len(row)}) does not match "
                    f"expected width ({width})"
                )
            for val in row:
                if not _is_valid_int(val):
                    raise ValueError(
                        "A bitmask value in 'walls' is not a valid int"
                    )
            walls_list.append(tuple(row))
        final_walls = tuple(walls_list)

        try:
            raw_player_spawn = content["player_spawn"]
        except KeyError:
            raise ValueError("Missing 'player_spawn' in level definition")

        final_player_spawn = _validate_coordinate(
            raw_player_spawn, "player_spawn", width, height
        )

        try:
            raw_ghost_spawns = content["ghost_spawns"]
        except KeyError:
            raise ValueError("Missing 'ghost_spawns' in level definition")

        if not isinstance(raw_ghost_spawns, list):
            raise ValueError("'ghost_spawns' must be a list")
        if len(raw_ghost_spawns) != 4:
            raise ValueError(
                f"'ghost_spawns' must have 4 entries, "
                f"got {len(raw_ghost_spawns)}"
            )

        final_ghost_spawns: tuple[
            tuple[int, int],
            tuple[int, int],
            tuple[int, int],
            tuple[int, int],
        ] = (
            _validate_coordinate(
                raw_ghost_spawns[0], "ghost_spawns", width, height
            ),
            _validate_coordinate(
                raw_ghost_spawns[1], "ghost_spawns", width, height
            ),
            _validate_coordinate(
                raw_ghost_spawns[2], "ghost_spawns", width, height
            ),
            _validate_coordinate(
                raw_ghost_spawns[3], "ghost_spawns", width, height
            ),
        )

        try:
            raw_pacgums = content["pacgums"]
        except KeyError:
            raise ValueError("Missing 'pacgums' in level definition")

        if not isinstance(raw_pacgums, list):
            raise ValueError("'pacgums' must be a list")

        final_pacgums: frozenset[tuple[int, int]] = frozenset(
            _validate_coordinate(p, "pacgums", width, height)
            for p in raw_pacgums
        )

        try:
            raw_super_pacgums = content["super_pacgums"]
        except KeyError:
            raise ValueError("Missing 'super_pacgums' in level definition")

        if not isinstance(raw_super_pacgums, list):
            raise ValueError("'super_pacgums' must be a list")

        final_super_pacgums: frozenset[tuple[int, int]] = frozenset(
            _validate_coordinate(sp, "super_pacgums", width, height)
            for sp in raw_super_pacgums
        )

        if final_player_spawn in final_ghost_spawns:
            raise ValueError(
                f"Player spawn {final_player_spawn} overlaps with ghost"
            )

        pacgum_overlap = final_pacgums & final_super_pacgums
        if pacgum_overlap:
            raise ValueError(
                f"Pacgums and super-pacgums overlap at: {pacgum_overlap}"
            )

        all_spawns = {final_player_spawn} | set(final_ghost_spawns)

        spawn_pacgum_overlap = final_pacgums & all_spawns
        if spawn_pacgum_overlap:
            raise ValueError(
                f"Pacgums overlap with spawn at: {spawn_pacgum_overlap}"
            )

        spawn_super_overlap = final_super_pacgums & all_spawns
        if spawn_super_overlap:
            raise ValueError(
                f"Super-pacgums overlap with spawn at: "
                f"{spawn_super_overlap}"
            )

        return LevelData(
            width=width,
            height=height,
            walls=final_walls,
            player_spawn=final_player_spawn,
            ghost_spawns=final_ghost_spawns,
            pacgums=final_pacgums,
            super_pacgums=final_super_pacgums,
        )
