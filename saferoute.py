"""SafeRoute AI - MVP Travel Risk Agent.
This script provides simple routing risk assessment using open-source
APIs. It fetches a driving route, evaluates how much of the route is far
from bomb shelters, and returns a basic risk score.
"""

import json
from math import atan2, cos, radians, sin, sqrt
from typing import Iterable, List, Sequence, Union

import requests

# Replace with your actual OpenRouteService API key if available
ORS_API_KEY = "YOUR_API_KEY"


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Return distance in meters between two lat/lon coordinates."""
    r = 6371000  # Earth radius in meters
    phi1 = radians(lat1)
    phi2 = radians(lat2)
    d_phi = radians(lat2 - lat1)
    d_lambda = radians(lon2 - lon1)

    a = sin(d_phi / 2) ** 2 + cos(phi1) * cos(phi2) * sin(d_lambda / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return r * c


def load_shelters(path: str = "shelters.json") -> List[dict]:
    """Load shelter metadata from ``path``."""
    with open(path, "r") as fh:
        return json.load(fh)


def count_exposed_segments(
    route: Iterable[Sequence[float]],
    shelters: Iterable[dict],
    threshold_meters: float = 1000,
) -> int:
    """Return number of route points farther than ``threshold_meters`` from a shelter."""
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


def fetch_route(start_coords: Sequence[float], end_coords: Sequence[float]) -> List[List[float]]:
    """Fetch a driving route from OpenRouteService and return ``[lon, lat]`` points."""
    url = "https://api.openrouteservice.org/v2/directions/driving-car"
    headers = {"Authorization": ORS_API_KEY, "Content-Type": "application/json"}
    body = {"coordinates": [start_coords, end_coords]}

    resp = requests.post(url, json=body, headers=headers)
    if resp.status_code == 200:
        data = resp.json()
        return data["features"][0]["geometry"]["coordinates"]
    print("Route fetch failed:", resp.status_code, resp.text)
    return []


def geocode_location(location: str) -> List[float]:
    """Return ``[lon, lat]`` coordinates for a location name using Nominatim."""
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": location, "format": "json", "limit": 1}
    resp = requests.get(url, params=params, headers={"User-Agent": "saferoute-ai"})
    if resp.status_code == 200 and resp.json():
        info = resp.json()[0]
        return [float(info["lon"]), float(info["lat"])]
    raise ValueError(f"Could not geocode location: {location}")


def _coords(loc: Union[str, Sequence[float]]) -> List[float]:
    if isinstance(loc, str):
        return geocode_location(loc)
    if isinstance(loc, (list, tuple)) and len(loc) == 2:
        return [float(loc[0]), float(loc[1])]
    raise TypeError("Location must be a name or coordinate pair")


def assess_risk(
    start_location: Union[str, Sequence[float]],
    end_location: Union[str, Sequence[float]],
    travel_time: str,
    threshold_meters: float = 1000,
) -> dict:
    """Return a basic risk assessment for traveling between two locations."""
    start_coords = _coords(start_location)
    end_coords = _coords(end_location)

    route = fetch_route(start_coords, end_coords)
    shelters = load_shelters()

    if not route:
        return {"risk_level": "UNKNOWN", "details": "Route retrieval failed."}

    exposed = count_exposed_segments(route, shelters, threshold_meters)
    total = len(route)
    ratio = exposed / total if total else 0

    if ratio < 0.2:
        risk = "LOW"
    elif ratio < 0.5:
        risk = "MODERATE"
    else:
        risk = "HIGH"

    details = (
        f"{exposed} of {total} route points are beyond {threshold_meters}m from a shelter "
        f"({ratio:.1%} exposed)."
    )
    return {"risk_level": risk, "details": details}


if __name__ == "__main__":
    route = fetch_route([34.7818, 32.0853], [34.8016, 30.6072])
    print(f"Route contains {len(route)} segments.")

    result = assess_risk("Tel Aviv", "Mitzpe Ramon", "2025-06-18 10:00")
    print("Risk Assessment:")
    print(result)
