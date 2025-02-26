from authentication.models import Driver
from geopy.distance import geodesic  # For calculating distances
import requests


def find_nearest_drivers(pickup_lat, pickup_lon, vehicle_type, radius=50, limit=20):
    from .serializers import FindDriversSerializer
    """
    Find a list of available drivers near the given pickup location.
    Uses geopy to calculate real distances.
    """
    available_drivers = Driver.objects.filter(is_available=True, vehicle_type__in=vehicle_type)
    drivers_list = []
    pickup_location = (float(pickup_lat), float(pickup_lon))

    for driver in available_drivers:
        driver_location = (driver.latitude, driver.longitude)
        distance = geodesic(pickup_location, driver_location).km  # Calculate distance in KM

        if distance <= radius:  # Only include drivers within the radius
            drivers_list.append({
                "driver": FindDriversSerializer(driver).data,
                "distance": round(distance, 2)
            })

    # Sort drivers by nearest distance and limit results
    drivers_list = sorted(drivers_list, key=lambda x: x["distance"])[:limit]
    if not drivers_list:
        return available_drivers

    return drivers_list


def get_route_data(pickup_lat, pickup_lon, dest_lat, dest_lon):
    """
    Call OSRM's public API to calculate route data between two coordinates.
    Returns a dict with 'distance_km' (rounded to 2 decimals) and 'duration' (in minutes or seconds).
    """
    url = f"http://router.project-osrm.org/route/v1/driving/{pickup_lon},{pickup_lat};{dest_lon},{dest_lat}?overview=false"
    try:
        response = requests.get(url)
        data = response.json()
        if data.get("code") == "Ok":
            route = data["routes"][0]
            distance_km = float(route["distance"]) / 1000.0 #round to 2 decimal place
            duration_min = float(route["duration"]) / 60.0  
                                                      

            # Convert duration to minutes, but keep short trips in seconds
            if duration_sec < 60:
                duration_str = f"{int(duration_sec)} sec"
            else:
                duration_str = f"{round(duration_sec / 60)} min"

            return {"distance_km": distance_km, "duration": duration_str}
    except Exception as e:
        print(f"Error calling OSRM API: {e}")

    return {"distance_km": 0.0, "duration": "0 min"}

