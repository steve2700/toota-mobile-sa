from authentication.models import Driver
import decimal
import datetime
from dotenv import load_dotenv
import requests
load_dotenv()
import aiohttp
import asyncio
import logging

logger = logging.getLogger(__name__)


def find_nearest_drivers(pickup_lat, pickup_lon, vehicle_type, limit=20):
    """
    Find the nearest available drivers to the given pickup location.
    Returns a list of serialized driver data.
    """
    from .serializers import FindDriversSerializer
    from geopy.distance import geodesic

    if not vehicle_type:
        available_drivers = Driver.objects.filter(is_available=True)
    else:
        available_drivers = Driver.objects.filter(is_available=True, vehicle_type__in=vehicle_type)

    pickup_location = (float(pickup_lat), float(pickup_lon))

    drivers_with_distance = []
    for driver in available_drivers:
        driver_location = (driver.latitude, driver.longitude)
        distance = geodesic(pickup_location, driver_location).km
        drivers_with_distance.append((driver, distance))

    # Sort by distance and limit the results
    sorted_drivers = sorted(drivers_with_distance, key=lambda x: x[1])[:limit]

    # Return only serialized driver data (no distance)
    return [FindDriversSerializer(driver).data for driver, _ in sorted_drivers]

async def get_route_data(pickup_lat, pickup_lon, dest_lat, dest_lon):
    """
    Call OSRM's public API to calculate route data between two coordinates using aiohttp.
    Returns a dict with 'distance_km' (rounded to 2 decimals) and 'duration' (formatted as 'X min' or 'X sec').
    """
    url = f"http://router.project-osrm.org/route/v1/driving/{pickup_lon},{pickup_lat};{dest_lon},{dest_lat}?overview=false"

    try:
        # Use aiohttp instead of requests for async HTTP requests
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=5) as response:  # 5-second timeout
                data = await response.json()

                if data.get("code") == "Ok" and "routes" in data and len(data["routes"]) > 0:
                    route = data["routes"][0]

                    distance_km = round(float(route["distance"]) / 1000.0, 2)
                    duration_sec = float(route["duration"])
                    
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

                    return {"distance": distance_km, "duration": duration_str}

    except (aiohttp.ClientError, asyncio.TimeoutError) as e:
        logger.error(f"Error calling OSRM API: {e}")
    except Exception as e:
        logger.error(f"Unexpected error calling OSRM API: {e}")

def calculate_easter(year):
    """
    Calculate Easter for the given year (Gregorian calendar)
    using the Anonymous Gregorian algorithm.
    Returns a datetime.date object.
    """
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31  # Month: 3=March, 4=April
    day = ((h + l - 7 * m + 114) % 31) + 1
    return datetime.date(year, month, day)

def is_peak_hour_or_festive(dt):
    """
    Check if the given datetime (dt) is during peak hours
    (6 PM to 6 AM) or falls on a festive day (New Year, Christmas, or Easter).
    
    Returns True if any condition is met, otherwise False.
    """
    # Check fixed-date festive days: New Year's Day and Christmas.
    fixed_holidays = [
        (1, 1),    # New Year's Day
        (12, 25)   # Christmas Day
    ]
    if (dt.month, dt.day) in fixed_holidays:
        return True

    # Check if it's Easter.
    easter_date = calculate_easter(dt.year)
    if dt.date() == easter_date:
        return True

    # Check for peak hours: from 6 PM (18:00) to 9 AM (09:00).
    if dt.hour >= 18 or dt.hour <= 9:
        return True

    return False


def convert_decimals(obj):
    if isinstance(obj, list):
        return [convert_decimals(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: convert_decimals(value) for key, value in obj.items()}
    elif isinstance(obj, decimal.Decimal):
        return float(obj)
    return obj
