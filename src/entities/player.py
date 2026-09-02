from src.contracts import Position, Direction, GridQuery
from dataclasses import dataclass

@dataclass
class Player:
    position: Position
    direction: Direction
    requested_direction: Direction
    spawn: Position
    lives: int
    progress: float = 0.0
    speed: float = 6.0
    facing: Direction = Direction.NONE

    def request_direction(self, direction: Direction) -> None:
        self.requested_direction = direction

    def _pick_next_direction(self, grid: GridQuery) -> None:
        candidate = (self.position[0] + self.requested_direction.value[0],
                     self.position[1] + self.requested_direction.value[1])
        if grid.is_walkable(self.position, candidate):
            self.direction = self.requested_direction
            self.facing = self.direction
            return

        fallback = (self.position[0] + self.direction.value[0],
                    self.position[1] + self.direction.value[1])
        if grid.is_walkable(self.position, fallback):
            return

        self.direction = Direction.NONE

    @staticmethod
    def _is_opposite(a: Direction, b: Direction) -> bool:
        return a.value == (-b.value[0], -b.value[1])

    def update(self, grid: GridQuery, dt: float) -> None:
        if (self.direction is not Direction.NONE and self.progress > 0.0
                and self._is_opposite(self.requested_direction, self.direction)):
            self.position = (self.position[0] + self.direction.value[0],
                              self.position[1] + self.direction.value[1])
            self.progress = 1.0 - self.progress
            self.direction = self.requested_direction
            self.facing = self.direction

        if self.direction is Direction.NONE:
            self._pick_next_direction(grid)
            return

        self.progress += self.speed * dt
        while self.progress >= 1.0:
            self.progress -= 1.0
            self.position = (self.position[0] + self.direction.value[0],
                              self.position[1] + self.direction.value[1])
            self._pick_next_direction(grid)
            if self.direction is Direction.NONE:
                self.progress = 0.0
                break

    @property
    def render_position(self) -> tuple[float, float]:
        return (self.position[0] + self.direction.value[0] * self.progress,
                self.position[1] + self.direction.value[1] * self.progress)

    @property
    def is_moving(self) -> bool:
        return self.direction is not Direction.NONE

    def respawn(self) -> None:
        self.position = self.spawn
        self.direction = Direction.NONE
        self.requested_direction = Direction.NONE
        self.facing = Direction.NONE