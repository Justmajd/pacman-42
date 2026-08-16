import json
from dataclasses import dataclass, field


@dataclass(frozen=True)
class LevelConfig:
    width: int = 15
    height: int = 15


@dataclass(frozen=True)
class GameConfig:
    highscore_filename: str = "highscores.json"
    levels: tuple[LevelConfig, ...] = field(default_factory=lambda: tuple(LevelConfig() for _ in range(10)))
    lives: int = 3
    pacgum_count: int = 42
    points_per_pacgum: int = 10
    points_per_super_pacgum: int = 50
    points_per_ghost: int = 200
    seed: int = 42
    level_max_time: int = 90




def read_config_file(path: str) -> dict[str, object]:
    text: list[str] = []
    with open(path, mode="r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            text.append(line)
    final_str = "".join(text)
    
