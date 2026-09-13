from random import Random

import pygame

from src.config import GameConfig
from src.contracts import (
    Direction,
    GameSnapshot,
    GameState,
    GhostState,
    LevelData,
    MazeProvider,
    Position,
    WorldEvent,
)
from src.entities.ghost import Ghost
from src.entities.player import Player
from src.game_session import GameSession
from src.grid import Grid
from src.input import key_to_direction
from src.maze_adapter import MazeGeneratorProvider
from src.rendering.renderer import Renderer
from src.ui.menu import Menu
from src.ui.screens import (
    GameOverScreen,
    MainMenuScreen,
    PauseScreen,
    Transition,
    VictoryScreen,
)
from src.world import World

SCATTER_DURATION = 7.0
CHASE_DURATION = 20.0
LEVEL_START_COUNTDOWN_DURATION = 3.0
RESPAWN_FREEZE_DURATION = 3.0
LEVEL_CLEAR_HOLD_DURATION = 2.0
GAME_OVER_FREEZE_DURATION = 2.0


def _scatter_corners(width: int, height: int) -> dict[int, Position]:
    return {
        0: (width - 1, 0),
        1: (0, 0),
        2: (width - 1, height - 1),
        3: (0, height - 1),
    }


def _create_level_runtime(
    level_data: LevelData,
    lives: int,
) -> tuple[Grid, World, Player, list[Ghost]]:
    grid = Grid(level=level_data)
    world = World(level=level_data)
    player = Player(
        spawn=level_data.player_spawn,
        position=level_data.player_spawn,
        direction=Direction.NONE,
        requested_direction=Direction.NONE,
        lives=lives,
    )
    scatter_corners = _scatter_corners(level_data.width, level_data.height)
    ghosts: list[Ghost] = []
    for ghost_id, spawn in enumerate(level_data.ghost_spawns):
        ghost = Ghost(
            position=spawn,
            spawn=spawn,
            direction=Direction.NONE,
            active=True,
            respawn_delay=0.0,
            ghost_id=ghost_id,
            scatter_target=scatter_corners[ghost_id],
        )
        ghosts.append(ghost)
    return grid, world, player, ghosts


