from src.contracts import LevelData, Position


class Grid:
    def __init__(self, level: LevelData) -> None:
        self.width = level.width
        self.height = level.height
        self.walls = level.walls

    def is_walkable(
        self,
        start: Position,
        end: Position,
    ) -> bool:
        sx, sy = start
        ex, ey = end
        if not (
            0 <= ex < self.width
            and 0 <= ey < self.height
            and 0 <= sx < self.width
            and 0 <= sy < self.height
        ):
            return False
        if (sx == ex and (ey == sy - 1)):
            if (self.walls[sy][sx] & 1 == 1):
                return False
            else:
                return True
        elif (sx == ex and (ey == sy + 1)):
            if (self.walls[sy][sx] & 4 == 4):
                return False
            else:
                return True
        elif (sy == ey and (ex == sx + 1)):
            if (self.walls[sy][sx] & 2 == 2):
                return False
            else:
                return True
        elif (sy == ey and (ex == sx - 1)):
            if (self.walls[sy][sx] & 8 == 8):
                return False
            else:
                return True
        else:
            return False

    def neighbours(
        self,
        position: Position,
    ) -> tuple[Position, ...]:
        walkable_neighbours: list[Position] = []
        cx, cy = position
        nx, ny = cx, cy - 1
        sx, sy = cx, cy + 1
        ex, ey = cx + 1, cy
        wx, wy = cx - 1, cy
        if self.is_walkable(position, (nx, ny)):
            walkable_neighbours.append((nx, ny))
        if self.is_walkable(position, (sx, sy)):
            walkable_neighbours.append((sx, sy))
        if self.is_walkable(position, (ex, ey)):
            walkable_neighbours.append((ex, ey))
        if self.is_walkable(position, (wx, wy)):
            walkable_neighbours.append((wx, wy))

        return tuple(walkable_neighbours)
