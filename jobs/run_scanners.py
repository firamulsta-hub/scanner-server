from services.scanner_runner import run_all_scanners

if __name__ == "__main__":
    result = run_all_scanners()
    print("scanner refresh complete")
    print(result.get("updated_at"))
