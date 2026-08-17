import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "pac-man.py"


def test_cli_without_argument_fails() -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPT)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0
    assert "Error:" in result.stdout
    assert "Traceback" not in result.stdout
    assert "Traceback" not in result.stderr


def test_cli_with_missing_file_fails_cleanly() -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "does-not-exist.json"],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0
    assert "could not open" in result.stdout.lower()
    assert "Traceback" not in result.stdout
    assert "Traceback" not in result.stderr


def test_cli_with_valid_config_succeeds(tmp_path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        """
        {
            "lives": 3,
            "levels": [
                {"width": 15, "height": 15},
                {"width": 15, "height": 15},
                {"width": 15, "height": 15},
                {"width": 15, "height": 15},
                {"width": 15, "height": 15},
                {"width": 15, "height": 15},
                {"width": 15, "height": 15},
                {"width": 15, "height": 15},
                {"width": 15, "height": 15},
                {"width": 15, "height": 15}
            ]
        }
        """,
        encoding="utf-8",
    )

    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(config_path)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "Traceback" not in result.stdout
    assert "Traceback" not in result.stderr