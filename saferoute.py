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

# Example test
if __name__ == "__main__":
    result = assess_risk("Tel Aviv", "Mitzpe Ramon", "2025-06-18 10:00")
    print("Risk Assessment:")
    print(result)