def run_app(config: GameConfig) -> int:
    session: GameSession = GameSession(config=config)
    provider: MazeProvider = MazeGeneratorProvider(config)
    level_data = provider.build_level(1, config.seed)
    grid, world, player, ghosts = _create_level_runtime(
        level_data,
        lives=session.lives,
    )
    renderer: Renderer = Renderer(
        window_width=1280,
        window_height=720,
        window_title="Pacman",
    )
    rng = Random(config.seed)

    level_start_countdown = LEVEL_START_COUNTDOWN_DURATION
    respawn_freeze = 0.0
    game_over_freeze = 0.0
    level_clear_hold = 0.0
    player_is_dying = False
    is_scattering = True
    phase_time_remaining = SCATTER_DURATION

    state = GameState.MENU
    pending_state: GameState | None = None
    transition: Transition | None = None
    level_swap_pending = False
    new_game_pending = False

    main_menu = MainMenuScreen(
        menu=Menu(options=["Start", "Highscores", "Instructions", "Exit"])
    )
    pause_screen = PauseScreen(menu=Menu(options=["Resume", "Main Menu"]))
    game_over_screen = GameOverScreen(menu=Menu(options=["Retry", "Main Menu"]))
    victory_screen = VictoryScreen(menu=Menu(options=["Retry", "Main Menu"]))

    renderer.load_level(level_data=level_data)
    game_snapshot: GameSnapshot | None = None

    def start_new_game() -> None:
        nonlocal session, level_data, grid, world, player, ghosts
        nonlocal level_start_countdown, respawn_freeze, game_over_freeze
        nonlocal level_clear_hold, player_is_dying
        nonlocal is_scattering, phase_time_remaining
        session = GameSession(config=config)
        level_data = provider.build_level(1, config.seed)
        grid, world, player, ghosts = _create_level_runtime(
            level_data,
            lives=session.lives,
        )
        renderer.load_level(level_data=level_data)
        level_start_countdown = LEVEL_START_COUNTDOWN_DURATION
        respawn_freeze = 0.0
        game_over_freeze = 0.0
        level_clear_hold = 0.0
        player_is_dying = False
        is_scattering = True
        phase_time_remaining = SCATTER_DURATION

    def render_current(target_state: GameState) -> None:
        if target_state == GameState.MENU:
            main_menu.render(renderer.screen)
        elif target_state == GameState.PAUSED:
            pause_screen.render(renderer.screen)
        elif target_state == GameState.PLAYING:
            renderer.render(game_snapshot)
        elif target_state == GameState.GAME_OVER:
            game_over_screen.render(renderer.screen, session.score)
        elif target_state == GameState.VICTORY:
            victory_screen.render(renderer.screen, session.score)

    while renderer.is_running:
        dt = renderer.tick()
        events = renderer.process_events()

        if transition is not None:
            was_covering = transition.covering
            transition.update(dt)
            if level_swap_pending and was_covering and not transition.covering:
                level_swap_pending = False
                level_data = provider.build_level(session.level, config.seed)
                grid, world, player, ghosts = _create_level_runtime(
                    level_data,
                    lives=session.lives,
                )
                renderer.load_level(level_data=level_data)
                level_start_countdown = LEVEL_START_COUNTDOWN_DURATION
                is_scattering = True
                phase_time_remaining = SCATTER_DURATION
            if new_game_pending and was_covering and not transition.covering:
                new_game_pending = False
                start_new_game()
            if transition.finished:
                if pending_state is not None:
                    state = pending_state
                    pending_state = None
                transition = None
        else:
            if state == GameState.MENU:
                for event in events:
                    next_state = main_menu.handle_event(event)
                    if next_state == GameState.EXIT:
                        renderer.is_running = False
                    elif next_state == GameState.PLAYING:
                        new_game_pending = True
                        pending_state = GameState.PLAYING
                        transition = Transition()
            elif state == GameState.PAUSED:
                for event in events:
                    next_state = pause_screen.handle_event(event)
                    if next_state == GameState.PLAYING:
                        state = GameState.PLAYING
                    if next_state == GameState.MENU:
                        pending_state = GameState.MENU
                        transition = Transition()
            elif state == GameState.GAME_OVER:
                for event in events:
                    next_state = game_over_screen.handle_event(event)
                    if next_state == GameState.PLAYING:
                        new_game_pending = True
                        pending_state = GameState.PLAYING
                        transition = Transition()
                    if next_state == GameState.MENU:
                        pending_state = GameState.MENU
                        transition = Transition()
            elif state == GameState.VICTORY:
                for event in events:
                    next_state = victory_screen.handle_event(event)
                    if next_state == GameState.PLAYING:
                        new_game_pending = True
                        pending_state = GameState.PLAYING
                        transition = Transition()
                    if next_state == GameState.MENU:
                        pending_state = GameState.MENU
                        transition = Transition()
            elif state == GameState.PLAYING:
                if session.state == GameState.PLAYING:
                    if level_clear_hold > 0:
                        level_clear_hold -= dt
                        if level_clear_hold <= 0:
                            level_clear_hold = 0.0
                            level_swap_pending = True
                            transition = Transition()
                    elif level_start_countdown > 0:
                        level_start_countdown -= dt
                        if level_start_countdown < 0:
                            level_start_countdown = 0.0
                    elif respawn_freeze > 0:
                        respawn_freeze -= dt
                        if respawn_freeze < 0:
                            respawn_freeze = 0.0
                        if respawn_freeze <= 0:
                            player.respawn()
                            for ghost in ghosts:
                                ghost.respawn()
                            player_is_dying = False
                    else:
                        for event in events:
                            if event.type == pygame.KEYDOWN:
                                if event.key == pygame.K_p:
                                    pause_screen.capture_background(
                                        renderer.screen
                                    )
                                    state = GameState.PAUSED
                                else:
                                    direction = key_to_direction(event.key)
                                    if direction is not None:
                                        player.request_direction(
                                            direction=direction
                                        )
                        player.update(grid=grid, dt=dt)
                        phase_time_remaining -= dt
                        if phase_time_remaining <= 0:
                            is_scattering = not is_scattering
                            phase_time_remaining = (
                                SCATTER_DURATION
                                if is_scattering
                                else CHASE_DURATION
                            )
                        blinky_pos = ghosts[0].position
                        for ghost in ghosts:
                            ghost_target = ghost.compute_target(
                                player.position,
                                player.facing,
                                blinky_pos,
                                is_scattering,
                            )
                            ghost.update(
                                dt=dt,
                                grid=grid,
                                target=ghost_target,
                                rng=rng,
                                frightened=(
                                    session.frightened_time_remaining > 0
                                    and not ghost.is_eaten
                                    and not ghost.frightened_immune
                                ),
                            )
                        world.player_position = player.position
                        world.ghosts = [ghost.position for ghost in ghosts]
                        consumable = world.consume_pickup()
                        for world_event in consumable:
                            session.handle_event(event=world_event)
                            if world_event == WorldEvent.LEVEL_CLEARED:
                                level_clear_hold = LEVEL_CLEAR_HOLD_DURATION
                            if world_event == WorldEvent.SUPER_PACGUM_EATEN:
                                for ghost in ghosts:
                                    ghost.frightened_immune = False
                        if level_clear_hold <= 0:
                            collision_index = world.player_ghost_collision(
                                player.render_position(),
                                [ghost.render_position() for ghost in ghosts],
                            )
                            if collision_index is not None:
                                collided_ghost = ghosts[collision_index]
                                if collided_ghost.is_eaten:
                                    pass
                                elif (
                                    session.frightened_time_remaining > 0
                                    and not collided_ghost.frightened_immune
                                ):
                                    session.handle_event(
                                        WorldEvent.GHOST_EATEN
                                    )
                                    collided_ghost.is_eaten = True
                                    collided_ghost.frightened_immune = True
                                else:
                                    session.handle_event(WorldEvent.PLAYER_HIT)
                                    player_is_dying = True
                                    if session.state == GameState.GAME_OVER:
                                        game_over_freeze = (
                                            GAME_OVER_FREEZE_DURATION
                                        )
                                    else:
                                        respawn_freeze = RESPAWN_FREEZE_DURATION
                        session.update(dt=dt)
                elif session.state == GameState.GAME_OVER:
                    game_over_freeze -= dt
                    if game_over_freeze <= 0:
                        state = GameState.GAME_OVER
                elif session.state == GameState.VICTORY:
                    level_clear_hold -= dt
                    if level_clear_hold <= 0:
                        state = GameState.VICTORY

        ghosts_state: list[GhostState] = []
        for ghost in ghosts:
            ghost_state = GhostState(
                id=ghost.ghost_id,
                position=ghost.render_position(),
                direction=ghost.direction,
                is_frightened=(
                    session.frightened_time_remaining > 0
                    and not ghost.is_eaten
                    and not ghost.frightened_immune
                ),
                frightened_time_remaining=(
                    session.frightened_time_remaining
                ),
                is_active=ghost.active,
                is_eaten=ghost.is_eaten,
            )
            ghosts_state.append(ghost_state)
        ghost_state_tuple: tuple[
            GhostState,
            GhostState,
            GhostState,
            GhostState,
        ] = (
            ghosts_state[0],
            ghosts_state[1],
            ghosts_state[2],
            ghosts_state[3],
        )
        level_cleared_display = (
            level_clear_hold > 0
            or (transition is not None and pending_state is None)
        )
        game_snapshot = GameSnapshot(
            level_start_countdown=level_start_countdown,
            level_cleared=level_cleared_display,
            player_pos=player.render_position(),
            player_direction=player.facing,
            player_is_dying=player_is_dying,
            player_is_moving=player.is_moving(),
            pacgums=frozenset(world.pacgums),
            super_pacgums=frozenset(world.super_pacgums),
            ghosts=ghost_state_tuple,
            score=session.score,
            level=session.level,
            lives=session.lives,
            time=session.level_time_remaining,
        )

        if transition is not None:
            if transition.covering or pending_state is None:
                render_current(state)
            else:
                render_current(pending_state)
            transition.render(renderer.screen)
        else:
            render_current(state)
        pygame.display.flip()

    renderer.cleanup()
    return 0
