from authentication.models import Driver
from geopy.distance import geodesic  # For calculating distances

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
