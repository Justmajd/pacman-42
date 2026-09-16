from dataclasses import dataclass, field
from src.contracts import Direction
from src.input import key_to_direction
import pygame

SECRET_SEQUENCE: tuple[Direction, ...] = (
    Direction.UP, Direction.UP,
    Direction.DOWN, Direction.DOWN,
    Direction.LEFT, Direction.RIGHT,
    Direction.LEFT, Direction.RIGHT,
)


@dataclass
class CheatController:
    enabled: bool = False
    invincible: bool = False
    ghosts_frozen: bool = False
    speed_boosted: bool = False
    _direction_buffer: list[Direction] = field(
        default_factory=list, repr=False
    )
    _extra_life_requested: bool = field(
        default=False, repr=False
    )
    _level_skip_requested: bool = field(
        default=False, repr=False
    )

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return

        direction = key_to_direction(event.key)
        if direction is not None:
            self._direction_buffer.append(direction)
            self._direction_buffer = self._direction_buffer[-len(
                SECRET_SEQUENCE):]
            if tuple(self._direction_buffer) == SECRET_SEQUENCE:
                self._direction_buffer.clear()
                if self.enabled:
                    self.enabled = False
                    self.invincible = False
                    self.ghosts_frozen = False
                    self.speed_boosted = False
                else:
                    self.enabled = True
            return
        else:
            if self.enabled:
                if event.key == pygame.K_F1:
                    self.invincible = not self.invincible
                if event.key == pygame.K_F2:
                    self.ghosts_frozen = not self.ghosts_frozen
                if event.key == pygame.K_F3:
                    self._extra_life_requested = True
                if event.key == pygame.K_F4:
                    self.speed_boosted = not self.speed_boosted
                if event.key == pygame.K_F5:
                    self._level_skip_requested = True

    def consume_extra_life_request(self) -> bool:
        requested = self._extra_life_requested
        self._extra_life_requested = False
        return requested

    def consume_level_skip_request(self) -> bool:
        requested = self._level_skip_requested
        self._level_skip_requested = False
        return requested
