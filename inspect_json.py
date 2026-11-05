
import json
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent
RAW_DIR = PROJECT_DIR / "data" / "raw"

files = [
    "competitions.json",
    "complexes.json",
    "rankings.json"
]

for filename in files:
    file_path = RAW_DIR / filename

    print("\n" + "=" * 50)
    print("FILE:", filename)
    print("=" * 50)

    if not file_path.exists():
        print("File not found:", file_path)
        continue

    with file_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    print("Top-level keys:", list(data.keys()))

    for key, value in data.items():
        if isinstance(value, list):
            print(f"\n{key}: {len(value)} records")

            if value and isinstance(value[0], dict):
                print("First record fields:", list(value[0].keys()))

                print("Sample record:")
                print(json.dumps(value[0], indent=2)[:1000])

