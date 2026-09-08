from src.contracts import LevelData, WorldEvent
from src.world import World


def make_level(
    pacgums: frozenset[tuple[int, int]] = frozenset(),
    super_pacgums: frozenset[tuple[int, int]] = frozenset(),
) -> LevelData:
    return LevelData(
        width=7,
        height=7,
        walls=tuple(tuple(0 for _ in range(7)) for _ in range(7)),
        player_spawn=(3, 3),
        ghost_spawns=((0, 0), (6, 0), (0, 6), (6, 6)),
        pacgums=pacgums,
        super_pacgums=super_pacgums,
    )


def test_world_copies_pickup_sets() -> None:
    level = make_level(
        pacgums=frozenset({(1, 1)}),
        super_pacgums=frozenset({(2, 2)}),
    )

    world = World(level)

    assert world.pacgums == {(1, 1)}
    assert world.super_pacgums == {(2, 2)}
    assert isinstance(world.pacgums, set)
    assert isinstance(world.super_pacgums, set)


def test_consume_normal_pacgum() -> None:
    level = make_level(
        pacgums=frozenset({(1, 1), (2, 2)}),
    )
    world = World(level)
    world.player_position = (1, 1)

    events = world.consume_pickup()

    assert events == (WorldEvent.PACGUM_EATEN,)
    assert (1, 1) not in world.pacgums
    assert (2, 2) in world.pacgums


def test_last_normal_pacgum_clears_level() -> None:
    level = make_level(
        pacgums=frozenset({(1, 1)}),
        super_pacgums=frozenset({(2, 2), (3, 3)}),
    )
    world = World(level)
    world.player_position = (1, 1)

    events = world.consume_pickup()

    assert events == (
        WorldEvent.PACGUM_EATEN,
        WorldEvent.LEVEL_CLEARED,
    )
    assert world.pacgums == set()
    assert world.super_pacgums == {(2, 2), (3, 3)}


def test_consume_super_pacgum() -> None:
    level = make_level(
        pacgums=frozenset({(1, 1)}),
        super_pacgums=frozenset({(2, 2)}),
    )
    world = World(level)
    world.player_position = (2, 2)

    events = world.consume_pickup()

    assert events == (WorldEvent.SUPER_PACGUM_EATEN,)
    assert (2, 2) not in world.super_pacgums
    assert (1, 1) in world.pacgums


def test_super_pacgum_does_not_clear_level_when_no_normal_pacgums() -> None:
    level = make_level(
        pacgums=frozenset(),
        super_pacgums=frozenset({(2, 2)}),
    )
    world = World(level)
    world.player_position = (2, 2)

    events = world.consume_pickup()

    assert events == (WorldEvent.SUPER_PACGUM_EATEN,)
    assert world.super_pacgums == set()


def test_no_pickup_returns_empty_tuple() -> None:
    level = make_level(
        pacgums=frozenset({(1, 1)}),
        super_pacgums=frozenset({(2, 2)}),
    )
    world = World(level)
    world.player_position = (3, 3)

    events = world.consume_pickup()

    assert events == ()


def test_pickup_can_only_be_consumed_once() -> None:
    level = make_level(
        pacgums=frozenset({(1, 1), (2, 2)}),
    )
    world = World(level)
    world.player_position = (1, 1)

    first_events = world.consume_pickup()
    second_events = world.consume_pickup()

    assert first_events == (WorldEvent.PACGUM_EATEN,)
    assert second_events == ()


def test_player_ghost_collision_returns_correct_index() -> None:
    level = make_level()
    world = World(level)
    world.player_position = (6, 0)

    collision_index = world.player_ghost_collision()

    assert collision_index == 1


def test_player_ghost_collision_returns_none() -> None:
    level = make_level()
    world = World(level)
    world.player_position = (3, 3)

    collision_index = world.player_ghost_collision()

    assert collision_index is None