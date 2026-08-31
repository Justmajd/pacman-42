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
    OPPOSITE = {Direction.UP: Direction.DOWN,
                Direction.DOWN: Direction.UP,
                Direction.LEFT: Direction.RIGHT,
                Direction.RIGHT: Direction.LEFT}

    def kill(self, respawn_delay: float) -> None:
        self.active = False
        self.respawn_delay = respawn_delay

    def update(self, dt: float, grid: GridQuery,
               target: Position, frightened: bool,
               rng: random.Random) -> None:
        if not self.active:
            self.respawn_delay -= dt

            if self.respawn_delay <= 0:
                self.active = True
                self.position = self.spawn
                self.direction = Direction.NONE
                self.respawn_delay = 0.0
        else:
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
                return

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

            final_direction = rng.choice(tied_directions)

            self.direction = final_direction
            self.position = (self.position[0] + final_direction.value[0],
                             self.position[1] + final_direction.value[1])