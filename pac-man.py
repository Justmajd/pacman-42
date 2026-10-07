import sys
from src import load_config


def main() -> int:
    if len(sys.argv) != 2:
        print("Error: expected exactly one configuration file argument.")
        return 1
    config_path = sys.argv[1]
    try:
        game_config = load_config(config_path)
    except ValueError as e:
        print(f"Error: {e}")
        return 1
    except OSError:
        print("Error: could not open the configuration file.")
        return 1
    try:
        from src.app import run_app

        return run_app(game_config)
    except KeyboardInterrupt:
        import pygame

        pygame.quit()
        print("Game interrupted.")
        return 0
    except ValueError as e:
        print(f"Error: {e}")
        return 1
    except ModuleNotFoundError as e:
        print(f"Error: missing required dependency '{e.name}'.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
