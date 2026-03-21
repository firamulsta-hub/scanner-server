from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_STABLE_DIR = DATA_DIR / "scanner_output"
OUTPUT_SWING_DIR = DATA_DIR / "scanner_output_swing"
OUTPUT_60_DIR = DATA_DIR / "scanner_output_60"
OUTPUT_70_DIR = DATA_DIR / "scanner_output_70"
ANALYSIS_DIR = DATA_DIR / "scanner_analysis"

for _p in [DATA_DIR, OUTPUT_STABLE_DIR, OUTPUT_SWING_DIR, OUTPUT_60_DIR, OUTPUT_70_DIR, ANALYSIS_DIR]:
    _p.mkdir(parents=True, exist_ok=True)

def ensure_dir(pathlike):
    p = Path(pathlike)
    p.mkdir(parents=True, exist_ok=True)
    return str(p)
