*This activity has been created as part of the 42 curriculum by malhodal, omjarada*

# Pac-Man 42

## Description

Pac-Man 42 is a Pac-Man-style game written in Python with Pygame as part of the 42 curriculum.

The goal of the activity is to build a complete playable game while applying modular software design, configuration-driven behavior, procedural maze generation, persistent data storage, packaging, and collaborative project management.

The game includes:

- 10 configurable levels.
- Procedurally generated mazes using the assigned A-Maze-ing package.
- Level 1 generated with the fixed seed `42`.
- Randomized maze generation for later levels.
- Pacgums and super pacgums.
- Four ghosts with chase, scatter, frightened, and eaten behavior.
- Score and lives that persist between levels.
- A configurable level timer.
- Main menu, pause menu, instructions screen, highscore screen, game-over screen, and victory screen.
- Persistent top-10 highscores.
- Name entry with validation.
- Cheat mode for peer evaluation.
- A reproducible standalone build using PyInstaller.

The project targets Python 3.10 or newer.

## Links

- [Play Pac-Man 42 on itch.io](https://justmajd.itch.io/pacman-42)
- [Project management](project_management/README.md)

---

## Instructions

### Requirements

You need:

- Python 3.10+
- `make`
- `pip`
- A system capable of running Pygame/SDL applications

The project uses the provided A-Maze-ing package from:

```text
mazegenerator-2.1.0-py3-none-any.whl
```

The package is installed through `pip` and imported normally by the game.

### Clone the repository

```bash
git clone https://github.com/Justmajd/pacman-42.git
cd pacman-42
```

### Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### Install dependencies

```bash
make install
```

The `install` target installs:

- dependencies from `requirements.txt`
- the provided `mazegenerator` wheel

### Run the game

```bash
make run
```

By default, the Makefile runs the game with:

```text
config.example.json
```

The game can also be launched directly:

```bash
python3 pac-man.py config.example.json
```

The program expects exactly one configuration-file argument.

### Debug

```bash
make debug
```

### Clean generated files

```bash
make clean
```

### Build the standalone version

The project includes a reproducible build script at the repository root:

```bash
./build.sh
```

The script uses PyInstaller in `--onedir` mode and creates:

```text
dist/pacman/
```

The generated directory contains:

```text
dist/pacman/
├── pacman
├── config.json
├── assets/
├── _internal/
└── run-pacman.sh
```

Run the packaged game with:

```bash
dist/pacman/run-pacman.sh
```

The launcher changes into the package directory before starting the executable so that relative paths for the configuration file and assets continue to work.

> PyInstaller builds are platform-specific. Build the distributable on the operating system you intend to distribute it for.

---

## Controls

### Gameplay

| Key | Action |
| --- | --- |
| Arrow keys | Move Pac-Man |
| `W` / `A` / `S` / `D` | Move Pac-Man |
| `Esc` | Pause the game |

### Menus

| Key | Action |
| --- | --- |
| Up / Down | Navigate |
| Enter | Select |
| Esc | Back or resume where applicable |

### Name entry

| Key | Action |
| --- | --- |
| Letters / numbers / space | Enter player name |
| Backspace | Delete the previous character |
| Enter | Confirm |
| Esc | Cancel |

Player names are limited to 10 characters and may contain alphanumeric characters and spaces.

---

## Cheat Mode

Cheat mode is included to make peer evaluation easier.

Enter the following directional sequence during gameplay:

```text
UP UP DOWN DOWN LEFT RIGHT LEFT RIGHT
```

When cheat mode is enabled:

| Key | Action |
| --- | --- |
| `F1` | Toggle invincibility |
| `F2` | Toggle ghost freeze |
| `F3` | Add one life |
| `F4` | Toggle speed boost |
| `F5` | Skip the current level |

Entering the secret sequence again disables cheat mode and clears the toggleable cheat states.

---

## Configuration

The game is configured through a JSON file.

The default configuration is provided in:

```text
config.example.json
```

Current default values:

```json
{
  "highscore_filename": "highscore.json",
  "levels": [
    {"width": 15, "height": 15},
    {"width": 15, "height": 15},
    {"width": 17, "height": 17},
    {"width": 17, "height": 17},
    {"width": 19, "height": 19},
    {"width": 19, "height": 19},
    {"width": 21, "height": 21},
    {"width": 21, "height": 21},
    {"width": 23, "height": 23},
    {"width": 23, "height": 23}
  ],
  "lives": 3,
  "pacgum_count": 42,
  "points_per_pacgum": 10,
  "points_per_super_pacgum": 50,
  "points_per_ghost": 200,
  "seed": 42,
  "level_max_time": 90,
  "frightened_duration": 6.0
}
```

### Configuration fields

| Field | Default | Purpose |
| --- | --- | --- |
| `highscore_filename` | `highscore.json` | File used for persistent highscores |
| `levels` | 10 level objects | Width and height for every configured level |
| `lives` | `3` | Starting number of lives |
| `pacgum_count` | `42` | Required positive pacgum configuration value validated by the maze provider |
| `points_per_pacgum` | `10` | Score awarded for a normal pacgum |
| `points_per_super_pacgum` | `50` | Score awarded for a super pacgum |
| `points_per_ghost` | `200` | Score awarded for eating a frightened ghost |
| `seed` | `42` | Base seed value used by maze generation |
| `level_max_time` | `90` | Maximum level duration in seconds |
| `frightened_duration` | `6.0` | Duration of frightened mode in seconds |

Configuration loading and validation are implemented in `src/config.py`.

Level 1 always resolves to seed `42`. Levels after level 1 pass `None` as the maze seed so that the external generator provides randomized layouts.

The packaged build copies `config.example.json` to `dist/pacman/config.json`, and the packaged launcher runs the game with that file.

---

## Highscore

The highscore system is implemented in `src/highscore.py`.

The configured highscore file stores a JSON list of entries such as:

```json
[
  {
    "name": "PLAYER",
    "score": 1234
  }
]
```

### Validation rules

A highscore name:

- must be a string
- cannot be empty
- cannot contain only spaces
- may contain letters, numbers, and spaces
- may contain at most 10 characters

A score:

- must be an integer
- cannot be a boolean
- must be greater than or equal to zero

When highscores are loaded:

- a missing file produces an empty highscore list
- malformed JSON produces an empty highscore list
- file-access errors are handled without crashing
- non-list JSON roots are rejected
- malformed entries are skipped
- valid entries are sorted by score in descending order
- ties are ordered by name
- only the top 10 entries are kept

When the player confirms a valid name after Game Over or Victory, the current score is appended to the existing entries and saved.

The game also reloads the highscore file when the Highscores menu is opened so that the displayed table reflects the current stored data.

### Why it was implemented this way

JSON was chosen because the amount of persistent data is small and the format is easy to inspect, validate, and debug.

The save process writes normalized data to a temporary file first and then replaces the destination with `os.replace()`. This reduces the chance of leaving a partially written highscore file if something goes wrong during writing.

Keeping highscore validation in its own module also keeps persistence rules separate from the UI and game loop.

---

## Maze Generation

Maze generation is implemented through `src/maze_adapter.py`.

The assigned A-Maze-ing package is imported as:

```python
from mazegenerator import MazeGenerator
```

The package is installed from the provided wheel and is not reimplemented inside the project.

### How the package is used

For every level, `MazeGeneratorProvider`:

1. Reads the configured width and height.
2. Resolves the seed.
3. Instantiates `MazeGenerator` with:
   - the configured level size
   - `perfect=False`
   - the resolved seed
4. Reads the generated maze grid, maze entry, and maze exit.
5. Validates the wall grid and generated coordinates.
6. Finds the cells reachable from the maze entry.
7. Chooses the player spawn as the usable reachable cell nearest the maze center.
8. Chooses four cells nearest the four maze corners.
9. Uses those four cells as both ghost spawns and super-pacgum positions.
10. Places normal pacgums on the remaining reachable non-spawn cells.
11. Converts the result into the project's immutable `LevelData` representation.
12. Runs a final validation pass before returning the level.

### Seed behavior

- Level 1 always uses seed `42`.
- Later levels use `None` for the package seed, allowing randomized maze generation.

### Validation and failure handling

The adapter validates:

- dimensions
- wall-grid shape and values
- coordinates
- spawn uniqueness
- pickup placement
- reachability
- overlap rules
- isolated cells

If the external package raises a runtime generation error, the adapter converts it into a controlled `ValueError`. The CLI catches application-level `ValueError`s and exits cleanly instead of exposing an uncaught traceback to the player.

The adapter acts as a boundary between the external package's output and the internal data structures expected by the rest of the game.

---

## Implementation

The project is split into focused modules so that configuration, gameplay, rendering, persistence, and external-package integration remain separate.

### Entry point

`pac-man.py` is the command-line entry point.

It:

- validates that exactly one configuration argument was supplied
- loads the configuration
- starts the application
- handles configuration/file failures
- handles controlled game failures
- handles keyboard interruption cleanly

### Main application

`src/app.py` contains the main runtime loop and coordinates the major systems:

- Pygame events
- game-state transitions
- menus and screens
- player movement
- ghost updates
- scatter/chase phase switching
- collisions
- pickups
- level timers
- frightened mode
- level transitions
- score and lives
- highscore saving/loading
- cheat-mode behavior
- rendering

### Game session

`src/game_session.py` owns game-wide progression state such as:

- current level
- score
- lives
- level timer
- frightened timer
- state changes caused by world events

### Grid and world

`src/grid.py` provides maze movement and wall checks.

`src/world.py` manages world-level gameplay data such as:

- remaining pacgums
- remaining super pacgums
- pickup consumption
- player/ghost collision lookup
- clearing pickups for level completion

### Entities

`src/entities/player.py` contains player movement, requested-direction handling, respawning, and render-position interpolation.

`src/entities/ghost.py` contains ghost movement and targeting behavior, including chase/scatter targeting and frightened/eaten behavior.

### UI

`src/ui/menu.py` provides reusable menu-selection behavior.

`src/ui/screens.py` contains:

- `MainMenuScreen`
- `PauseScreen`
- `InstructionsScreen`
- `HighscoreScreen`
- `GameOverScreen`
- `VictoryScreen`
- `Transition`

These classes handle screen-specific keyboard input and rendering behavior.

### Rendering

`src/rendering/renderer.py` owns the Pygame window and renders game snapshots.

`src/rendering/shapes.py` contains visual shape data used by the renderer and screen transitions.

### Shared contracts

`src/contracts.py` defines shared types and data structures used between modules, including game states, directions, world events, level data, ghost state, and render snapshots.

### Input

`src/input.py` maps keyboard keys to the shared direction representation.

### Cheats

`src/cheat.py` contains `CheatController`, which detects the secret directional sequence and tracks cheat toggles and one-shot requests.

### Highscores

`src/highscore.py` owns highscore validation, normalization, loading, and saving.

### Maze adapter

`src/maze_adapter.py` contains `MazeGeneratorProvider` and validation helpers that convert A-Maze-ing output into internal `LevelData`.

---

## General Software Architecture

The project uses a modular architecture with `src/app.py` as the coordinator.

High-level relationship:

```text
pac-man.py
    |
    v
src/config.py
    |
    v
src/app.py
    |
    +----------------------+----------------------+----------------------+
    |                      |                      |                      |
    v                      v                      v                      v
game_session.py        ui/screens.py        rendering/             cheat.py
    |                      |                renderer.py
    |                      |                      |
    v                      v                      v
 world.py <---------- contracts.py ----------> entities/
    |                      ^                  player.py
    v                      |                  ghost.py
 grid.py                  |
                           |
                           +------ maze_adapter.py
                                      |
                                      v
                                mazegenerator

src/app.py
    |
    +------ highscore.py
```

### Responsibilities and relationships

- **`pac-man.py`** starts the program and provides top-level error handling.
- **`config.py`** converts JSON configuration into validated game settings.
- **`app.py`** coordinates the state machine and all runtime systems.
- **`game_session.py`** keeps progression and scoring rules separate from entity movement.
- **`maze_adapter.py`** isolates the external maze library from internal game structures.
- **`contracts.py`** defines shared types so modules communicate through explicit data contracts.
- **`grid.py`** answers maze-navigation questions for moving entities.
- **`world.py`** owns pickups and world-level interactions.
- **`entities/player.py`** and **`entities/ghost.py`** own entity-specific movement and behavior.
- **`ui/`** owns menus and non-gameplay screens.
- **`rendering/`** owns presentation and drawing.
- **`highscore.py`** owns persistent leaderboard data.
- **`cheat.py`** owns cheat-sequence and cheat-state logic.

---

## Project Management

The activity was developed collaboratively and divided into implementation rounds/milestones.

The work was split between team members so that different areas could progress in parallel, including:

- configuration and shared contracts
- maze integration
- gameplay systems
- player and ghost behavior
- UI and state transitions
- highscore persistence
- cheat mode
- packaging and deployment preparation

Git branches, commits, and merges were used to integrate changes incrementally.

Project-management notes are stored in the dedicated directory:

[project_management/](./project_management/)

The current tracked project-management document is:

[project_management/open_questions.md](./project_management/open_questions.md)

It records design decisions and questions related to graphics, maze integration, gameplay, and packaging.

---

---

## Packaging

PyInstaller `6.22.3` is pinned in `requirements.txt` so that the packaging tool version is reproducible.

The build script:

- removes/rebuilds PyInstaller output using `--clean`
- creates a directory-based executable with `--onedir`
- copies the `assets/` directory into the distributable
- copies the example configuration as `config.json`
- creates `run-pacman.sh`
- marks the launcher as executable

---

## Resources

### Documentation and references

The following references are useful for understanding the technologies and concepts used in the activity:

- Python documentation: https://docs.python.org/3/
- Python `dataclasses`: https://docs.python.org/3/library/dataclasses.html
- Python `json` module: https://docs.python.org/3/library/json.html
- Python `pathlib`: https://docs.python.org/3/library/pathlib.html
- Pygame Community Edition documentation: https://pyga.me/docs/
- PyInstaller documentation: https://pyinstaller.org/en/stable/
- PEP 8 — Style Guide for Python Code: https://peps.python.org/pep-0008/
- PEP 257 — Docstring Conventions: https://peps.python.org/pep-0257/
- 42 project subject and evaluation requirements supplied with the activity.
- The assigned A-Maze-ing / `mazegenerator` package supplied with the project.

### AI usage

AI tools were used as development assistance during the activity.

They were used for:

- interpreting and checking project requirements
- discussing architecture and module boundaries
- reviewing developer-written code and identifying bugs
- reviewing highscore and maze-generation edge cases
- drafting and reviewing project documentation, including this README
- fixing all mypy and flake8 errors after finishing development
AI assistance was used as a support and review tool. The authors remained responsible for understanding the implementation, integrating changes, and making the final project decisions.

---

## Repository Structure

```text
pacman-42/
├── assets/
│   └── fonts/
├── project_management/
│   └── open_questions.md
├── src/
│   ├── entities/
│   │   ├── ghost.py
│   │   └── player.py
│   ├── rendering/
│   │   ├── renderer.py
│   │   └── shapes.py
│   ├── ui/
│   │   ├── menu.py
│   │   └── screens.py
│   ├── app.py
│   ├── cheat.py
│   ├── config.py
│   ├── contracts.py
│   ├── game_session.py
│   ├── grid.py
│   ├── highscore.py
│   ├── input.py
│   ├── maze_adapter.py
│   └── world.py
├── build.sh
├── config.example.json
├── config.json
├── highscore.json
├── Makefile
├── mazegenerator-2.1.0-py3-none-any.whl
├── pac-man.py
├── requirements.txt
└── README.md
```
