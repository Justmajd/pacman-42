from src.contracts import Position, Direction, GridQuery
from dataclasses import dataclass
import random


@dataclass
class Ghost:
    position: Position
    direction: Direction
    spawn: Position
    active: bool
    respawn_delay: float
    progress: float = 0.0
    speed: float = 6.0
    ghost_id: int = 0
    scatter_target: Position = (0, 0)
    is_eaten: bool = False
    OPPOSITE = {Direction.UP: Direction.DOWN,
                Direction.DOWN: Direction.UP,
                Direction.LEFT: Direction.RIGHT,
                Direction.RIGHT: Direction.LEFT}
    CLYDE_SHY_DISTANCE = 8

    def kill(self, respawn_delay: float) -> None:
        self.active = False
        self.respawn_delay = respawn_delay

    def compute_target(self, player_pos: Position, player_facing: Direction,
                        blinky_pos: Position) -> Position:
        if self.is_eaten:
            return self.spawn

        if self.ghost_id == 0:
            return player_pos

        if self.ghost_id == 1:
            return (player_pos[0] + player_facing.value[0] * 4,
                    player_pos[1] + player_facing.value[1] * 4)

        if self.ghost_id == 2:
            ahead = (player_pos[0] + player_facing.value[0] * 2,
                     player_pos[1] + player_facing.value[1] * 2)
            return (2 * ahead[0] - blinky_pos[0], 2 * ahead[1] - blinky_pos[1])

        distance = abs(self.position[0] - player_pos[0]) + abs(self.position[1] - player_pos[1])
        if distance > self.CLYDE_SHY_DISTANCE:
            return player_pos
        return self.scatter_target

    def _pick_direction(self, grid: GridQuery, target: Position,
                         frightened: bool, rng: random.Random,
                         occupied: frozenset[Position] = frozenset()) -> Direction:
        directions = [Direction.UP, Direction.DOWN,
                      Direction.LEFT, Direction.RIGHT]
        walkable_directions = []

        for d in directions:
            candidate = (self.position[0] + d.value[0],
                         self.position[1] + d.value[1])
            if grid.is_walkable(self.position, candidate):
                walkable_directions.append(d)

        non_reversing_directions = list(
            filter(lambda d: d != self.OPPOSITE.get(self.direction),
                   walkable_directions))

        if not non_reversing_directions:
            candidate_directions = walkable_directions
        else:
            candidate_directions = non_reversing_directions

        if len(candidate_directions) == 0:
            return Direction.NONE

        non_colliding_directions = [
            d for d in candidate_directions
            if (self.position[0] + d.value[0],
                self.position[1] + d.value[1]) not in occupied
        ]
        if non_colliding_directions:
            candidate_directions = non_colliding_directions

        distances = {}
        for d in candidate_directions:
            candidate = (self.position[0] + d.value[0],
                         self.position[1] + d.value[1])
            distances[d] = (abs(candidate[0] - target[0])
                            + abs(candidate[1] - target[1]))

        if frightened:
            target_distance = max(distances.values())
        else:
            target_distance = min(distances.values())

        tied_directions = []
        for key, value in distances.items():
            if value == target_distance:
                tied_directions.append(key)

        return rng.choice(tied_directions)

    def update(self, dt: float, grid: GridQuery,
               target: Position, frightened: bool,
               rng: random.Random,
               occupied: frozenset[Position] = frozenset()) -> None:
        if not self.active:
            self.respawn_delay -= dt

            if self.respawn_delay <= 0:
                self.active = True
                self.position = self.spawn
                self.direction = Direction.NONE
                self.progress = 0.0
                self.respawn_delay = 0.0
            return

        if self.direction is Direction.NONE:
            self.direction = self._pick_direction(grid, target, frightened, rng, occupied)
            if self.direction is Direction.NONE:
                return

        self.progress += self.speed * dt
        while self.progress >= 1.0:
            self.progress -= 1.0
            self.position = (self.position[0] + self.direction.value[0],
                              self.position[1] + self.direction.value[1])
            self.direction = self._pick_direction(grid, target, frightened, rng, occupied)
            if self.direction is Direction.NONE:
                self.progress = 0.0
                break
        if self.is_eaten and self.position == self.spawn:
            self.is_eaten = False

    @property
    def render_position(self) -> tuple[float, float]:
        return (self.position[0] + self.direction.value[0] * self.progress,
                self.position[1] + self.direction.value[1] * self.progress)