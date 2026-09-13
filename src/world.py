from src.contracts import LevelData, Position
from src.contracts import WorldEvent

COLLISION_DISTANCE = 0.5


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

    def consume_pickup(self) -> tuple[WorldEvent, ...]:
        events: list[WorldEvent] = []
        if self.player_position in self.pacgums:
            self.pacgums.remove(self.player_position)
            events.append(WorldEvent.PACGUM_EATEN)
            if len(self.pacgums) <= 0:
                events.append(WorldEvent.LEVEL_CLEARED)
            return tuple(events)
        elif self.player_position in self.super_pacgums:
            self.super_pacgums.remove(self.player_position)
            events.append(WorldEvent.SUPER_PACGUM_EATEN)
            return tuple(events)
        return tuple(events)

    def player_ghost_collision(
        self,
        player_render_position: tuple[float, float],
        ghost_render_positions: list[tuple[float, float]],
    ) -> int | None:
        px, py = player_render_position
        for ghost_index, (gx, gy) in enumerate(ghost_render_positions):
            if abs(px - gx) <= COLLISION_DISTANCE and abs(py - gy) <= COLLISION_DISTANCE:
                return ghost_index
        return None
