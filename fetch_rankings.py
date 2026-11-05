
import os
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

# Locate project folder and load API key
PROJECT_DIR = Path(__file__).resolve().parent
load_dotenv(PROJECT_DIR / ".env", override=True)
API_KEY = os.getenv("SPORTRADAR_API_KEY", "").strip()

if not API_KEY:
    print("ERROR: API key is missing from the .env file.")
    raise SystemExit

# Doubles competitor rankings endpoint
url = (
    "https://api.sportradar.com/tennis/trial/v3/en/"
    "double_competitors_rankings.json"
)

try:
    response = requests.get(
        url,
        headers={"x-api-key": API_KEY},
        timeout=30
    )
    response.raise_for_status()
    data = response.json()

    # Save JSON data
    output_dir = PROJECT_DIR / "data" / "raw"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "rankings.json"

    with output_file.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

    # Count ranking groups and competitors
    ranking_groups = data.get("rankings", [])
    total_competitors = sum(
        len(group.get("competitor_rankings", []))
        for group in ranking_groups
    )

    print("Doubles rankings downloaded successfully!")
    print("Number of ranking groups:", len(ranking_groups))
    print("Total competitor ranking entries:", total_competitors)
    print("Saved file:", output_file)

except requests.exceptions.HTTPError as error:
    print("API HTTP error:", error)
    print("Response details:", response.text[:500])

except (requests.exceptions.RequestException, ValueError) as error:
    print("Error:", error)
