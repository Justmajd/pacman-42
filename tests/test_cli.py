from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "pac-man.py"

def test_cli_with_valid_config_succeeds(tmp_path, monkeypatch) -> None:
    import importlib.util

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

    spec = importlib.util.spec_from_file_location("pacman_cli", SCRIPT)
    assert spec is not None
    assert spec.loader is not None

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    calls = []

    def fake_run_app(config) -> int:
        calls.append(config)
        return 0

    monkeypatch.setattr(module, "run_app", fake_run_app)
    monkeypatch.setattr(
        sys,
        "argv",
        [str(SCRIPT), str(config_path)],
    )

    result = module.main()

    assert result == 0
    assert len(calls) == 1