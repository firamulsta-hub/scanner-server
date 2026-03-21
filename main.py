from __future__ import annotations

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from services.cache_store import load_cache
from services.scanner_runner import run_all_scanners
from services.summary_builder import scanner_descriptions

app = FastAPI(title="Leading Scanner API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SCANNER_LABELS = scanner_descriptions()


@app.on_event("startup")
def startup_event() -> None:
    cache = load_cache()
    if not cache.get("updated_at"):
        run_all_scanners()


@app.get("/")
def root():
    return {"message": "leading scanner server running"}


@app.get("/refresh")
def refresh():
    return run_all_scanners()


@app.get("/dashboard")
def dashboard():
    return load_cache()


@app.get("/descriptions")
def descriptions():
    return SCANNER_LABELS


@app.get("/scan/{scanner_key}")
def scan(scanner_key: str, market: str | None = Query(default=None)):
    cache = load_cache()
    scanner = cache.get("scanners", {}).get(scanner_key)
    if not scanner:
        return {"error": "scanner not found", "scanner_key": scanner_key}

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


@app.get("/indexes")
def indexes():
    cache = load_cache()
    return cache.get("indexes", {})
