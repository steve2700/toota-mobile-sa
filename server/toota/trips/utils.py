import requests
from decimal import Decimal
from .models import Vehicle

def get_distance_from_google(pickup, dropoff):
    """
    Calculate distance between two locations using Google Maps Distance Matrix API.
    """
    GOOGLE_API_KEY = 'YOUR_GOOGLE_API_KEY'
    url = f'https://maps.googleapis.com/maps/api/distancematrix/json?origins={pickup}&destinations={dropoff}&key={GOOGLE_API_KEY}'
    response = requests.get(url).json()

    try:
        distance_meters = response['rows'][0]['elements'][0]['distance']['value']
        return Decimal(distance_meters) / 1000  # Convert meters to kilometers
    except (KeyError, IndexError):
        return None

def calculate_fare(distance_km, vehicle_type):
    """
    Calculate the suggested fare based on distance and vehicle type.
    """
    try:
        vehicle = Vehicle.objects.get(vehicle_type=vehicle_type)
        return round(vehicle.base_rate_per_km * Decimal(distance_km), 2)
    except Vehicle.DoesNotExist:
        raise ValueError("Invalid vehicle type provided")

def suggest_trip_fare(pickup, dropoff, vehicle_type):
    """
    Suggest a fare for a trip based on pickup, dropoff, and vehicle type.
    """
    distance_km = get_distance_from_google(pickup, dropoff)
    if distance_km is None:
        raise ValueError("Unable to calculate distance. Please check the provided locations.")

    suggested_fare = calculate_fare(distance_km, vehicle_type)
    return {
        "distance_km": distance_km,
        "suggested_fare": suggested_fare
    }

