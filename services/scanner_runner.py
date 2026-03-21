from __future__ import annotations

from datetime import datetime
from pathlib import Path
import copy
import json
import subprocess
import sys
from typing import Any

from .cache_store import load_cache, save_cache

BASE_DIR = Path(__file__).resolve().parent.parent

SCRIPT_MAP = {
    "50": "scanner_stable.py",
    "51": "scanner_swing.py",
    "60": "scanner_60.py",
    "70": "scanner_70.py",
    "92": "scanner_92_strategy.py",
    "93b": "scanner_93b_integrated.py",
}

SCANNER_INFO: dict[str, dict[str, str]] = {
    "50": {
        "title": "Stable 5.0 (안정형)",
        "description": "상대적으로 안정적인 흐름의 종목을 찾는 스캐너입니다.",
    },
    "51": {
        "title": "Swing 5.1 (단타형)",
        "description": "단기 탄력과 스윙 흐름을 함께 보는 스캐너입니다.",
    },
    "60": {
        "title": "Force 6.0 (세력포착형)",
        "description": "강한 수급과 추세 강화 구간을 포착하는 스캐너입니다.",
    },
    "70": {
        "title": "Early 7.0 (세력초기진입포착형)",
        "description": "초기 진입 구간을 빠르게 찾는 스캐너입니다.",
    },
    "92": {
        "title": "Strategy 9.2 (자동 매매 전략 추천 시스템)",
        "description": "시장 상태에 맞는 스캐너와 비중을 자동 추천합니다.",
    },
    "93b": {
        "title": "Total 9.3B (전체 조건 통합 시스템)",
        "description": "후보군 전체를 통합 평가해 PASS/WATCH/SKIP으로 나눕니다.",
    },
}


def now_text() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def _find_json_start(text: str) -> int:
    obj = text.find("{")
    arr = text.find("[")
    indexes = [i for i in [obj, arr] if i >= 0]
    return min(indexes) if indexes else -1


def _run_python_script(filename: str) -> dict[str, Any]:
    script_path = BASE_DIR / filename
    if not script_path.exists():
        raise FileNotFoundError(f"scanner file not found: {script_path}")

    result = subprocess.run(
        [sys.executable, str(script_path)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=str(BASE_DIR),
        timeout=300,
    )

    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or f"script failed: {filename}")

    stdout = (result.stdout or "").strip()
    start = _find_json_start(stdout)
    if start < 0:
        raise ValueError(f"json output not found: {filename}\nstdout={stdout[:500]}")

    parsed = json.loads(stdout[start:])
    if not isinstance(parsed, dict):
        raise ValueError(f"json root must be object: {filename}")
    return parsed


def _to_market(value: str | None) -> str:
    text = (value or "").upper()
    if "KOSPI" in text or "코스피" in text:
        return "KOSPI"
    if "KOSDAQ" in text or "코스닥" in text:
        return "KOSDAQ"
    return text or "UNKNOWN"


def _normalize_item(item: dict[str, Any], scanner_key: str) -> dict[str, Any]:
    code = str(item.get("code", "")).zfill(6) if item.get("code") is not None else ""
    return {
        "code": code,
        "name": item.get("name", ""),
        "status": item.get("status", "WATCH"),
        "market": _to_market(item.get("market")),
        "current_price": float(item.get("current_price", item.get("price", 0)) or 0),
        "change_percent": float(item.get("change_percent", item.get("change_rate", 0)) or 0),
        "scanner_type": str(item.get("scanner_type", item.get("scanner", scanner_key))),
        "entry1": float(item["entry1"]) if item.get("entry1") is not None else None,
        "stop": float(item["stop"]) if item.get("stop") is not None else None,
        "target1": float(item.get("target1", item.get("target", 0))) if item.get("target1") is not None or item.get("target") is not None else None,
        "rr": float(item["rr"]) if item.get("rr") is not None else None,
        "comment": item.get("comment"),
    }


