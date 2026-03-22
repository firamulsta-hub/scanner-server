from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
import json
import re

BASE_DIR = Path(__file__).resolve().parent.parent
CACHE_FILE = BASE_DIR / "data" / "scanner_cache.json"
SEARCH_DIRS = [
    BASE_DIR / "data" / "scanner_analysis",
    BASE_DIR,
]

def now_text() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M")

def ensure_cache_dir() -> None:
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)

def parse_int(text: str) -> int:
    text = text.strip().replace(",", "")
    m = re.search(r"-?\d+", text)
    return int(m.group()) if m else 0

def parse_float(text: str) -> float:
    text = text.strip().replace(",", "")
    m = re.search(r"-?\d+(?:\.\d+)?", text)
    return float(m.group()) if m else 0.0

def find_latest_summary() -> Path | None:
    files: list[Path] = []
    for folder in SEARCH_DIRS:
        if folder.exists():
            files.extend(folder.glob("scanner93b_summary_*.txt"))
            files.extend(folder.glob("scanner_93b_summary_*.txt"))
    if not files:
        return None
    return max(files, key=lambda p: p.stat().st_mtime)

def parse_summary_file(path: Path) -> dict:
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    date = ""
    total_candidates = 0
    pass_count = 0
    watch_count = 0
    skip_count = 0
    mode = None
    result = []

    for line in lines:
        if line.startswith("기준일자:"):
            date = line.split(":", 1)[1].strip()
        elif line.startswith("전체 후보 수:"):
            total_candidates = parse_int(line.split(":", 1)[1])
        elif line.startswith("PASS 수:"):
            pass_count = parse_int(line.split(":", 1)[1])
        elif line.startswith("WATCH 수:"):
            watch_count = parse_int(line.split(":", 1)[1])
        elif line.startswith("SKIP 수:"):
            skip_count = parse_int(line.split(":", 1)[1])
        elif line.startswith("[상위 PASS"):
            mode = "PASS"
        elif line.startswith("[상위 WATCH"):
            mode = "WATCH"
        elif " / " in line and mode in {"PASS", "WATCH"}:
            parts = [p.strip() for p in line.split(" / ")]
            if len(parts) < 9:
                continue
            item = {
                "code": parts[0].zfill(6),
                "name": parts[1],
                "scanner_type": parts[2],
                "market": "UNKNOWN",
                "current_price": parse_float(parts[3].replace("현재가:", "")),
                "change_percent": 0.0,
                "entry1": parse_float(parts[4].replace("진입1:", "")),
                "stop": parse_float(parts[5].replace("손절:", "")),
                "target1": parse_float(parts[6].replace("목표1:", "")),
                "rr": parse_float(parts[7].replace("RR:", "")),
                "status": mode,
                "comment": parts[8].replace("코멘트:", ""),
            }
            result.append(item)

    return {
        "summary": {
            "date": date or datetime.today().strftime("%Y%m%d"),
            "total_candidates": total_candidates,
            "pass_count": pass_count,
            "watch_count": watch_count,
            "skip_count": skip_count,
        },
        "result": result,
    }

def fetch_indexes() -> dict:
    try:
        import FinanceDataReader as fdr  # type: ignore

        end = datetime.now()
        start = end - timedelta(days=10)

        def one(symbol: str, name: str) -> dict:
            df = fdr.DataReader(symbol, start, end)
            if df is None or len(df) == 0:
                raise RuntimeError(f"{name} empty")
            close = float(df.iloc[-1]["Close"])
            if len(df) >= 2:
                prev = float(df.iloc[-2]["Close"])
                change = ((close / prev) - 1.0) * 100.0 if prev else 0.0
            else:
                change = 0.0
            return {
                "name": name,
                "value": round(close, 2),
                "change_percent": round(change, 2),
            }

        return {
            "kospi": one("KS11", "KOSPI"),
            "kosdaq": one("KQ11", "KOSDAQ"),
        }
    except Exception:
        return {
            "kospi": {"name": "KOSPI", "value": 0.0, "change_percent": 0.0},
            "kosdaq": {"name": "KOSDAQ", "value": 0.0, "change_percent": 0.0},
        }

