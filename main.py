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


def safe_load_cache():
    try:
        cache = load_cache()
        if not isinstance(cache, dict):
            return {"updated_at": None, "indexes": {}, "scanners": {}, "errors": {"server": "invalid cache format"}}
        cache.setdefault("updated_at", None)
        cache.setdefault("indexes", {})
        cache.setdefault("scanners", {})
        return cache
    except Exception as e:
        return {
            "updated_at": None,
            "indexes": {},
            "scanners": {},
            "errors": {"server": f"cache load failed: {type(e).__name__}: {e}"},
        }


@app.on_event("startup")
def startup_event() -> None:
    # Railway에서는 startup에서 무거운 작업을 돌리지 않음
    # 앱이 먼저 살아 있어야 /dashboard 와 /refresh가 바로 응답 가능
    safe_load_cache()


@app.get("/")
def root():
    return {
        "message": "leading scanner server running",
        "status": "ok",
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/refresh")
def refresh():
    try:
        return run_all_scanners()
    except Exception as e:
        cache = safe_load_cache()
        cache.setdefault("errors", {})
        cache["errors"]["refresh"] = f"{type(e).__name__}: {e}"
        return cache


@app.get("/dashboard")
def dashboard():
    return safe_load_cache()


@app.get("/descriptions")
def descriptions():
    return SCANNER_LABELS


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


@app.get("/indexes")
def indexes():
    cache = safe_load_cache()
    return cache.get("indexes", {})
