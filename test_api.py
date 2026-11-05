
import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("SPORTRADAR_API_KEY")

if not API_KEY:
    raise ValueError("API key not found. Check your .env file.")

url = "https://api.sportradar.com/tennis/trial/v3/en/competitions.json"

response = requests.get(
    url,
    headers={"x-api-key": API_KEY},
    timeout=30
)

response.raise_for_status()

data = response.json()
print("API connection successful!")
print("Number of competitions:", len(data.get("competitions", [])))


