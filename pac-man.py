import sys
from src.config import load_config
from src.app import run_app


def main() -> int:
    if len(sys.argv) != 2:
        print("Error: user didn't pass config file")
        return 1
    config_path = sys.argv[1]
    try:
        game_config = load_config(config_path)
    except ValueError as e:
        print(e)
        return 1
    except OSError:
        print("Error: could not open the configuration file.")
        return 1
    return run_app(game_config)


if __name__ == "__main__":
    sys.exit(main())
