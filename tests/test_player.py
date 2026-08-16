from src.contracts import Position, Direction
from src.entities.player import Player


class FakeGrid:
    def __init__(self, walkable: set[Position]) -> None:
        self.walkable = walkable

    def is_walkable(self, position: Position) -> bool:
        return position in self.walkable


def make_player(
    position: Position = (5, 5),
    direction: Direction = Direction.RIGHT,
    requested_direction: Direction = Direction.RIGHT,
    spawn: Position = (5, 5),
    lives: int = 3,
) -> Player:
    return Player(
        position=position,
        direction=direction,
        requested_direction=requested_direction,
        spawn=spawn,
        lives=lives,
    )


def test_turn_succeeds_when_requested_direction_is_walkable() -> None:
    player = make_player(
        position=(5, 5),
        direction=Direction.RIGHT,
        requested_direction=Direction.UP,
    )
    grid = FakeGrid(walkable={(4, 5)})

    player.update(grid)

    assert player.position == (4, 5)
    assert player.direction == Direction.UP


def test_fallback_to_current_direction_when_requested_is_blocked() -> None:
    player = make_player(
        position=(5, 5),
        direction=Direction.RIGHT,
        requested_direction=Direction.UP,
    )
    grid = FakeGrid(walkable={(5, 6)})

    player.update(grid)

    assert player.position == (5, 6)
    assert player.direction == Direction.RIGHT

def test_stays_put_when_boxed_in() -> None:
    player = make_player(
        position=(5, 5),
        direction=Direction.RIGHT,
        requested_direction=Direction.UP,
    )
    grid = FakeGrid(walkable=set())

    player.update(grid)

    assert player.position == (5, 5)
    assert player.direction == Direction.RIGHT


def test_respawn_resets_position_and_direction_but_not_lives() -> None:
    player = make_player(
        position=(1, 1),
        direction=Direction.LEFT,
        requested_direction=Direction.DOWN,
        spawn=(5, 5),
        lives=2,
    )

    player.respawn()

    assert player.position == (5, 5)
    assert player.direction == Direction.NONE
    assert player.requested_direction == Direction.NONE
    assert player.lives == 2

def test_queued_turn_applies_once_target_becomes_walkable() -> None:
    player = make_player(
        position=(5, 5),
        direction=Direction.RIGHT,
        requested_direction=Direction.UP
    )
    grid = FakeGrid(walkable={(5, 6), (4, 6)})

    player.update(grid)
    assert player.position == (5, 6)
    assert player.direction == Direction.RIGHT
    assert player.requested_direction == Direction.UP

    player.update(grid)
    assert player.position == (4, 6)
    assert player.direction == Direction.UP