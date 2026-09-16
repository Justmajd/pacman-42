import json
from pathlib import Path

import pytest

from src.highscore import (
    HighscoreEntry,
    load_highscores,
    normalize_entries,
    save_highscores,
    validate_name,
    validate_score,
)


def test_validate_name_accepts_valid_names() -> None:
    assert validate_name("MAJD") == "MAJD"
    assert validate_name("Majd 42") == "Majd 42"
    assert validate_name("1234567890") == "1234567890"


@pytest.mark.parametrize(  # type: ignore[misc]
    "name",
    [
        "",
        "           ",
        "12345678901",
        "Majd!",
        "Majd_Omar",
        "Majd-Omar",
        "Majd\tOmar",
    ],
)
def test_validate_name_rejects_invalid_names(name: object) -> None:
    with pytest.raises(ValueError):
        validate_name(name)


@pytest.mark.parametrize(  # type: ignore[misc]
    "name",
    [
        42,
        None,
        True,
        [],
        {},
    ],
)
def test_validate_name_rejects_non_strings(name: object) -> None:
    with pytest.raises(ValueError):
        validate_name(name)


def test_validate_score_accepts_non_negative_integers() -> None:
    assert validate_score(0) == 0
    assert validate_score(42) == 42
    assert validate_score(100000) == 100000


@pytest.mark.parametrize(  # type: ignore[misc]
    "score",
    [
        -1,
        -500,
        True,
        False,
        3.5,
        "42",
        None,
    ],
)
def test_validate_score_rejects_invalid_values(score: object) -> None:
    with pytest.raises(ValueError):
        validate_score(score)


def test_normalize_entries_sorts_highest_score_first() -> None:
    entries = [
        HighscoreEntry("ALI", 100),
        HighscoreEntry("MAJD", 500),
        HighscoreEntry("OMAR", 300),
    ]

    result = normalize_entries(entries)

    assert result == [
        HighscoreEntry("MAJD", 500),
        HighscoreEntry("OMAR", 300),
        HighscoreEntry("ALI", 100),
    ]


def test_normalize_entries_sorts_equal_scores_by_name() -> None:
    entries = [
        HighscoreEntry("OMAR", 500),
        HighscoreEntry("MAJD", 500),
        HighscoreEntry("ALI", 500),
    ]

    result = normalize_entries(entries)

    assert result == [
        HighscoreEntry("ALI", 500),
        HighscoreEntry("MAJD", 500),
        HighscoreEntry("OMAR", 500),
    ]


def test_normalize_entries_keeps_only_top_ten() -> None:
    entries = [
        HighscoreEntry(f"P{index}", index * 100)
        for index in range(12)
    ]

    result = normalize_entries(entries)

    assert len(result) == 10
    assert result[0].score == 1100
    assert result[-1].score == 200


def test_normalize_entries_does_not_modify_original_list() -> None:
    entries = [
        HighscoreEntry("ALI", 100),
        HighscoreEntry("MAJD", 500),
    ]
    original = list(entries)

    normalize_entries(entries)

    assert entries == original


def test_load_missing_file_returns_empty_list(tmp_path: Path) -> None:
    path = tmp_path / "missing.json"

    result = load_highscores(str(path))

    assert result == []


def test_load_empty_file_returns_empty_list(tmp_path: Path) -> None:
    path = tmp_path / "highscore.json"
    path.write_text("", encoding="utf-8")

    result = load_highscores(str(path))

    assert result == []


def test_load_corrupt_json_returns_empty_list(tmp_path: Path) -> None:
    path = tmp_path / "highscore.json"
    path.write_text("{broken json", encoding="utf-8")

    result = load_highscores(str(path))

    assert result == []


def test_load_wrong_root_type_returns_empty_list(tmp_path: Path) -> None:
    path = tmp_path / "highscore.json"
    path.write_text(
        json.dumps({"name": "MAJD", "score": 500}),
        encoding="utf-8",
    )

    result = load_highscores(str(path))

    assert result == []


