from dataclasses import dataclass
from pathlib import Path
import json
def is_valid_name(name) -> bool:
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
    if not isinstance(name ,str):
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
    final_list = []
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
    final_format = {}
    with open(file=path, mode='r+') as score_file:
        content = score_file.read()
        if len(content.strip()) == 0:
            return []
        final_format: list[dict] = json.load(content)
    names = validate_name(final_format)
    scores = validate_score(final_format)
    

