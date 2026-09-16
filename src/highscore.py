from dataclasses import dataclass
from pathlib import Path
import json
import os


def is_valid_name(name: str) -> bool:
    if not name:
        return False

    for char in name:
        if not char.isalnum() and char != " ":
            return False

    return True


@dataclass(frozen=True)
class HighscoreEntry:
    name: str
    score: int


def validate_name(name: object) -> str:
    if not isinstance(name, str):
        raise ValueError("the name should be a string")
    if len(name) == 0:
        raise ValueError("field is empty")
    if len(name) > 10:
        raise ValueError("name is more than 10 characters")
    if not is_valid_name(name=name):
        raise ValueError("name have symbols")
    if name.isspace():
        raise ValueError("name have only spaces")
    return name


def validate_score(score: object) -> int:
    if not isinstance(score, int) or isinstance(score, bool):
        raise ValueError("score is not an int")
    if score < 0:
        raise ValueError("score shouldn't be under 0")
    return score


def normalize_entries(
    entries: list[HighscoreEntry],
) -> list[HighscoreEntry]:
    sorted_list = sorted(entries, key=lambda x: (-x.score, x.name))
    final_list: list[HighscoreEntry] = []
    if len(sorted_list) < 10:
        for _ in range(len(sorted_list)):
            final_list.append(sorted_list[_])
    else:
        for _ in range(10):
            final_list.append(sorted_list[_])
    return final_list


def load_highscores(path: str) -> list[HighscoreEntry]:
    file_path = Path(path)
    if not file_path.exists():
        return []
    final_format: list[dict[str, object]] = []
    try:
        with open(file=path, mode='r', encoding="utf-8") as score_file:
            formatted_json: object = json.load(score_file)
        if not isinstance(formatted_json, list):
            return []
        for x in formatted_json:
            if isinstance(x, dict):
                final_format.append(x)
        final_list: list[HighscoreEntry] = []
    except json.JSONDecodeError:
        return []
    except OSError:
        return []

    for _ in final_format:
        try:
            name = validate_name(_["name"])
            score = validate_score(_["score"])
        except ValueError:
            continue
        except KeyError:
            continue
        entry = HighscoreEntry(name=name, score=score)
        final_list.append(entry)
    final_list = normalize_entries(final_list)
    return final_list


def save_highscores(
    path: str,
    entries: list[HighscoreEntry],
) -> None:
    temp_list: list[HighscoreEntry] = []
    for entry in entries:
        name = validate_name(entry.name)
        score = validate_score(entry.score)
        validated_entry = HighscoreEntry(name=name, score=score)
        temp_list.append(validated_entry)
    normalized_entries = normalize_entries(temp_list)
    final_list: list[dict[str, object]] = []
    for _ in normalized_entries:
        temp_dict = {"name": _.name, "score": _.score}
        final_list.append(temp_dict)
    file_path = Path(path)
    temp_path = file_path.with_name(file_path.name + ".tmp")
    with open(file=temp_path, mode='w', encoding="utf-8") as score_file:
        json.dump(final_list, score_file)
    os.replace(temp_path, file_path)
