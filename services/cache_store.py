from __future__ import annotations

from pathlib import Path
import json
from typing import Any


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
CACHE_FILE = DATA_DIR / "scanner_cache.json"


def load_cache() -> dict[str, Any]:
    if not CACHE_FILE.exists():
        return {"updated_at": None, "indexes": {}, "scanners": {}}
    with CACHE_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_cache(payload: dict[str, Any]) -> None:
    with CACHE_FILE.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
