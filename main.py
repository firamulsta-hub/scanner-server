from __future__ import annotations

from pathlib import Path
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import json
import subprocess
import sys

BASE_DIR = Path(__file__).resolve().parent
CACHE_FILE = BASE_DIR / "data" / "scanner_cache.json"

app = FastAPI(title="Leading Scanner API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def safe_load_cache() -> dict:
    try:
        if not CACHE_FILE.exists():
            return {
                "updated_at": None,
                "indexes": {},
                "scanners": {},
                "errors": {"server": f"cache file not found: {CACHE_FILE}"},
            }

        text = CACHE_FILE.read_text(encoding="utf-8")
        data = json.loads(text)

        if not isinstance(data, dict):
            return {
                "updated_at": None,
                "indexes": {},
                "scanners": {},
                "errors": {"server": "invalid cache format"},
            }

        data.setdefault("updated_at", None)
        data.setdefault("indexes", {})
        data.setdefault("scanners", {})
        data.setdefault("errors", {})
        return data
    except Exception as e:
        return {
            "updated_at": None,
            "indexes": {},
            "scanners": {},
            "errors": {"server": f"cache load failed: {type(e).__name__}: {e}"},
        }


@app.get("/")
def root():
    return {"status": "ok", "message": "leading scanner railway server running"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/dashboard")
def dashboard():
    return safe_load_cache()


@app.get("/indexes")
def indexes():
    return safe_load_cache().get("indexes", {})


@app.get("/scan/{scanner_key}")
def scan(scanner_key: str, market: str | None = Query(default=None)):
    cache = safe_load_cache()
    scanner = cache.get("scanners", {}).get(scanner_key)

    if not scanner:
        return {
            "error": "scanner not found",
            "scanner_key": scanner_key,
            "updated_at": cache.get("updated_at"),
        }

    result = scanner.get("result", [])
    if market:
        result = [item for item in result if item.get("market", "").lower() == market.lower()]

    return {
        "meta": scanner.get("meta", {}),
        "summary": scanner.get("summary"),
        "strategy": scanner.get("strategy"),
        "result": result,
        "updated_at": cache.get("updated_at"),
    }


@app.get("/refresh")
def refresh():
    try:
        job_file = BASE_DIR / "jobs" / "run_scanners.py"
        result = subprocess.run(
            [sys.executable, str(job_file)],
            cwd=str(BASE_DIR),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=600,
        )

        cache = safe_load_cache()
        cache["refresh_stdout"] = (result.stdout or "")[-4000:]
        cache["refresh_stderr"] = (result.stderr or "")[-4000:]
        cache["refresh_returncode"] = result.returncode
        return cache
    except Exception as e:
        cache = safe_load_cache()
        cache.setdefault("errors", {})
        cache["errors"]["refresh"] = f"{type(e).__name__}: {e}"
        return cache
