from authentication.models import Driver
from geopy.distance import geodesic  # For calculating distances
import base64
import json
from Crypto.Cipher import AES
from django.conf import settings
from dotenv import load_dotenv
import os, requests
load_dotenv()

def find_nearest_drivers(pickup_lat, pickup_lon, vehicle_type, radius=50, limit=20):
    from .serializers import FindDriversSerializer
    """
    Find a list of available drivers near the given pickup location.
    Uses geopy to calculate real distances.
    """
    available_drivers = Driver.objects.filter(is_available=True, vehicle_type__in=vehicle_type)  # Get available drivers
    drivers_list = []
    pickup_location = (float(pickup_lat), float(pickup_lon))

    for driver in available_drivers:
        driver_location = (driver.latitude, driver.longitude)
        distance = geodesic(pickup_location, driver_location).km  # Calculate distance in KM
        
        if distance <= radius:  # Only include drivers within the radius
            drivers_list.append({
                "driver":FindDriversSerializer(driver).data,
                "distance": round(distance, 2)
            })


    # Sort drivers by nearest distance and limit results
    drivers_list = sorted(drivers_list, key=lambda x: x["distance"])[:limit]
    if not drivers_list:
        return available_drivers
    
    return drivers_list


def encrypt_card_details(card_details):
    """Encrypts card details using AES encryption required by Flutterwave"""
    key = os.getenv("FLUTTERWAVE_ENCRYPTION_KEY")
    key_bytes = base64.b64decode(key)
    
    # Convert card details to JSON and encode
    data_string = json.dumps(card_details)
    block_size = AES.block_size
    padding = block_size - (len(data_string) % block_size)
    data_string += chr(padding) * padding
    
    # Encrypt using AES
    cipher = AES.new(key_bytes, AES.MODE_ECB)
    encrypted_bytes = cipher.encrypt(data_string.encode("utf-8"))
    
    # Encode the encrypted data in base64
    encrypted_data = base64.b64encode(encrypted_bytes).decode("utf-8")
    
    return encrypted_data


def get_route_data(pickup_lat, pickup_lon, dest_lat, dest_lon):
    """
    Call OSRM's public API to calculate route data between two coordinates.
    Returns a dict with 'distance_km' (rounded to 2 decimals) and 'duration' (formatted as 'X min' or 'X sec').
    """
    url = f"http://router.project-osrm.org/route/v1/driving/{pickup_lon},{pickup_lat};{dest_lon},{dest_lat}?overview=false"

    try:
        response = requests.get(url)
        data = response.json()

        if data.get("code") == "Ok" and "routes" in data and len(data["routes"]) > 0:
            route = data["routes"][0]

            distance_km = round(float(route["distance"]) / 1000.0, 2)  # Rounded to 2 decimals
            duration_sec = float(route["duration"])  # Convert duration to seconds
            
            # Format duration to be human-readable
            if duration_sec < 60:
                duration_str = f"{int(duration_sec)} sec"
            elif duration_sec < 3600:
                duration_str = f"{int(duration_sec // 60)} min"
            else:
                hours = int(duration_sec // 3600)
                minutes = int((duration_sec % 3600) // 60)
                seconds = int(duration_sec % 60)
                duration_str = f"{hours} hour{'s' if hours > 1 else ''} {minutes} min"
                if seconds > 0:
                    duration_str += f" {seconds} sec"

            return {"distance_km": distance_km, "duration": duration_str}

    except Exception as e:
        print(f"Error calling OSRM API: {e}")

    return {"distance_km": 0.0, "duration": "0 min"}