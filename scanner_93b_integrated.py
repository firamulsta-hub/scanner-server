import json
import re
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent

SEARCH_DIRS = [
    BASE_DIR / "data" / "scanner_analysis",
    BASE_DIR,
]

def find_latest_summary():
    candidates = []
    for folder in SEARCH_DIRS:
        if folder.exists():
            candidates.extend(folder.glob("scanner93b_summary_*.txt"))
            candidates.extend(folder.glob("scanner_93b_summary_*.txt"))
    if not candidates:
        return None
    return max(candidates, key=lambda p: p.stat().st_mtime)

def parse_int(text):
    text = text.strip().replace(",", "")
    m = re.search(r"-?\d+", text)
    return int(m.group()) if m else 0

def parse_float(text):
    text = text.strip().replace(",", "")
    m = re.search(r"-?\d+(?:\.\d+)?", text)
    return float(m.group()) if m else 0.0

def parse_line(line):
    parts = [p.strip() for p in line.split(" / ")]
    if len(parts) < 9:
        return None
    try:
        return {
            "code": parts[0].zfill(6),
            "name": parts[1],
            "scanner_type": parts[2],
            "current_price": parse_float(parts[3].replace("현재가:", "")),
            "entry1": parse_float(parts[4].replace("진입1:", "")),
            "stop": parse_float(parts[5].replace("손절:", "")),
            "target1": parse_float(parts[6].replace("목표1:", "")),
            "rr": parse_float(parts[7].replace("RR:", "")),
            "comment": parts[8].replace("코멘트:", "") if len(parts) >= 9 else "",
            "market": "UNKNOWN",
            "change_percent": 0.0,
        }
    except Exception:
        return None

def main():
    summary_file = find_latest_summary()

    if not summary_file or not summary_file.exists():
        payload = {
            "summary": {
                "date": datetime.today().strftime("%Y%m%d"),
                "total_candidates": 0,
                "pass_count": 0,
                "watch_count": 0,
                "skip_count": 0,
            },
            "result": []
        }
        print(json.dumps(payload, ensure_ascii=False))
        return

    text = summary_file.read_text(encoding="utf-8", errors="replace")
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
            item = parse_line(line)
            if item:
                item["status"] = mode
                result.append(item)

    payload = {
        "summary": {
            "date": date or datetime.today().strftime("%Y%m%d"),
            "total_candidates": total_candidates,
            "pass_count": pass_count,
            "watch_count": watch_count,
            "skip_count": skip_count,
        },
        "result": result,
    }

    print(json.dumps(payload, ensure_ascii=False))

if __name__ == "__main__":
    main()
