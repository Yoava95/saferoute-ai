import json
import re
from datetime import datetime
from typing import List, Dict

import requests
from bs4 import BeautifulSoup

DATA_PATH = "missile_hits.json"
FEED_URL = "https://rocketalert.live/alerts.json"
HOME_URL = "https://rocketalert.live/"


def geocode_location(location: str) -> (float, float):
    """Convert a location string to latitude and longitude."""
    # Real implementation would query a geocoding API.
    # Placeholder returns (0.0, 0.0) to keep offline compatibility.
    return 0.0, 0.0


def _normalize_alerts(data: List[Dict]) -> List[Dict[str, str]]:
    """Normalize alert records into a consistent structure."""
    alerts = []
    for item in data:
        location = item.get("location") or item.get("name")
        time_str = item.get("time") or item.get("date")
        alert_type = item.get("type", "alert")
        if not location or not time_str:
            continue
        dt = None
        for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"):
            try:
                dt = datetime.strptime(time_str, fmt)
                break
            except ValueError:
                continue
        if not dt:
            try:
                dt = datetime.fromisoformat(time_str)
            except ValueError:
                continue
        lat, lon = geocode_location(location)
        alerts.append({
            "location": location,
            "lat": lat,
            "lon": lon,
            "datetime": dt.isoformat(),
            "type": alert_type,
        })
    return alerts


def fetch_latest_alerts() -> List[Dict[str, str]]:
    """Fetch latest alerts from rocketalert.live."""
    try:
        response = requests.get(FEED_URL, timeout=10)
        if response.status_code == 200:
            try:
                data = response.json()
                if isinstance(data, list):
                    return _normalize_alerts(data)
            except ValueError:
                pass
    except requests.RequestException as exc:
        print(f"JSON feed request failed: {exc}")

    # Fallback to scraping the homepage for embedded alert data
    try:
        response = requests.get(HOME_URL, timeout=10)
    except requests.RequestException as exc:
        print(f"Homepage request failed: {exc}")
        return []
    if response.status_code != 200:
        print(f"Failed to fetch home page {response.status_code}")
        return []
    soup = BeautifulSoup(response.text, "html.parser")
    for script in soup.find_all("script"):
        if "alertData" in script.text:
            match = re.search(r"alertData\s*=\s*(\[.*?\])\s*;", script.text, re.S)
            if match:
                try:
                    data = json.loads(match.group(1))
                    return _normalize_alerts(data)
                except ValueError:
                    pass
    return []


def update_dataset(new_hits: List[Dict[str, str]], path: str = DATA_PATH) -> None:
    """Append new alert reports to the dataset, avoiding duplicates."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = []

    for hit in new_hits:
        duplicate = any(
            h.get("location") == hit.get("location") and h.get("datetime") == hit.get("datetime")
            for h in data
        )
        if not duplicate:
            data.append(hit)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def run_scraper():
    alerts = fetch_latest_alerts()
    if alerts:
        update_dataset(alerts)
        print(f"Added {len(alerts)} new alerts")
    else:
        print("No new alerts found")


if __name__ == "__main__":
    import schedule
    import time

    schedule.every(12).hours.do(run_scraper)
    while True:
        schedule.run_pending()
        time.sleep(60)
