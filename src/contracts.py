from dataclasses import dataclass
from enum import Enum, auto
from typing import Protocol


Position = tuple[int, int]


class GameState(Enum):
    MENU = auto()
    PLAYING = auto()
    PAUSED = auto()
    GAME_OVER = auto()
    VICTORY = auto()
    NAME_ENTRY = auto()


@dataclass(frozen=True)
class LevelData:
    width: int
    height: int
    walls: tuple[tuple[int, ...], ...]
    player_spawn: Position
    ghost_spawns: tuple[Position, Position, Position, Position]
    pacgums: frozenset[Position]
    super_pacgums: frozenset[Position]


class MazeProvider(Protocol):
    def build_level(
        self,
        level_number: int,
        seed: int | None,
    ) -> LevelData:
        ...

class Direction(Enum):
    UP = (-1, 0)
    DOWN = (1, 0)
    LEFT = (0, -1)
    RIGHT = (0, 1)
    NONE = (0, 0)

class WorldEvent(Enum):
    ...


class GridQuery(Protocol):
    def is_walkable(self, position: Position) ->bool:
        ...