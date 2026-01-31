import json
from pathlib import Path


def _base_dir() -> Path:
    return Path(__file__).resolve().parents[2]


def _load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_locale() -> dict:
    base = _base_dir()
    return _load_json(base / "config" / "locale_entebbe.json")


def load_territory() -> dict:
    base = _base_dir()
    return _load_json(base / "data" / "territory_entebbe.json")


def load_techs() -> dict:
    base = _base_dir()
    return _load_json(base / "data" / "technician_roster.json")
