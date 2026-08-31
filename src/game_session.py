from src.config import GameConfig
from src.contracts import GameState
from src.contracts import WorldEvent

class GameSession:
    def __init__(self, config: GameConfig) -> None:
        self.score = 0
        self.lives = config.lives
        self.level = 1
        self.level_time_remaining = config.level_max_time
        self.frightened_time_remaining = 0.0
        self.state : GameState = GameState.PLAYING
        self.config = config

    def update(self, dt: float) -> None:
        if self.state == GameState.PLAYING:
            self.level_time_remaining -= dt
            if self.level_time_remaining <= 0.0:
                self.level_time_remaining = 0.0
            if self.level_time_remaining == 0.0:
                self.state = GameState.GAME_OVER 
            if self.frightened_time_remaining > 0:
                self.frightened_time_remaining -= dt
        if self.frightened_time_remaining <= 0.0:
            self.frightened_time_remaining = 0.0

    def handle_event(self, event: WorldEvent) -> None:
        if event == WorldEvent.PACGUM_EATEN:
            self.score += self.config.points_per_pacgum
        if event == WorldEvent.SUPER_PACGUM_EATEN:
            self.score += self.config.points_per_super_pacgum
            self.frightened_time_remaining = self.config.frightened_duration
        if event == WorldEvent.GHOST_EATEN:
            self.score += self.config.points_per_ghost
        if event == WorldEvent.PLAYER_HIT:
            self.lives -= 1
            if self.lives <= 0:
                self.lives = 0
                self.state = GameState.GAME_OVER
        if event == WorldEvent.LEVEL_CLEARED:
            if self.level < len(self.config.levels):
                self.level += 1
                self.level_time_remaining = self.config.level_max_time
                self.frightened_time_remaining = 0.0
            else:
                self.state = GameState.VICTORY