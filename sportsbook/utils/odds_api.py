import requests
import os

API_KEY = os.getenv("ODDS_API_KEY")
BASE_URL = "https://api.the-odds-api.com/v4/sports"

def get_sports():
    res = requests.get(f"{BASE_URL}", params={"apiKey": API_KEY})
    return res.json()

def get_odds(sport_key, region="us", market="h2h", odds_format="decimal"):
    if not API_KEY:
        raise EnvironmentError("⚠️ ODDS_API_KEY not set in environment variables.")

    print(f"⚙️ Fetching odds for {sport_key}...")

    url = f"{BASE_URL}/{sport_key}/odds"
    params = {
        "apiKey": API_KEY,
        "regions": region,
        "markets": market,
        "oddsFormat": odds_format
    }

    try:
        res = requests.get(url, params=params)
        res.raise_for_status()  # will raise for 4XX or 5XX
        return res.json()
    except requests.RequestException as e:
        print("❌ Error fetching odds:", e)
        return []















