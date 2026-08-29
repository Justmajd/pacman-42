from src.contracts import Position, Direction, GridQuery
from dataclasses import dataclass

@dataclass
class Player:
    position: Position
    direction: Direction
    requested_direction: Direction
    spawn: Position
    lives: int

    def request_direction(self, direction: Direction) -> None:
        self.requested_direction = direction

    def update(self, grid: GridQuery) -> None:
        candidate = (self.position[0] + self.requested_direction.value[0],
                     self.position[1] + self.requested_direction.value[1])

        if grid.is_walkable(self.position, candidate):
            self.direction = self.requested_direction
            self.position = candidate
        else:
            fallback = (self.position[0] + self.direction.value[0],
            self.position[1] + self.direction.value[1])
            if grid.is_walkable(self.position, fallback):
                self.position = fallback

    def respawn(self) -> None:
        self.position = self.spawn
        self.direction = Direction.NONE
        self.requested_direction = Direction.NONE