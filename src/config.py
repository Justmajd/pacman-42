import json
import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class LevelConfig:
    width: int = 15
    height: int = 15


@dataclass(frozen=True)
class GameConfig:
    highscore_filename: str = "highscore.json"
    levels: tuple[LevelConfig, ...] = field(
        default_factory=lambda: tuple(LevelConfig() for _ in range(10))
    )
    lives: int = 3
    pacgum_count: int = 42
    points_per_pacgum: int = 10
    points_per_super_pacgum: int = 50
    points_per_ghost: int = 200
    seed: int = 42
    level_max_time: int = 90
    frightened_duration: float = 6.0


def read_config_file(path: str) -> dict[str, object]:
    text: list[str] = []
    with open(path, mode="r", encoding="utf-8") as file:
        for line in file:
            line = line.strip() 
            if not line or line.startswith("#"):
                continue
            text.append(line)
    final_str = "".join(text)
    try:
        result = json.loads(final_str)
    except json.JSONDecodeError:
        raise ValueError("malformed JSON")
    if isinstance(result, dict):
        return result
    raise ValueError("configuration root must be a JSON object")


def load_config(path: str) -> GameConfig:
    config_json = read_config_file(path=path)
    try:
        lives = config_json['lives']
    except KeyError:
        logger.warning("Missing 'lives' in config, using default 3")
        lives = 3
    if (
        isinstance(lives, bool)
        or not isinstance(lives, int)
        or lives < 1
    ):
        logger.warning(
            "Invalid 'lives' value (%r), fallback to 3", lives
        )
        lives = 3
    try:
        points_per_pacgum = config_json['points_per_pacgum']
    except KeyError:
        logger.warning(
            "Missing 'points_per_pacgum' in config, using default 10"
        )
        points_per_pacgum = 10
    if (
        isinstance(points_per_pacgum, bool)
        or not isinstance(points_per_pacgum, int)
        or points_per_pacgum < 1
    ):
        logger.warning(
            "Invalid 'points_per_pacgum' value (%r), fallback to 10",
            points_per_pacgum,
        )
        points_per_pacgum = 10
    try:
        points_per_super_pacgum = config_json['points_per_super_pacgum']
    except KeyError:
        logger.warning(
            "Missing 'points_per_super_pacgum' in config, using default 50"
        )
        points_per_super_pacgum = 50
    if (
        isinstance(points_per_super_pacgum, bool)
        or not isinstance(points_per_super_pacgum, int)
        or points_per_super_pacgum < 1
    ):
        logger.warning(
            "Invalid 'points_per_super_pacgum' value (%r), fallback to 50",
            points_per_super_pacgum,
        )
        points_per_super_pacgum = 50
    try:
        points_per_ghost = config_json['points_per_ghost']
    except KeyError:
        logger.warning(
            "Missing 'points_per_ghost' in config, using default 200"
        )
        points_per_ghost = 200
    if (
        isinstance(points_per_ghost, bool)
        or not isinstance(points_per_ghost, int)
        or points_per_ghost < 1
    ):
        logger.warning(
            "Invalid 'points_per_ghost' value (%r), fallback to 200",
            points_per_ghost,
        )
        points_per_ghost = 200
    try:
        seed = config_json['seed']
    except KeyError:
        logger.warning("Missing 'seed' in config, using default 42")
        seed = 42
    if isinstance(seed, bool) or not isinstance(seed, int):
        logger.warning("Invalid 'seed' value (%r), fallback to 42", seed)
        seed = 42
    try:
        level_max_time = config_json['level_max_time']
    except KeyError:
        logger.warning(
            "Missing 'level_max_time' in config, using default 90"
        )
        level_max_time = 90
    if (
        isinstance(level_max_time, bool)
        or not isinstance(level_max_time, int)
        or level_max_time < 60
    ):
        logger.warning(
            "Invalid 'level_max_time' value (%r), fallback to 90",
            level_max_time,
        )
        level_max_time = 90
    try:
        pacgum_count = config_json['pacgum_count']
    except KeyError:
        logger.warning(
            "Missing 'pacgum_count' in config, using default 42"
        )
        pacgum_count = 42
    if (
        isinstance(pacgum_count, bool)
        or not isinstance(pacgum_count, int)
        or pacgum_count < 1
    ):
        logger.warning(
            "Invalid 'pacgum_count' value (%r), fallback to 42",
            pacgum_count,
        )
        pacgum_count = 42
    try:
        highscore_filename = config_json['highscore_filename']
    except KeyError:
        logger.warning(
            "Missing 'highscore_filename' in config, "
            "using default 'highscore.json'"
        )
        highscore_filename = "highscore.json"
    if not isinstance(highscore_filename, str) or not highscore_filename:
        logger.warning(
            "Invalid 'highscore_filename' value (%r), "
            "fallback to 'highscore.json'",
            highscore_filename,
        )
        highscore_filename = "highscore.json"
    try:
        levels = config_json['levels']
    except KeyError:
        logger.warning("Missing 'levels' in config, using empty list")
        levels = []
    if not isinstance(levels, list):
        logger.warning("Invalid 'levels' type, fallback to empty list")
        levels = []
    try:
        frightened_duration = config_json['frightened_duration']
    except KeyError:
        logger.warning("Missing 'frightened_duration' in config, using default 6.0")
        frightened_duration = 6.0
    if (
        isinstance(frightened_duration, bool)
        or not isinstance(frightened_duration, (float,int))
        or frightened_duration <= 0 
    ):
        logger.warning(
            "Invalid 'frightened_duration' value (%r), fallback to 6.0", frightened_duration
        )
        frightened_duration = 6.0
    level_config: list[LevelConfig] = []
    for verlevel in levels:
        if isinstance(verlevel, dict):
            try:
                width = verlevel['width']
            except KeyError:
                logger.warning("Missing 'width' in level, using default 15")
                width = 15
            if (
                isinstance(width, bool)
                or not isinstance(width, int)
                or width < 7
            ):
                logger.warning(
                    "Invalid 'width' (%r) in level, fallback to 15",
                    width,
                )
                width = 15
            try:
                height = verlevel['height']
            except KeyError:
                logger.warning("Missing 'height' in level, using default 15")
                height = 15
            if (
                isinstance(height, bool)
                or not isinstance(height, int)
                or height < 7
            ):
                logger.warning(
                    "Invalid 'height' (%r) in level, fallback to 15",
                    height,
                )
                height = 15
            level_config.append(LevelConfig(width=width, height=height))
        else:
            logger.warning(
                "Level entry is not a dict (%r), using default LevelConfig",
                verlevel,
            )
            level_config.append(LevelConfig())
        
    if len(level_config) < 10:
        remaining_num = 10 - len(level_config)
        logger.warning(
            "Levels count (%d) is less than 10; padding %d default levels",
            len(level_config),
            remaining_num,
        )
        for _ in range(remaining_num):
            level_config.append(LevelConfig())

    game_config = GameConfig(
        highscore_filename=highscore_filename,
        levels=tuple(level_config),
        lives=lives,
        pacgum_count=pacgum_count,
        points_per_pacgum=points_per_pacgum,
        points_per_super_pacgum=points_per_super_pacgum,
        points_per_ghost=points_per_ghost,
        seed=seed,
        level_max_time=level_max_time,
        frightened_duration=frightened_duration,
    )
    return game_config
