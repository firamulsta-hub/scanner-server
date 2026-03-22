from __future__ import annotations

from pathlib import Path
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import json
import subprocess
import sys

BASE_DIR = Path(__file__).resolve().parent
CACHE_FILE = BASE_DIR / "data" / "scanner_cache.json"

app = FastAPI(title="Leading Scanner API - 93B Only")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def empty_payload() -> dict:
    return {
        "updated_at": None,
        "indexes": {},
        "scanners": {},
        "errors": {},
    }

def load_cache() -> dict:
    try:
        if not CACHE_FILE.exists():
            return empty_payload()
        data = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return empty_payload()
        data.setdefault("updated_at", None)
        data.setdefault("indexes", {})
        data.setdefault("scanners", {})
        data.setdefault("errors", {})
        return data
    except Exception as e:
        payload = empty_payload()
        payload["errors"]["server"] = f"{type(e).__name__}: {e}"
        return payload

@app.get("/")
def root():
    return {"status": "ok", "message": "leading scanner server running (93b only)"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/dashboard")
def dashboard():
    return load_cache()

@app.get("/indexes")
def indexes():
    return load_cache().get("indexes", {})

@app.get("/scan/{scanner_key}")
def scan(scanner_key: str, market: str | None = Query(default=None)):
    cache = load_cache()
    scanner = cache.get("scanners", {}).get(scanner_key)
    if not scanner:
        return {
            "error": "scanner not found",
            "scanner_key": scanner_key,
            "updated_at": cache.get("updated_at"),
            "result": [],
        }

    result = scanner.get("result", [])
    if market and market != "ALL":
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
    cache = load_cache()
    cache["refresh_returncode"] = result.returncode
    cache["refresh_stdout"] = (result.stdout or "")[-3000:]
    cache["refresh_stderr"] = (result.stderr or "")[-3000:]
    return cache
