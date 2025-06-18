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
import requests
import os

ORS_API_KEY = os.getenv("ORS_API_KEY")

from math import radians, sin, cos, sqrt, atan2

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculates distance in meters between two lat/lon points.
    """
    R = 6371000  # Earth radius in meters
    phi1 = radians(lat1)
    phi2 = radians(lat2)
    d_phi = radians(lat2 - lat1)
    d_lambda = radians(lon2 - lon1)

    a = sin(d_phi/2)**2 + cos(phi1) * cos(phi2) * sin(d_lambda/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

def load_shelters(path="shelters.json"):
    with open(path, "r") as f:
        return json.load(f)
import json
import requests
from math import radians, sin, cos, sqrt, atan2

def haversine_distance(lat1, lon1, lat2, lon2):
    ...

def load_shelters(path="shelters.json"):
    ...

def count_exposed_segments(route, shelters, threshold_meters=1000):
    """
    Counts how many route points are farther than `threshold_meters` from the nearest shelter.
    """
    exposed = 0
    for point in route:
        lon, lat = point
        min_distance = float("inf")
        for shelter in shelters:
            dist = haversine_distance(lat, lon, shelter["lat"], shelter["lon"])
            if dist < min_distance:
                min_distance = dist
        if min_distance > threshold_meters:
            exposed += 1
    return exposed

def fetch_route(start_coords, end_coords):
    ...
    
def assess_risk(start_location, end_location, travel_time):
    ...

def assess_risk(start_location, end_location, travel_time):
    """
    Core function for route risk assessment.
    For now, this is a placeholder that returns mock risk levels.
    """
    print(f"Starting location: {start_location}")
    print(f"Destination: {end_location}")
    print(f"Travel time: {travel_time}")

    # TODO: Add route lookup
    # TODO: Add shelter proximity logic
    # TODO: Add risk scoring

    return {
        "risk_level": "MODERATE",
        "details": "Between Be'er Sheva and Mitzpe Ramon, there is a 40km stretch with no shelter access."
    }
def fetch_route(start_coords, end_coords):
    """
    Fetch driving route from OpenRouteService.
    Input: [lon, lat] for start and end
    Returns: list of [lon, lat] coordinates along the route
    """
    url = "https://api.openrouteservice.org/v2/directions/driving-car"
    headers = {
        "Authorization": ORS_API_KEY,
        "Content-Type": "application/json"
    }
    body = {
        "coordinates": [start_coords, end_coords]
    }

    response = requests.post(url, json=body, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data["features"][0]["geometry"]["coordinates"]
    else:
        print("Route fetch failed:", response.status_code, response.text)
        return []

# Example test
if __name__ == "__main__":
    # Test route from Tel Aviv to Mitzpe Ramon
    route = fetch_route([34.7818, 32.0853], [34.8016, 30.6072])
    print(f"Route contains {len(route)} segments.")

    result = assess_risk("Tel Aviv", "Mitzpe Ramon", "2025-06-18 10:00")
    print("Risk Assessment:")
    print(result)
