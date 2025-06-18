# SafeRoute AI - MVP Travel Risk Agent
# Author: Yoav A.
# Version: 0.1

"""
This script will:
1. Accept origin, destination, and travel time
2. Use a routing service to calculate the route
3. Analyze exposure to risk (e.g., distance from bomb shelters)
4. Return a natural-language safety summary
"""

import os
import json
from datetime import datetime
from math import radians, sin, cos, sqrt, atan2

import requests

ORS_API_KEY = os.getenv("ORS_API_KEY")


def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculates distance in meters between two lat/lon points."""
    R = 6371000  # Earth radius in meters
    phi1 = radians(lat1)
    phi2 = radians(lat2)
    d_phi = radians(lat2 - lat1)
    d_lambda = radians(lon2 - lon1)

    a = sin(d_phi / 2) ** 2 + cos(phi1) * cos(phi2) * sin(d_lambda / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c


def load_shelters(path="shelters.json"):
    """Load shelter locations from a JSON file."""
    with open(path, "r") as f:
        return json.load(f)


def load_missile_hits(path="missile_hits.json"):
    """Load recorded missile hit locations."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def count_recent_hits(route, hits, threshold_meters=5000, days=30):
    """Count hits within `threshold_meters` of the route in the last `days`."""
    now = datetime.utcnow()
    recent_hits = [h for h in hits if (now - datetime.fromisoformat(h["datetime"])).days <= days]
    count = 0
    for hit in recent_hits:
        for lon, lat in route:
            dist = haversine_distance(lat, lon, hit["lat"], hit["lon"])
            if dist <= threshold_meters:
                count += 1
                break
    return count


def count_exposed_segments(route, shelters, threshold_meters=1000):
    """Counts how many route points are farther than `threshold_meters` from the nearest shelter."""
    exposed = 0
    for lon, lat in route:
        min_distance = float("inf")
        for shelter in shelters:
            dist = haversine_distance(lat, lon, shelter["lat"], shelter["lon"])
            if dist < min_distance:
                min_distance = dist
        if min_distance > threshold_meters:
            exposed += 1
    return exposed


def fetch_route(start_coords, end_coords):
    """Fetch driving route from OpenRouteService."""
    url = "https://api.openrouteservice.org/v2/directions/driving-car"
    headers = {
        "Authorization": ORS_API_KEY,
        "Content-Type": "application/json",
    }
    body = {"coordinates": [start_coords, end_coords]}

    response = requests.post(url, json=body, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data["features"][0]["geometry"]["coordinates"]
    else:
        print("Route fetch failed:", response.status_code, response.text)
        return []


def assess_risk(start_coords, end_coords, travel_time):
    """Assess risk along a route between two coordinate pairs."""
    route = fetch_route(start_coords, end_coords)
    shelters = load_shelters()
    hits = load_missile_hits()

    exposed = count_exposed_segments(route, shelters)
    nearby_hits = count_recent_hits(route, hits)

    if exposed > 20 or nearby_hits > 5:
        risk = "HIGH"
    elif exposed > 10 or nearby_hits > 0:
        risk = "MODERATE"
    else:
        risk = "LOW"

    return {
        "risk_level": risk,
        "exposed_segments": exposed,
        "nearby_hits": nearby_hits,
    }


if __name__ == "__main__":
    # Test route from Tel Aviv to Mitzpe Ramon
    route = fetch_route([34.7818, 32.0853], [34.8016, 30.6072])
    print(f"Route contains {len(route)} segments.")

    result = assess_risk([34.7818, 32.0853], [34.8016, 30.6072], "2025-06-18 10:00")
    print("Risk Assessment:")
    print(result)
