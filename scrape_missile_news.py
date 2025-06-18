import json
import time
from datetime import datetime
from typing import List, Dict

import requests
from bs4 import BeautifulSoup

DATA_PATH = "missile_hits.json"
NEWS_URL = "https://example.com/israel-missile-hits"  # Placeholder URL


def fetch_latest_hits() -> List[Dict[str, str]]:
    """Fetch latest missile hit reports from the news site."""
    try:
        response = requests.get(NEWS_URL, timeout=10)
    except requests.RequestException as exc:
        print(f"Request failed: {exc}")
        return []

    if response.status_code != 200:
        print("Failed to fetch news page", response.status_code)
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    hits = []

    # This selector structure is hypothetical and should be adapted
    # to the actual news page layout.
    for item in soup.select(".hit-entry"):
        location = item.select_one(".location").get_text(strip=True)
        dt_str = item.select_one(".datetime").get_text(strip=True)
        try:
            # Example format: '23 May 2024 14:35'
            dt = datetime.strptime(dt_str, "%d %B %Y %H:%M")
        except ValueError:
            continue
        lat, lon = geocode_location(location)
        hits.append({
            "location": location,
            "lat": lat,
            "lon": lon,
            "datetime": dt.isoformat()
        })
    return hits


def geocode_location(location: str) -> (float, float):
    """Convert a location string to latitude and longitude."""
    # Real implementation would query a geocoding API.
    # Placeholder returns (0.0, 0.0) to keep offline compatibility.
    return 0.0, 0.0


def update_dataset(new_hits: List[Dict[str, str]], path: str = DATA_PATH) -> None:
    """Append new hit reports to the dataset, avoiding duplicates."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = []

    for hit in new_hits:
        duplicate = any(h["location"] == hit["location"] and h["datetime"] == hit["datetime"] for h in data)
        if not duplicate:
            data.append(hit)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def run_scraper():
    hits = fetch_latest_hits()
    if hits:
        update_dataset(hits)
        print(f"Added {len(hits)} new hits")
    else:
        print("No new hits found")


if __name__ == "__main__":
    import schedule

    schedule.every(12).hours.do(run_scraper)
    while True:
        schedule.run_pending()
        time.sleep(60)
