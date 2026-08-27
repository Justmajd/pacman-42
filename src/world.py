from src.contracts import LevelData, Position
from enum import Enum

class World:
    def __init__(
        self,
        level: LevelData,
    ) -> None:
        self.walls = level.walls
        self.pacgums: set[Position] = set(level.pacgums)
        self.super_pacgums: set[Position] = set(level.super_pacgums)
        self.player_position = level.player_spawn
        self.ghosts: list[Position] = list(level.ghost_spawns)

    def consume_pickup(self) -> str | None:
        if self.player_position in self.pacgums:
            self.pacgums.remove(self.player_position)
            return "pacgum"
        elif self.player_position in self.super_pacgums:
            self.super_pacgums.remove(self.player_position)
            return "super_pacgum"
        else:
            return None

    def player_ghost_collision(self) -> str | None:
        if self.player_position in self.ghosts:
            return "player collided with the ghost"
        else:
            return None

