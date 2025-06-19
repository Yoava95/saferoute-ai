import json
import re
from datetime import datetime
from typing import List, Dict, Tuple

import requests
from bs4 import BeautifulSoup

DATA_PATH = "missile_hits.json"
FEED_URL = "https://rocketalert.live/alerts.json"
HOME_URL = "https://rocketalert.live/"
HISTORY_START_DATE = datetime(2024, 6, 12)


def geocode_location(location: str) -> Tuple[float, float]:
    """Convert a location string to latitude and longitude (placeholder)."""
    # A real implementation would query a geocoding API.
    return 0.0, 0.0


def _parse_datetime(value: str) -> datetime | None:
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"):  # common formats
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def _normalize_alerts(data: List[Dict]) -> List[Dict[str, str]]:
    """Normalize raw alert records from the feed or page."""
    alerts = []
    for item in data:
        location = item.get("location") or item.get("name")
        time_str = item.get("time") or item.get("date")
        alert_type = item.get("type", "alert")
        lat = item.get("lat") or item.get("latitude")
        lon = item.get("lon") or item.get("longitude")
        if not location or not time_str:
            continue
        dt = _parse_datetime(time_str)
        if not dt:
            continue
        if lat is None or lon is None:
            lat, lon = geocode_location(location)
        alerts.append(
            {
                "location": location,
                "lat": float(lat),
                "lon": float(lon),
                "datetime": dt.isoformat(),
                "type": alert_type,
            }
        )
    return alerts


def _fetch_from_json() -> List[Dict[str, str]]:
    try:
        response = requests.get(FEED_URL, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                return _normalize_alerts(data)
    except requests.RequestException:
        pass
    except ValueError:
        pass
    return []


def _fetch_from_html() -> List[Dict[str, str]]:
    try:
        response = requests.get(HOME_URL, timeout=10)
    except requests.RequestException:
        return []
    if response.status_code != 200:
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
                    return []
    return []


def fetch_alerts() -> List[Dict[str, str]]:
    alerts = _fetch_from_json()
    if alerts:
        return alerts
    return _fetch_from_html()


def load_dataset(path: str = DATA_PATH) -> List[Dict[str, str]]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def save_dataset(data: List[Dict[str, str]], path: str = DATA_PATH) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def newest_datetime(data: List[Dict[str, str]]) -> datetime:
    if not data:
        return HISTORY_START_DATE
    return max(datetime.fromisoformat(d["datetime"]) for d in data)


def update_dataset() -> None:
    existing = load_dataset()
    since = newest_datetime(existing)
    alerts = [a for a in fetch_alerts() if datetime.fromisoformat(a["datetime"]) >= since]
    new_records = []
    for alert in alerts:
        duplicate = any(
            alert["location"] == e.get("location") and alert["datetime"] == e.get("datetime")
            for e in existing
        )
        if not duplicate:
            existing.append(alert)
            new_records.append(alert)
    if new_records:
        save_dataset(existing)
    print(f"Added {len(new_records)} new alerts")


def run_scraper() -> None:
    update_dataset()


if __name__ == "__main__":
    import schedule
    import time

    run_scraper()
    schedule.every().day.do(run_scraper)
    while True:
        schedule.run_pending()
        time.sleep(60)