def _build_summary_text(scanner_key: str, raw: dict[str, Any], updated_at: str) -> str:
    if scanner_key == "92":
        strategy = raw.get("strategy", raw)
        return "\n".join([
            "스캐너 9.2 자동 전략 추천",
            "=" * 50,
            f"기준일시: {strategy.get('date', updated_at)}",
            f"시장 상태: {strategy.get('market_mode', '-')}",
            f"추천 스캐너: {', '.join(strategy.get('recommended_scanners', [])) if isinstance(strategy.get('recommended_scanners'), list) else strategy.get('recommended_scanners', '-')}",
            f"권장 비중: {strategy.get('position_size', '-')}",
            f"매매 스타일: {strategy.get('strategy_type', '-')}",
            f"코멘트: {strategy.get('comment', '-')}",
        ])

    if scanner_key == "93b":
        summary = raw.get("summary", raw)
        return "\n".join([
            "스캐너 9.3B 통합 요약",
            "=" * 50,
            f"기준일시: {summary.get('date', updated_at)}",
            f"전체 후보 수: {summary.get('total_candidates', '-')}",
            f"PASS 수: {summary.get('pass_count', '-')}",
            f"WATCH 수: {summary.get('watch_count', '-')}",
            f"SKIP 수: {summary.get('skip_count', '-')}",
        ])

    return "\n".join([
        SCANNER_INFO[scanner_key]["title"],
        "=" * 50,
        f"기준일시: {updated_at}",
    ])


def _normalize_scanner(scanner_key: str, raw: dict[str, Any]) -> dict[str, Any]:
    updated_at = now_text()
    meta = {
        "key": scanner_key,
        "title": SCANNER_INFO[scanner_key]["title"],
        "description": SCANNER_INFO[scanner_key]["description"],
        "updated_at": updated_at,
        "summary_text": _build_summary_text(scanner_key, raw, updated_at),
        "stale_from_cache": False,
    }

    items = raw.get("result", [])
    if not isinstance(items, list):
        items = []

    normalized = {
        "meta": meta,
        "result": [_normalize_item(item, scanner_key) for item in items if isinstance(item, dict)],
    }

    if scanner_key == "92":
        normalized["strategy"] = raw.get("strategy", raw)
    if scanner_key == "93b":
        normalized["summary"] = raw.get("summary", raw)

    return normalized


def _default_indexes() -> dict[str, Any]:
    return {
        "kospi": {"name": "KOSPI", "value": 2718.35, "change_percent": 0.42},
        "kosdaq": {"name": "KOSDAQ", "value": 889.44, "change_percent": -0.31},
    }


def _build_error_scanner(key: str, error_text: str, previous: dict[str, Any] | None) -> dict[str, Any]:
    if previous:
        copied = copy.deepcopy(previous)
        copied.setdefault("meta", {})
        copied["meta"]["stale_from_cache"] = True
        copied["meta"]["last_error"] = error_text
        copied["meta"]["summary_text"] = (
            copied["meta"].get("summary_text", SCANNER_INFO[key]["title"]) +
            f"\n\n[주의] 최신 실행 실패로 이전 캐시를 표시 중\n사유: {error_text}"
        )
        return copied

    return {
        "meta": {
            "key": key,
            "title": SCANNER_INFO[key]["title"],
            "description": SCANNER_INFO[key]["description"],
            "updated_at": now_text(),
            "summary_text": f"{SCANNER_INFO[key]['title']}\n실행 실패: {error_text}",
            "stale_from_cache": False,
            "last_error": error_text,
        },
        "result": [],
    }


def run_all_scanners() -> dict[str, Any]:
    previous = load_cache()
    payload: dict[str, Any] = {
        "updated_at": now_text(),
        "indexes": previous.get("indexes") or _default_indexes(),
        "scanners": {},
        "errors": {},
    }

    for key, filename in SCRIPT_MAP.items():
        try:
            print(f"[RUN] {key} -> {filename}", flush=True)
            raw = _run_python_script(filename)
            payload["scanners"][key] = _normalize_scanner(key, raw)
            print(f"[OK] {key}", flush=True)
        except Exception as e:
            error_text = f"{type(e).__name__}: {e}"
            payload["errors"][key] = error_text
            print(f"[FAIL] {key} -> {error_text}", flush=True)
            old = previous.get("scanners", {}).get(key)
            payload["scanners"][key] = _build_error_scanner(key, error_text, old)

    save_cache(payload)
    print("[DONE] scanner_cache.json saved", flush=True)
    return payload
