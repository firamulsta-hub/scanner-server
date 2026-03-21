from __future__ import annotations

from .cache_store import save_cache
from .summary_builder import build_default_payload


def run_all_scanners() -> dict:
    payload = build_default_payload()
    save_cache(payload)
    return payload
