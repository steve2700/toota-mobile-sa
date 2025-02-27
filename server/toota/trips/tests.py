import json
import uuid
from unittest.mock import patch
import pytest
from django.test import Client
from rest_framework.test import APIClient
from channels.testing import WebsocketCommunicator
from channels.db import database_sync_to_async
from authentication.models import User, Driver
from trips.models import Trip
from trips.consumers import (
    DriverLocationConsumer,
    PassengerGetLocationConsumer,
    TripRequestConsumer,
    DriverTripConsumer,
)
from trips.views import FindDriversView, UpdateTripStatusView, CalculateFareView

pytestmark = pytest.mark.django_db

# Helper functions
def create_user(email="testuser@example.com", password="testpass123"):
    return User.objects.create_user(email=email, password=password)

def create_driver(user=None, latitude=123.456, longitude=789.012, vehicle_type="Bakkie"):
    if not user:
        user = create_user()
    return Driver.objects.create(
        user=user, id=f"driver-{uuid.uuid4()}", latitude=latitude, longitude=longitude, 
        vehicle_type=vehicle_type, is_available=True
    )

# WebSocket Tests
@pytest.mark.asyncio
async def test_driver_location_consumer_connect():
    user = create_user()
    driver = create_driver(user=user)
    communicator = WebsocketCommunicator(
        DriverLocationConsumer.as_asgi(), f"/ws/trips/driver/location/{driver.id}/"
    )
    communicator.scope["user"] = user
    connected, _ = await communicator.connect()
    assert connected
    await communicator.disconnect()

@pytest.mark.asyncio
async def test_driver_location_consumer_unauthenticated():
    communicator = WebsocketCommunicator(
        DriverLocationConsumer.as_asgi(), "/ws/trips/driver/location/driver-123/"
    )
    communicator.scope["user"] = None
    connected, _ = await communicator.connect()
    assert not connected

@pytest.mark.asyncio
async def test_driver_location_consumer_receive():
    user = create_user()
    driver = create_driver(user=user)
    communicator = WebsocketCommunicator(
        DriverLocationConsumer.as_asgi(), f"/ws/trips/driver/location/{driver.id}/"
    )
    communicator.scope["user"] = user
    await communicator.connect()
    await communicator.send_json_to({"latitude": 123.457, "longitude": 789.013})
    response = await communicator.receive_json_from()
    assert response["latitude"] == 123.457
    assert response["longitude"] == 789.013
    await communicator.disconnect()

@pytest.mark.asyncio
async def test_passenger_get_location_consumer_connect():
    user = create_user()
    driver = create_driver()
    communicator = WebsocketCommunicator(
        PassengerGetLocationConsumer.as_asgi(), f"/ws/trips/user/location/{driver.id}/"
    )
    communicator.scope["user"] = user
    connected, _ = await communicator.connect()
    assert connected
    await communicator.disconnect()

@pytest.mark.asyncio
async def test_trip_request_consumer_create_trip():
    user = create_user()
    driver = create_driver()
    communicator = WebsocketCommunicator(
        TripRequestConsumer.as_asgi(), f"/ws/trips/user/request/{driver.id}/"
    )
    communicator.scope["user"] = user
    communicator.scope["user"].id = user.id
    await communicator.connect()

    trip_data = {
        "action": "create_trip",
        "vehicle_type": "Bakkie",
        "pickup": "Test Pickup",
        "destination": "Test Destination",
        "pickup_lat": 123.456,
        "pickup_lon": 789.012,
        "dest_lat": 124.456,
        "dest_lon": 790.012,
        "surge": False,
        "load_description": "Fragile electronics"
    }
    with patch("trips.consumers.get_route_data", return_value={"distance_km": 10.0, "duration_min": 20.0}):
        await communicator.send_json_to(trip_data)
        response = await communicator.receive_json_from()
        assert response["message"] == "Trip created successfully"
        assert response["estimated_fare"] == 220.0  # 80 + 10*10 + 20*2
        assert response["load_description"] == "Fragile electronics"
        assert "user_info" in response
    await communicator.disconnect()

@pytest.mark.asyncio
async def test_driver_trip_consumer_accept_trip():
    user = create_user()
    driver = create_driver(user=user)
    trip = Trip.objects.create(
        user=user, pickup="Test Pickup", destination="Test Destination", 
        vehicle_type="Bakkie", load_description="Test Load"
    )
    communicator = WebsocketCommunicator(
        DriverTripConsumer.as_asgi(), f"/ws/trips/driver/response/{driver.id}/"
    )
    communicator.scope["user"] = user
    await communicator.connect()

    driver_response = {
        "user_id": str(user.id),
        "trip_id": str(trip.id),
        "trip_response_status": "accepted"
    }
    await communicator.send_json_to(driver_response)
    response = await communicator.receive_json_from()
    assert response["type"] == "trip_accepted_confirmation"
    assert response["trip_id"] == str(trip.id)
    
    # Check trip update
    updated_trip = await database_sync_to_async(Trip.objects.get)(id=trip.id)
    assert updated_trip.status == "accepted"
    assert updated_trip.driver == driver
    await communicator.disconnect()

@pytest.mark.asyncio
async def test_driver_trip_consumer_reject_trip():
    user = create_user()
    driver = create_driver(user=user)
    trip = Trip.objects.create(
        user=user, pickup="Test Pickup", destination="Test Destination", vehicle_type="Bakkie"
    )
    communicator = WebsocketCommunicator(
        DriverTripConsumer.as_asgi(), f"/ws/trips/driver/response/{driver.id}/"
    )
    communicator.scope["user"] = user
    await communicator.connect()

    driver_response = {
        "user_id": str(user.id),
        "trip_id": str(trip.id),
        "trip_response_status": "rejected"
    }
    await communicator.send_json_to(driver_response)
    response = await communicator.receive_json_from()
    assert response["status"] == "rejected"
    assert response["trip_id"] == str(trip.id)
    await communicator.disconnect()

# HTTP Endpoint Tests
@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def authenticated_client(api_client):
    user = create_user()
    api_client.force_authenticate(user=user)
    return api_client

def test_find_drivers_view(authenticated_client):
    driver = create_driver()
    data = {"pickup_lat": "123.456", "pickup_lon": "789.012", "vehicle_type": ["Bakkie"]}
    response = authenticated_client.post("/find-driver/", data, format="json")
    assert response.status_code == 200
    assert "drivers" in response.data

def test_update_trip_status_view(authenticated_client):
    user = create_user()
    driver = create_driver(user=user)
    trip = Trip.objects.create(
        user=user, driver=driver, pickup="Pickup", destination="Destination", vehicle_type="Bakkie"
    )
    data = {"trip_id": str(trip.id), "status": "picked up"}
    response = authenticated_client.post(f"/{trip.id}/status/", data, format="json")
    assert response.status_code == 200
    trip.refresh_from_db()
    assert trip.status == "picked up"

def test_calculate_fare_view(authenticated_client):
    data = {
        "pickup_lat": 123.456,
        "pickup_lon": 789.012,
        "dest_lat": 124.456,
        "dest_lon": 790.012,
        "vehicle_type": ["Bakkie"],
        "surge": False,
    }
    with patch("trips.views.get_route_data", return_value={"distance_km": 10.0, "duration_min": 20.0}):
        response = authenticated_client.post("/calculate-fare/", data, format="json")
        assert response.status_code == 200
        assert response.data["estimated_fare"] == 220.0
