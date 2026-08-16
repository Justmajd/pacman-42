import json
from pathlib import Path


FIXTURE_PATH = Path("tests/fixtures/stub_level.json")


def load_fixture() -> dict:
    with FIXTURE_PATH.open("r", encoding="utf-8") as fixture_file:
        return json.load(fixture_file)


def test_stub_level_dimensions_match_walls() -> None:
    data = load_fixture()

    assert len(data["walls"]) == data["height"]
    assert all(len(row) == data["width"] for row in data["walls"])


def test_stub_level_has_four_ghost_spawns() -> None:
    data = load_fixture()

    assert len(data["ghost_spawns"]) == 4


def test_stub_level_positions_are_in_bounds() -> None:
    data = load_fixture()

    width = data["width"]
    height = data["height"]

    positions = [
        data["player_spawn"],
        *data["ghost_spawns"],
        *data["pacgums"],
        *data["super_pacgums"],
    ]

    for x, y in positions:
        assert 0 <= x < width
        assert 0 <= y < height


def test_player_spawn_does_not_overlap_ghost_spawn() -> None:
    data = load_fixture()

    assert data["player_spawn"] not in data["ghost_spawns"]


def test_pacgums_and_super_pacgums_do_not_overlap() -> None:
    data = load_fixture()

    pacgums = {tuple(position) for position in data["pacgums"]}
    super_pacgums = {
        tuple(position) for position in data["super_pacgums"]
    }

    assert pacgums.isdisjoint(super_pacgums)