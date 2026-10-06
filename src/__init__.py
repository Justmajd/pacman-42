from src.config import GameConfig, load_config


def run_app(config: GameConfig) -> int:
	from src.app import run_app as start_app

	return start_app(config)


__all__ = ["run_app", "GameConfig", "load_config"]
