from src.contracts import Direction
from src.entities.player import Player


class FakeGrid:
    def __init__(self, walkable: set[tuple[int, int]]) -> None:
        self.walkable = walkable

    def is_walkable(
        self,
        start: tuple[int, int],
        end: tuple[int, int],
    ) -> bool:
        return end in self.walkable


def make_player(
    position: tuple[int, int] = (5, 5),
    direction: Direction = Direction.NONE,
    requested_direction: Direction = Direction.NONE,
    lives: int = 3,
) -> Player:
    return Player(
        position=position,
        direction=direction,
        requested_direction=requested_direction,
        spawn=position,
        lives=lives,
    )


def test_requested_direction_is_selected_when_stopped() -> None:
    player = make_player(
        position=(5, 5),
        direction=Direction.NONE,
        requested_direction=Direction.UP,
    )
    grid = FakeGrid(walkable={(5, 4)})

    player.update(grid, 0.1)

    assert player.position == (5, 5)
    assert player.direction == Direction.UP


def test_player_moves_one_tile_after_enough_time() -> None:
    player = make_player(
        position=(5, 5),
        direction=Direction.RIGHT,
        requested_direction=Direction.RIGHT,
    )
    grid = FakeGrid(
        walkable={
            (6, 5),
            (7, 5),
        }
    )

    player.update(grid, 1.0 / 6.0)

    assert player.position == (6, 5)
    assert player.direction == Direction.RIGHT


def test_stays_put_when_boxed_in() -> None:
    player = make_player(
        position=(5, 5),
        direction=Direction.NONE,
        requested_direction=Direction.UP,
    )
    grid = FakeGrid(walkable=set())

    player.update(grid, 0.1)

    assert player.position == (5, 5)
    assert player.direction == Direction.NONE


def test_respawn_resets_position_and_direction_but_not_lives() -> None:
    player = Player(
        position=(8, 8),
        direction=Direction.LEFT,
        requested_direction=Direction.UP,
        spawn=(5, 5),
        lives=2,
        progress=0.75,
    )

    player.respawn()

    assert player.position == (5, 5)
    assert player.direction == Direction.NONE
    assert player.requested_direction == Direction.NONE
    assert player.progress == 0.0
    assert player.lives == 2


def test_queued_turn_applies_at_next_tile() -> None:
    player = make_player(
        position=(5, 5),
        direction=Direction.RIGHT,
        requested_direction=Direction.UP,
    )
    grid = FakeGrid(
        walkable={
            (6, 5),
            (6, 4),
        }
    )

    player.update(grid, 1.0 / 6.0)

    assert player.position == (6, 5)
    assert player.direction == Direction.UP

    player.update(grid, 1.0 / 6.0)

    assert player.position == (6, 4)