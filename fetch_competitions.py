
import os
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

# Find the project folder and load its .env file
PROJECT_DIR = Path(__file__).resolve().parent
load_dotenv(PROJECT_DIR / ".env", override=True)

API_KEY = os.getenv("SPORTRADAR_API_KEY", "").strip()

if not API_KEY:
    print("ERROR: API key is missing from the .env file.")
    raise SystemExit
else:
    url = "https://api.sportradar.com/tennis/trial/v3/en/competitions.json"

    try:
        response = requests.get(
            url,
            headers={"x-api-key": API_KEY},
            timeout=30
        )
        response.raise_for_status()

        data = response.json()

        # Create data/raw if it does not exist
        output_dir = PROJECT_DIR / "data" / "raw"
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save the response as a JSON file
        output_file = output_dir / "competitions.json"
        with output_file.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

        print("Competitions downloaded successfully!")
        print("Number of competitions:", len(data.get("competitions", [])))
        print("Saved file:", output_file)

    except requests.exceptions.HTTPError as error:
        print("API HTTP error:", error)
        print("Response details:", response.text[:500])

    except (requests.exceptions.RequestException, ValueError) as error:
        print("Error:", error)
