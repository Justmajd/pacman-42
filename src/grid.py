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