def enrich_market_and_change(items: list[dict]) -> list[dict]:
    try:
        import FinanceDataReader as fdr  # type: ignore
    except Exception:
        return items

    try:
        krx = fdr.StockListing("KRX")
        market_map: dict[str, str] = {}
        if "Symbol" in krx.columns and "Market" in krx.columns:
            for _, row in krx.iterrows():
                code = str(row["Symbol"]).zfill(6)
                market = str(row["Market"]).upper()
                if "KOSDAQ" in market:
                    market_map[code] = "KOSDAQ"
                elif "KOSPI" in market:
                    market_map[code] = "KOSPI"
                else:
                    market_map[code] = market
    except Exception:
        market_map = {}

    end = datetime.now()
    start = end - timedelta(days=7)

    for item in items:
        code = str(item.get("code", "")).zfill(6)
        if code in market_map:
            item["market"] = market_map[code]
        else:
            item["market"] = "KOSPI" if code.startswith("0") else "KOSDAQ"

        try:
            df = fdr.DataReader(code, start, end)
            if df is not None and len(df) >= 2:
                prev_close = float(df.iloc[-2]["Close"])
                current_price = float(item.get("current_price", 0.0))
                if prev_close:
                    item["change_percent"] = round(((current_price / prev_close) - 1.0) * 100.0, 2)
        except Exception:
            item["change_percent"] = 0.0

    return items

def main() -> None:
    ensure_cache_dir()
    summary_file = find_latest_summary()

    if summary_file is None:
        payload = {
            "updated_at": now_text(),
            "indexes": fetch_indexes(),
            "scanners": {
                "93b": {
                    "meta": {
                        "key": "93b",
                        "title": "Total 9.3B (전체 조건 통합 시스템)",
                        "description": "후보군 전체를 통합 평가해 PASS/WATCH/SKIP으로 나눕니다.",
                        "updated_at": now_text(),
                        "summary_text": "93b 요약 파일을 찾지 못했습니다.",
                        "stale_from_cache": False,
                    },
                    "summary": {
                        "date": datetime.today().strftime("%Y%m%d"),
                        "total_candidates": 0,
                        "pass_count": 0,
                        "watch_count": 0,
                        "skip_count": 0,
                    },
                    "result": [],
                }
            },
            "errors": {"93b": "summary file not found"},
        }
    else:
        parsed = parse_summary_file(summary_file)
        parsed["result"] = enrich_market_and_change(parsed["result"])

        payload = {
            "updated_at": now_text(),
            "indexes": fetch_indexes(),
            "scanners": {
                "93b": {
                    "meta": {
                        "key": "93b",
                        "title": "Total 9.3B (전체 조건 통합 시스템)",
                        "description": "후보군 전체를 통합 평가해 PASS/WATCH/SKIP으로 나눕니다.",
                        "updated_at": now_text(),
                        "summary_text": (
                            "스캐너 9.3B 통합 요약\n"
                            "==================================================\n"
                            f"기준일시: {parsed['summary']['date']}\n"
                            f"전체 후보 수: {parsed['summary']['total_candidates']}\n"
                            f"PASS 수: {parsed['summary']['pass_count']}\n"
                            f"WATCH 수: {parsed['summary']['watch_count']}\n"
                            f"SKIP 수: {parsed['summary']['skip_count']}"
                        ),
                        "stale_from_cache": False,
                    },
                    "summary": parsed["summary"],
                    "result": parsed["result"],
                }
            },
            "errors": {},
        }

    CACHE_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print("[DONE] 93b cache updated with market/change")

if __name__ == "__main__":
    main()
