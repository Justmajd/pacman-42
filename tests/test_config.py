import json

from src.config import GameConfig, load_config


def write_config(tmp_path, data: object) -> str:
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps(data), encoding="utf-8")
    return str(config_path)


def test_load_valid_config(tmp_path) -> None:
    data = {
        "highscore_filename": "scores.json",
        "levels": [
            {"width": 15, "height": 15}
            for _ in range(10)
        ],
        "lives": 5,
        "pacgum_count": 50,
        "points_per_pacgum": 20,
        "points_per_super_pacgum": 100,
        "points_per_ghost": 500,
        "seed": 123,
        "level_max_time": 120,
    }

    config = load_config(write_config(tmp_path, data))

    assert config.highscore_filename == "scores.json"
    assert config.lives == 5
    assert config.pacgum_count == 50
    assert config.points_per_pacgum == 20
    assert config.points_per_super_pacgum == 100
    assert config.points_per_ghost == 500
    assert config.seed == 123
    assert config.level_max_time == 120
    assert len(config.levels) == 10
    assert config.levels[0].width == 15
    assert config.levels[0].height == 15


def test_missing_values_use_defaults(tmp_path) -> None:
    config = load_config(write_config(tmp_path, {}))

    defaults = GameConfig()

    assert config.highscore_filename == defaults.highscore_filename
    assert config.lives == defaults.lives
    assert config.pacgum_count == defaults.pacgum_count
    assert config.points_per_pacgum == defaults.points_per_pacgum
    assert config.points_per_super_pacgum == defaults.points_per_super_pacgum
    assert config.points_per_ghost == defaults.points_per_ghost
    assert config.seed == defaults.seed
    assert config.level_max_time == defaults.level_max_time
    assert len(config.levels) == 10


def test_invalid_integer_values_use_defaults(tmp_path) -> None:
    data = {
        "lives": -1,
        "pacgum_count": 0,
        "points_per_pacgum": "ten",
        "points_per_super_pacgum": False,
        "points_per_ghost": -200,
        "seed": True,
        "level_max_time": 30,
    }

    config = load_config(write_config(tmp_path, data))

    assert config.lives == 3
    assert config.pacgum_count == 42
    assert config.points_per_pacgum == 10
    assert config.points_per_super_pacgum == 50
    assert config.points_per_ghost == 200
    assert config.seed == 42
    assert config.level_max_time == 90


def test_levels_are_padded_to_ten(tmp_path) -> None:
    data = {
        "levels": [
            {"width": 20, "height": 21},
            {"width": 22, "height": 23},
        ]
    }

    config = load_config(write_config(tmp_path, data))

    assert len(config.levels) == 10
    assert config.levels[0].width == 20
    assert config.levels[0].height == 21
    assert config.levels[1].width == 22
    assert config.levels[1].height == 23

    for level in config.levels[2:]:
        assert level.width == 15
        assert level.height == 15


def test_invalid_level_entries_use_defaults(tmp_path) -> None:
    data = {
        "levels": [
            {"width": 5, "height": 5},
            "invalid",
        ]
        + [
            {"width": 15, "height": 15}
            for _ in range(8)
        ]
    }

    config = load_config(write_config(tmp_path, data))

    assert config.levels[0].width == 15
    assert config.levels[0].height == 15
    assert config.levels[1].width == 15
    assert config.levels[1].height == 15


def test_comment_lines_are_ignored(tmp_path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        '# comment before config\n'
        '{\n'
        '  "lives": 4,\n'
        '# comment inside config\n'
        '  "level_max_time": 100\n'
        '}\n',
        encoding="utf-8",
    )

    config = load_config(str(config_path))

    assert config.lives == 4
    assert config.level_max_time == 100


def test_malformed_json_raises_value_error(tmp_path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text('{"lives": 3', encoding="utf-8")

    try:
        load_config(str(config_path))
    except ValueError as error:
        assert str(error) == "malformed JSON"
    else:
        raise AssertionError("Expected ValueError")


def test_non_object_root_raises_value_error(tmp_path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text("[1, 2, 3]", encoding="utf-8")

    try:
        load_config(str(config_path))
    except ValueError as error:
        assert str(error) == "configuration root must be a JSON object"
    else:
        raise AssertionError("Expected ValueError")