def test_load_skips_invalid_entries_but_keeps_valid_ones(
        tmp_path: Path) -> None:
    path = tmp_path / "highscore.json"

    data = [
        {"name": "MAJD", "score": 500},
        {"name": "BAD!", "score": 900},
        {"name": "OMAR", "score": 300},
        {"name": "ALI"},
        "broken entry",
        {"name": "NEGATIVE", "score": -1},
    ]

    path.write_text(json.dumps(data), encoding="utf-8")

    result = load_highscores(str(path))

    assert result == [
        HighscoreEntry("MAJD", 500),
        HighscoreEntry("OMAR", 300),
    ]


def test_load_normalizes_and_keeps_top_ten(tmp_path: Path) -> None:
    path = tmp_path / "highscore.json"

    data = [
        {"name": f"P{index}", "score": index * 100}
        for index in range(12)
    ]

    path.write_text(json.dumps(data), encoding="utf-8")

    result = load_highscores(str(path))

    assert len(result) == 10
    assert result[0].score == 1100
    assert result[-1].score == 200


def test_save_and_load_round_trip(tmp_path: Path) -> None:
    path = tmp_path / "highscore.json"

    entries = [
        HighscoreEntry("OMAR", 300),
        HighscoreEntry("MAJD", 500),
        HighscoreEntry("ALI", 100),
    ]

    save_highscores(str(path), entries)
    loaded = load_highscores(str(path))

    assert loaded == [
        HighscoreEntry("MAJD", 500),
        HighscoreEntry("OMAR", 300),
        HighscoreEntry("ALI", 100),
    ]


def test_save_writes_valid_json(tmp_path: Path) -> None:
    path = tmp_path / "highscore.json"

    entries = [
        HighscoreEntry("MAJD", 500),
        HighscoreEntry("OMAR", 300),
    ]

    save_highscores(str(path), entries)

    with open(path, mode="r", encoding="utf-8") as score_file:
        data = json.load(score_file)

    assert data == [
        {"name": "MAJD", "score": 500},
        {"name": "OMAR", "score": 300},
    ]


def test_save_keeps_only_top_ten(tmp_path: Path) -> None:
    path = tmp_path / "highscore.json"

    entries = [
        HighscoreEntry(f"P{index}", index * 100)
        for index in range(12)
    ]

    save_highscores(str(path), entries)
    loaded = load_highscores(str(path))

    assert len(loaded) == 10
    assert loaded[0].score == 1100
    assert loaded[-1].score == 200


def test_save_rejects_invalid_name(tmp_path: Path) -> None:
    path = tmp_path / "highscore.json"

    entries = [
        HighscoreEntry("BAD!", 500),
    ]

    with pytest.raises(ValueError):
        save_highscores(str(path), entries)


def test_save_rejects_invalid_score(tmp_path: Path) -> None:
    path = tmp_path / "highscore.json"

    entries = [
        HighscoreEntry("MAJD", -1),
    ]

    with pytest.raises(ValueError):
        save_highscores(str(path), entries)


def test_save_uses_temporary_file_and_replaces_it(tmp_path: Path) -> None:
    path = tmp_path / "highscore.json"
    temp_path = tmp_path / "highscore.json.tmp"

    entries = [
        HighscoreEntry("MAJD", 500),
    ]

    save_highscores(str(path), entries)

    assert path.exists()
    assert not temp_path.exists()
    assert load_highscores(str(path)) == [
        HighscoreEntry("MAJD", 500),
    ]


def test_save_replaces_existing_file(tmp_path: Path) -> None:
    path = tmp_path / "highscore.json"

    old_data = [
        {"name": "OLD", "score": 10},
    ]
    path.write_text(json.dumps(old_data), encoding="utf-8")

    save_highscores(
        str(path),
        [
            HighscoreEntry("MAJD", 500),
            HighscoreEntry("OMAR", 300),
        ],
    )

    assert load_highscores(str(path)) == [
        HighscoreEntry("MAJD", 500),
        HighscoreEntry("OMAR", 300),
    ]


def test_load_highscores_returns_empty_list_on_os_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    path = tmp_path / "highscores.json"
    path.write_text("[]", encoding="utf-8")

    def failing_open(*args: object, **kwargs: object) -> None:
        raise PermissionError("permission denied")

    monkeypatch.setattr("builtins.open", failing_open)

    assert load_highscores(str(path)) == []
