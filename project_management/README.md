### Round 0 — joint cont+ract session, 45–60 minutes

- [x]  Agree on all interfaces above.
- [x]  Create repository structure and protected main branch.
- [x]  Add the stub level fixture.
- [x]  Add minimal `Makefile` targets: `install`, `run`, `test`, `lint`, `clean`.
- [x]  Add CI or a local pre-merge command that runs tests, flake8, and mypy.
- [x]  Decide branch naming and pull-request rules.
- [x]  Record unresolved subject questions in `project_management/open_questions.md`.

**Merge gate:** both teammates can run the empty window/application skeleton and the test suite.

### Round 1 — movement foundation and application skeleton

#### Majd — Config and application bootstrap

- [x]  Implement the config dataclass and documented defaults.
- [x]  Parse the exact format required by the real subject.
- [x]  Validate types, ranges, and mandatory fields.
- [x]  Implement clean CLI argument handling in `pac-man.py`.
- [x]  Build `app.py` with the event/update/render loop using the stub provider.
- [x]  Add config and CLI tests.

#### Omar — Player and input intent

- [x]  Implement player position, direction, requested direction, spawn, and respawn.
- [x]  Support arrows and WASD if permitted.
- [x]  Validate movement through the grid interface.
- [x]  Do not modify score, lives, pickups, or ghosts inside `Player`.
- [x]  Add movement, blocked-turn, queued-turn, and respawn tests.

**Merge gate:** player moves around the stub maze in the real application loop.

### Round 2 — world model and ghost movement

#### Majd — Grid, level, and world rules

- [x]  Implement walkability and neighbour queries.
- [x]  Store remaining pacgums and super-pacgums.
- [x]  Resolve pickup consumption.
- [x]  Resolve player/ghost collisions after movement updates.
- [x]  Emit gameplay events without directly changing UI state.
- [x]  Validate all spawns and pickups when loading a level.

#### Omar — Ghost entity and deterministic AI

- [x]  Implement ghost position, direction, spawn, active/dead state, and respawn delay.
- [x]  Chase by choosing a valid neighbour that minimizes Manhattan distance.
- [x]  Flee by maximizing Manhattan distance.
- [x]  Avoid reversal unless no other move exists.
- [x]  Inject randomness for deterministic tie-break tests.
- [x]  Add dead-end, tie-break, chase, flee, and respawn tests.

**Merge gate:** one player and four ghosts move together; collisions are detected by `World`.

### Round 3 — progression and rendering

#### Majd — Game session and progression

- [x]  Implement score, lives, level, timers, frightened timer, and state transitions.
- [x]  Handle pacgum, super-pacgum, ghost-eaten, player-hit, timeout, and level-cleared events.
- [x]  Decide whether timeout loses a life only after confirming the real subject.
- [x]  Preserve score/lives across level transitions where required.
- [x]  Define victory and game-over conditions from the actual subject.
- [x]  Add transition and timer tests using a fake clock or explicit `dt` values.

#### Omar — Renderer and HUD

- [x]  Create and own the pygame window lifecycle.
- [x]  Draw walls, corridors, pickups, Pac-Man, and distinct ghosts.
- [x]  Draw score, lives, level, and time only from a read-only session snapshot.
- [x]  Make tile size and viewport scaling config-driven.
- [x]  Avoid importing gameplay internals; consume contracts/snapshots only.
- [x]  Add renderer smoke tests that work with a dummy display when possible.

**Merge gate:** complete playable vertical slice with score, lives, ghosts, HUD, and level completion.

### Round 4 — external maze integration and UI flow

#### Majd — A-Maze-ing adapter

- [x]  Confirm the assigned package name, installation method, import path, and public API.
- [x]  Pin or constrain the dependency only as allowed by the subject.
- [x]  Translate its output into `LevelData`.
- [x]  Use seed `42` for level 1 only if the Pac-Man subject explicitly requires it.
- [x]  Generate or derive reachable player/ghost/pickup positions.
- [x]  Validate adapter output before starting gameplay.
- [x]  Add adapter contract tests with a fake package implementation.

#### Omar — Menus and screens

- [x]  Main menu: Start, Highscores, Instructions, Exit.
- [x]  Pause menu: Resume, Main Menu.
- [x]  Game-over and victory screens.
- [x]  Name-entry screen with editing, confirmation, and cancellation behaviour.
- [x]  Keep screen navigation separate from game simulation logic.
- [x]  Add keyboard-navigation smoke tests where practical.

**Merge gate:** a user can navigate from menu to a generated level, pause, return, lose, win, and enter a name.

### Round 5 — persistence and cheats

#### Majd — Highscores

- [x]  Load and save with context managers and atomic replacement (`temp file → replace`).
- [x]  Validate names and scores according to the real subject.
- [x]  Keep only the top required number of entries.
- [x]  Define deterministic sorting for equal scores.
- [x]  Recover from missing, empty, partially written, and corrupt files.
- [x]  Add persistence and corruption tests.

#### Omar — Cheat controller

- [x]  Confirm every required cheat and key from the actual subject.
- [x]  Put key mapping and enabled state in `CheatController`.
- [x]  Call public session/world methods only.
- [x]  Implement invincibility, level skip, ghost freeze, extra lives, and speed boost only when required.
- [x]  Display a visible cheat-mode indicator.
- [x]  Add tests proving cheats cannot corrupt score, timers, or state transitions.

**Merge gate:** highscores survive restart and all mandatory cheats work through public interfaces.

### Round 6 — quality, accessibility, and packaging

#### Majd — Packaging and deployment

- [x]  Verify whether standalone packaging and itch.io are mandatory or optional.
- [x]  Add a reproducible build script.
- [x]  Ensure external maze dependency is installed rather than copied into the repository.
- [x]  Test the build in a clean environment.
- [x]  Include licences/credits and minimal launch instructions.
- [x]  Upload privately/unlisted only if required.

#### Omar — Test expansion and Makefile finalization

- [x]  Finalize `install`, `run`, `debug`, `clean`, `test`, `lint`, and `lint-strict` targets as required.
- [x]  Add an end-to-end smoke test with the stub maze provider.
- [x]  Add malformed config, tiny map, unreachable spawn, timeout, simultaneous collision, and final-pacgum edge cases.
- [x]  Run flake8 and the exact mypy flags from the subject.
- [x]  Confirm tests do not depend on frame rate or wall-clock timing.

**Merge gate:** clean clone → install → lint → test → run → package succeeds.