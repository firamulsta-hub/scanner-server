from pathlib import Path
import sys

# Add project root to path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from services.scanner_runner import run_all_scanners


if __name__ == "__main__":
    result = run_all_scanners()
    print(result)
