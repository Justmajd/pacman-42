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
    WorldEvent,
)
from src.entities.ghost import Ghost
from src.entities.player import Player
from src.game_session import GameSession
from src.grid import Grid
from src.input import key_to_direction
from src.maze_adapter import MazeGeneratorProvider
from src.rendering.renderer import Renderer
from src.world import World


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
    ghosts: list[Ghost] = []
    for ghost_id, spawn in enumerate(level_data.ghost_spawns):
        ghost = Ghost(
            position=spawn,
            spawn=spawn,
            direction=Direction.NONE,
            active=True,
            respawn_delay=0.0,
            ghost_id=ghost_id,
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
    transition: bool = False
    level_start_countdown = 3.0
    renderer.load_level(level_data=level_data)
    while renderer.is_running:
        dt = renderer.tick()
        events = renderer.process_events()
        if session.state == GameState.PLAYING:
            if level_start_countdown > 0:
                level_start_countdown = level_start_countdown - dt
                if level_start_countdown < 0:
                    level_start_countdown = 0
            else:
                transition = False
                for event in events:
                    if event.type == pygame.KEYDOWN:
                        direction = key_to_direction(event.key)
                        if direction is not None:
                            player.request_direction(direction=direction)
                player.update(grid=grid, dt=dt)
                for ghost in ghosts:
                    ghost.update(
                        dt=dt,
                        grid=grid,
                        target=player.position,
                        rng=rng,
                        frightened=session.frightened_time_remaining > 0,
                    )
                world.player_position = player.position
                world.ghosts = [ghost.position for ghost in ghosts]
                consumable = world.consume_pickup()
                for world_event in consumable:
                    session.handle_event(event=world_event)
                    if world_event == WorldEvent.LEVEL_CLEARED:
                        if session.state == GameState.PLAYING:
                            level_data = provider.build_level(
                                session.level,
                                config.seed,
                            )
                            grid, world, player, ghosts = (
                                _create_level_runtime(
                                    level_data,
                                    lives=session.lives,
                                )
                            )
                            renderer.load_level(level_data=level_data)
                            transition = True
                            level_start_countdown = 3.0
                if (
                    not transition
                    and session.state == GameState.PLAYING
                ):
                    collision_index = world.player_ghost_collision()
                    if collision_index is not None:
                        if session.frightened_time_remaining > 0:
                            collided_ghost = ghosts[collision_index]
                            if not collided_ghost.is_eaten:
                                session.handle_event(WorldEvent.GHOST_EATEN)
                                collided_ghost.is_eaten = True

                        else:
                            session.handle_event(WorldEvent.PLAYER_HIT)
                            level_start_countdown = 3.0
                            if session.state != GameState.GAME_OVER:
                                player.respawn()
                                for ghost in ghosts:
                                    ghost.respawn()
                    session.update(dt=dt)
        ghosts_state: list[GhostState] = []
        for ghost in ghosts:
            ghost_state = GhostState(
                id=ghost.ghost_id,
                position=ghost.render_position(),
                direction=ghost.direction,
                is_frightened=session.frightened_time_remaining > 0,
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
        game_snapshot = GameSnapshot(
            level_start_countdown=level_start_countdown,
            player_pos=player.render_position(),
            player_direction=player.facing,
            player_is_dying=session.state == GameState.GAME_OVER,
            player_is_moving=player.is_moving(),
            pacgums=frozenset(world.pacgums),
            super_pacgums=frozenset(world.super_pacgums),
            ghosts=ghost_state_tuple,
            score=session.score,
            level=session.level,
            lives=session.lives,
            time=session.level_time_remaining,
        )
        renderer.render(game_snapshot)
    renderer.cleanup()
    return 0
