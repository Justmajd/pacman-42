import pytest
import random
from src.contracts import Direction
from src.entities.ghost import Ghost

class MockGrid:
    def __init__(self, walkable_cells: list[tuple[int, int]]):
        self.walkable_cells = walkable_cells

    def is_walkable(self, pos: tuple[int, int]) -> bool:
        return pos in self.walkable_cells

def test_ghost_respawn() -> None:
    spawn_pos = (1, 1)
    ghost = Ghost(position=(5, 5), direction=Direction.UP, spawn=spawn_pos, 
                  active=False, respawn_delay=2.0)
    fake_grid = MockGrid([(5, 5)])
    rng = random.Random(42)

    ghost.update(dt=1.0, grid=fake_grid, target=(10, 10), frightened=False, rng=rng)
    assert not ghost.active
    assert ghost.respawn_delay == 1.0

    ghost.update(dt=1.5, grid=fake_grid, target=(10, 10), frightened=False, rng=rng)
    assert ghost.active
    assert ghost.position == spawn_pos
    assert ghost.direction == Direction.NONE

def test_ghost_chase_no_tie() -> None:
    ghost = Ghost(position=(2, 2), direction=Direction.NONE, spawn=(1, 1), 
                  active=True, respawn_delay=0.0)
    fake_grid = MockGrid([(2, 3), (3, 2)])
    rng = random.Random(42)

    # Target is (2, 4). In (row, col), this is to the RIGHT.
    ghost.update(dt=0.1, grid=fake_grid, target=(2, 4), frightened=False, rng=rng)
    
    assert ghost.direction == Direction.RIGHT
    assert ghost.position == (2, 3)

def test_ghost_flee_no_tie() -> None:
    ghost = Ghost(position=(2, 2), direction=Direction.NONE, spawn=(1, 1), 
                  active=True, respawn_delay=0.0)
    fake_grid = MockGrid([(2, 3), (3, 2)])
    rng = random.Random(42)

    # Target is (2, 4) [RIGHT]. To flee, ghost should move DOWN to (3, 2).
    ghost.update(dt=0.1, grid=fake_grid, target=(2, 4), frightened=True, rng=rng)
    
    assert ghost.direction == Direction.DOWN
    assert ghost.position == (3, 2)

def test_ghost_deterministic_tie_breaker() -> None:
    ghost = Ghost(position=(2, 2), direction=Direction.NONE, spawn=(1, 1), 
                  active=True, respawn_delay=0.0)
    fake_grid = MockGrid([(2, 3), (3, 2)])
    rng_1 = random.Random(42) 
    
    ghost.update(dt=0.1, grid=fake_grid, target=(4, 4), frightened=False, rng=rng_1)
    
    # Seed 42 resolves this specific tie to DOWN
    assert ghost.direction == Direction.DOWN 

def test_ghost_dead_end_reversal() -> None:
    ghost = Ghost(position=(5, 5), direction=Direction.RIGHT, spawn=(1, 1), 
                  active=True, respawn_delay=0.0)
    # The only walkable cell is (4, 5), which is UP in a (row, col) system
    fake_grid = MockGrid([(4, 5)])
    rng = random.Random(42)

    ghost.update(dt=0.1, grid=fake_grid, target=(10, 10), frightened=False, rng=rng)
    
    assert ghost.direction == Direction.UP
    assert ghost.position == (4, 5)