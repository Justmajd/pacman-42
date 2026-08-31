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


def test_world_stores_mutable_pickups() -> None:
    level = make_level(
        pacgums=frozenset({(1, 1), (2, 2)}),
        super_pacgums=frozenset({(5, 5)}),
    )

    world = World(level)

    assert world.pacgums == {(1, 1), (2, 2)}
    assert world.super_pacgums == {(5, 5)}
    assert isinstance(world.pacgums, set)
    assert isinstance(world.super_pacgums, set)


def test_consume_normal_pacgum() -> None:
    level = make_level(
        pacgums=frozenset({(3, 3), (4, 4)}),
    )
    world = World(level)

    events = world.consume_pickup()

    assert events == (WorldEvent.PACGUM_EATEN,)
    assert (3, 3) not in world.pacgums
    assert (4, 4) in world.pacgums


def test_consume_super_pacgum() -> None:
    level = make_level(
        pacgums=frozenset({(4, 4)}),
        super_pacgums=frozenset({(3, 3)}),
    )
    world = World(level)

    events = world.consume_pickup()

    assert events == (WorldEvent.SUPER_PACGUM_EATEN,)
    assert (3, 3) not in world.super_pacgums


def test_final_normal_pacgum_emits_level_cleared() -> None:
    level = make_level(
        pacgums=frozenset({(3, 3)}),
    )
    world = World(level)

    events = world.consume_pickup()

    assert events == (
        WorldEvent.PACGUM_EATEN,
        WorldEvent.LEVEL_CLEARED,
    )
    assert world.pacgums == set()
    assert world.super_pacgums == set()


def test_final_super_pacgum_emits_level_cleared() -> None:
    level = make_level(
        super_pacgums=frozenset({(3, 3)}),
    )
    world = World(level)

    events = world.consume_pickup()

    assert events == (
        WorldEvent.SUPER_PACGUM_EATEN,
        WorldEvent.LEVEL_CLEARED,
    )
    assert world.pacgums == set()
    assert world.super_pacgums == set()


def test_no_pickup_returns_empty_tuple() -> None:
    level = make_level(
        pacgums=frozenset({(1, 1)}),
        super_pacgums=frozenset({(5, 5)}),
    )
    world = World(level)

    events = world.consume_pickup()

    assert events == ()
    assert world.pacgums == {(1, 1)}
    assert world.super_pacgums == {(5, 5)}


def test_pickup_is_only_consumed_once() -> None:
    level = make_level(
        pacgums=frozenset({(3, 3), (4, 4)}),
    )
    world = World(level)

    first_events = world.consume_pickup()
    second_events = world.consume_pickup()

    assert first_events == (WorldEvent.PACGUM_EATEN,)
    assert second_events == ()


def test_player_ghost_collision_emits_player_hit() -> None:
    level = make_level()
    world = World(level)

    world.ghosts[0] = world.player_position

    event = world.player_ghost_collision()

    assert event == WorldEvent.PLAYER_HIT


def test_no_player_ghost_collision_returns_none() -> None:
    level = make_level()
    world = World(level)

    event = world.player_ghost_collision()

    assert event is None