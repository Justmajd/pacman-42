from src.config import GameConfig
from src.maze_adapter import StubMazeProvider
from src.grid import Grid
from src.world import World
from src.game_session import GameSession
from src.entities.player import Player
from src.entities.ghost import Ghost
from src.contracts import Direction
from src.rendering.renderer import Renderer
from src.input import key_to_direction , _KEY_DIRECTIONS
import pygame
def run_app(config: GameConfig) -> int:
    stubmaze: StubMazeProvider = StubMazeProvider()
    level_data = stubmaze.build_level(1,config.seed)
    grid: Grid = Grid(level=level_data)
    world: World = World(level=level_data)
    session: GameSession = GameSession(config=config)
    player: Player = Player(spawn=level_data.player_spawn,position=level_data.player_spawn , direction = Direction.NONE , requested_direction= Direction.NONE , lives= session.lives)
    ghosts: list[Ghost] = []
    renderer: Renderer = Renderer(window_width=1280,window_height=720, window_title= "Pacman")
    for spawn in level_data.ghost_spawns:
        ghost: Ghost = Ghost(position=spawn ,spawn=spawn , direction=Direction.NONE,active=True,respawn_delay=0.0)
        ghosts.append(ghost)
    renderer.load_level(level_data=level_data)

    while renderer.is_running:
        dt = renderer.tick()
        events = renderer.process_events()
        for event in events:
            if event == isinstance(pygame.KEYDOWN):
                pass
    renderer.cleanup()
    return 0