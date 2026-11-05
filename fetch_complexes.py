
import os
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

# Find the project folder
PROJECT_DIR = Path(__file__).resolve().parent

# Load the API key from .env
load_dotenv(PROJECT_DIR / ".env", override=True)
API_KEY = os.getenv("SPORTRADAR_API_KEY", "").strip()

if not API_KEY:
    print("ERROR: API key is missing from the .env file.")
    raise SystemExit

# SportRadar complexes endpoint
url = "https://api.sportradar.com/tennis/trial/v3/en/complexes.json"

try:
    response = requests.get(
        url,
        headers={"x-api-key": API_KEY},
        timeout=30
    )

    response.raise_for_status()
    data = response.json()

    # Create the output folder
    output_dir = PROJECT_DIR / "data" / "raw"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save the downloaded JSON
    output_file = output_dir / "complexes.json"

    with output_file.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

    print("Complexes data downloaded successfully!")
    print("Number of complexes:", len(data.get("complexes", [])))
    print("Number of venues:", sum(
        len(complex_item.get("venues", []))
        for complex_item in data.get("complexes", [])
    ))
    print("Saved file:", output_file)

except requests.exceptions.HTTPError as error:
    print("API HTTP error:", error)
    print("Response details:", response.text[:500])

except (requests.exceptions.RequestException, ValueError) as error:
    print("Error:", error)
