from services.scanner_runner import run_all_scanners


if __name__ == "__main__":
    payload = run_all_scanners()
    print("scanner refresh complete:", payload.get("updated_at"))
