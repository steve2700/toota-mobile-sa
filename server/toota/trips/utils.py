from authentication.models import Driver
from geopy.distance import geodesic  # For calculating distances
import base64
import json
from Crypto.Cipher import AES
from django.conf import settings
from dotenv import load_dotenv
import os
load_dotenv()

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
