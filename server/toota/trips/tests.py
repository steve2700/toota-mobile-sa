import json
from rest_framework.test import APIClient
from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch, MagicMock
from channels.testing import WebsocketCommunicator
from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async
import json
import uuid
from decimal import Decimal
from rest_framework.test import APIClient
from rest_framework import status

from .models import Trip
from .consumers import (
    DriverLocationConsumer, 
    PassengerGetLocationConsumer,
    TripRequestConsumer,
    DriverTripConsumer
)
from .serializers import TripDescriptionSerializer, UpdateTripStatusSerializer
from authentication.models import User, Driver
from django.contrib.auth import get_user_model


class SouthAfricaTripModelTests(TestCase):
    """Tests for the Trip model using South African locations"""
    
    def setUp(self):
        # Create test user
        self.user = User.objects.create(
            email="user@example.co.za",
            password="testpassword123"
        )
        
        # Create test driver
        self.driver = Driver.objects.create(
            email="driver@example.co.za",
            password="testpassword123",
            vehicle_type="Bakkie",
            is_available=True,
            latitude=-26.2041, # Johannesburg coordinates
            longitude=28.0473
        )
        
        # Create test trip
        self.trip = Trip.objects.create(
            user=self.user,
            pickup="Sandton City, Johannesburg",
            destination="Pretoria Central",
            vehicle_type="Bakkie"
        )
    
    def test_trip_creation(self):
        """Test trip instance creation"""
        self.assertEqual(self.trip.status, Trip.StatusChoices.PENDING)
        self.assertEqual(self.trip.pickup, "Sandton City, Johannesburg")
        self.assertEqual(self.trip.destination, "Pretoria Central")
        self.assertEqual(self.trip.vehicle_type, "Bakkie")
        self.assertEqual(self.trip.user, self.user)
        self.assertIsNone(self.trip.driver)
    
    def test_trip_str_representation(self):
        """Test the string representation of a trip"""
        expected_string = f"Sandton City, Johannesburg to Pretoria Central and status is pending"
        self.assertEqual(str(self.trip), expected_string)
    
    def test_calculate_fare(self):
        """Test the fare calculation functionality with South African distances"""
        # Test regular fare calculation (Sandton to Pretoria is about 50km, ~45min)
        fare = self.trip.calculate_fare(50, 45, surge=False)
        # Base fare for Bakkie (80) + 50km * 10 + 45min * 2
        expected_fare = 80 + 50 * 10 + 45 * 2
        self.assertEqual(fare, expected_fare)
        
        # Test surge fare calculation (weekend/peak hours)
        surge_fare = self.trip.calculate_fare(50, 45, surge=True)
        expected_surge_fare = expected_fare * 1.5
        self.assertEqual(surge_fare, expected_surge_fare)
        
        # Test with different vehicle type
        self.trip.vehicle_type = "1 ton Truck"
        self.trip.save()
        fare = self.trip.calculate_fare(50, 45, surge=False)
        expected_fare = 100 + 50 * 10 + 45 * 2
        self.assertEqual(fare, expected_fare)


class SouthAfricaUtilsTests(TestCase):
    """Tests for the utility functions using South African coordinates"""
    
    def setUp(self):
        # Create test drivers in different South African locations
        self.driver1 = Driver.objects.create(
            email="driver1@example.co.za",
            password="testpassword123",
            vehicle_type="Bakkie",
            is_available=True,
            latitude=-26.2041,  # Johannesburg
            longitude=28.0473
        )
        
        self.driver2 = Driver.objects.create(
            email="driver2@example.co.za",
            password="testpassword123",
            vehicle_type="1 ton Truck",
            is_available=True,
            latitude=-25.7479,  # Pretoria
            longitude=28.2293
        )
        
        self.driver3 = Driver.objects.create(
            email="driver3@example.co.za",
            password="testpassword123",
            vehicle_type="Bakkie",
            is_available=False,  # Not available
            latitude=-26.1052,  # Midrand
            longitude=28.0600
        )
    
    @patch('trips.utils.geodesic')
    def test_find_nearest_drivers(self, mock_geodesic):
        """Test finding nearest available drivers in Johannesburg area"""
        from trips.utils import find_nearest_drivers
        
        # Setup mock distance calculations
        def mock_distance_calculator(point1, point2):
            # Rough distance calculator for South African coordinates
            # Returns MagicMock with appropriate distance based on locations
            
            # Sandton coordinates
            sandton_lat, sandton_lon = -26.1067, 28.0568
            
            if point1[0] == sandton_lat and point1[1] == sandton_lon:
                if point2[0] == self.driver1.latitude and point2[1] == self.driver1.longitude:
                    # Sandton to Johannesburg CBD (about 12km)
                    mock_dist = MagicMock()
                    mock_dist.km = 12.0
                    return mock_dist
                elif point2[0] == self.driver2.latitude and point2[1] == self.driver2.longitude:
                    # Sandton to Pretoria (about 55km)
                    mock_dist = MagicMock()
                    mock_dist.km = 55.0
                    return mock_dist
                elif point2[0] == self.driver3.latitude and point2[1] == self.driver3.longitude:
                    # Sandton to Midrand (about 20km)
                    mock_dist = MagicMock()
                    mock_dist.km = 20.0
                    return mock_dist
            
            # Default distance
            mock_dist = MagicMock()
            mock_dist.km = 10.0
            return mock_dist
        
        mock_geodesic.side_effect = mock_distance_calculator
        
        # Test finding drivers for Sandton with specific vehicle type
        nearest_drivers = find_nearest_drivers(-26.1067, 28.0568, ["Bakkie"], radius=30, limit=5)
        
        # Should find only driver1 (driver3 is not available)
        self.assertEqual(len(nearest_drivers), 1)
        self.assertEqual(nearest_drivers[0]["driver"]["email"], "driver1@example.co.za")
        self.assertEqual(nearest_drivers[0]["distance"], 12.0)
        
        # Test finding with multiple vehicle types and larger radius
        nearest_drivers = find_nearest_drivers(-26.1067, 28.0568, ["Bakkie", "1 ton Truck"], radius=60, limit=5)
        self.assertEqual(len(nearest_drivers), 2)
        # First driver should be closest (Johannesburg)
        self.assertEqual(nearest_drivers[0]["driver"]["email"], "driver1@example.co.za")
        # Second driver should be further (Pretoria)
        self.assertEqual(nearest_drivers[1]["driver"]["email"], "driver2@example.co.za")
    
    @patch('trips.utils.requests.get')
    def test_get_route_data(self, mock_get):
        """Test route data retrieval for South African routes"""
        from trips.utils import get_route_data
        
        # Sandton to Johannesburg CBD route data
        sandton_to_joburg = {
            "code": "Ok",
            "routes": [{
                "distance": 12000,  # 12 km in meters
                "duration": 1200    # 20 minutes in seconds
            }]
        }
        
        # Sandton to Pretoria route data
        sandton_to_pretoria = {
            "code": "Ok",
            "routes": [{
                "distance": 55000,  # 55 km in meters
                "duration": 2700    # 45 minutes in seconds
            }]
        }
        
        # Mock successful OSRM response for Sandton to Johannesburg
        mock_response1 = MagicMock()
        mock_response1.json.return_value = sandton_to_joburg
        
        # Mock successful OSRM response for Sandton to Pretoria
        mock_response2 = MagicMock()
        mock_response2.json.return_value = sandton_to_pretoria
        
        # Setup the mock to return different responses for different coordinates
        def get_mock_response(url):
            if "28.0568" in url and "28.0473" in url:  # Sandton to Johannesburg
                return mock_response1
            elif "28.0568" in url and "28.2293" in url:  # Sandton to Pretoria
                return mock_response2
            else:
                raise Exception("Unexpected URL")
        
        mock_get.side_effect = get_mock_response
        
        # Test Sandton to Johannesburg route
        route_data = get_route_data(-26.1067, 28.0568, -26.2041, 28.0473)
        self.assertEqual(route_data["distance_km"], 12.0)
        self.assertEqual(route_data["duration_min"], 20.0)
        
        # Test Sandton to Pretoria route
        route_data = get_route_data(-26.1067, 28.0568, -25.7479, 28.2293)
        self.assertEqual(route_data["distance_km"], 55.0)
        self.assertEqual(route_data["duration_min"], 45.0)
        
        # Test error handling
        mock_get.side_effect = Exception("API Error")
        route_data = get_route_data(-26.1067, 28.0568, -26.2041, 28.0473)
        
        # Should return defaults if API fails
        self.assertEqual(route_data["distance_km"], 0.0)
        self.assertEqual(route_data["duration_min"], 0.0)


class SouthAfricaSerializerTests(TestCase):
    """Tests for serializers with South African data"""
    
    def test_trip_description_serializer(self):
        """Test TripDescriptionSerializer validation with South African coordinates"""
        # Valid data for Sandton to Pretoria
        valid_data = {
            "pickup_lat": "-26.1067",
            "pickup_lon": "28.0568",
            "dest_lat": "-25.7479",
            "dest_lon": "28.2293",
            "vehicle_type": ["Bakkie"]
        }
        
        serializer = TripDescriptionSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid())
        
        # Valid data for Cape Town to Table Mountain
        valid_data2 = {
            "pickup_lat": "-33.9249",
            "pickup_lon": "18.4241",
            "dest_lat": "-33.9628",
            "dest_lon": "18.4017",
            "vehicle_type": ["1 ton Truck"]
        }
        
        serializer = TripDescriptionSerializer(data=valid_data2)
        self.assertTrue(serializer.is_valid())
        
        # Invalid data - missing fields
        invalid_data = {
            "pickup_lat": "-26.1067",
            "pickup_lon": "28.0568"
        }
        
        serializer = TripDescriptionSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
    
    def test_update_trip_status_serializer(self):
        """Test UpdateTripStatusSerializer validation"""
        # Create a trip
        user = User.objects.create(email="customer@example.co.za", password="test123")
        trip = Trip.objects.create(
            user=user,
            pickup="Sandton City, Johannesburg",
            destination="Pretoria Central"
        )
        
        # Valid data
        valid_data = {
            "trip_id": str(trip.id),
            "status": "picked up"
        }
        
        serializer = UpdateTripStatusSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid())
        
        # Invalid status
        invalid_data = {
            "trip_id": str(trip.id),
            "status": "invalid_status"
        }
        
        serializer = UpdateTripStatusSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())


class SouthAfricaWebSocketTests(TestCase):
    """Tests for WebSocket consumers with South African locations"""
    
    async def setup_auth_driver(self):
        """Setup an authenticated driver for testing"""
        self.driver = await database_sync_to_async(Driver.objects.create)(
            email="driver@example.co.za",
            password="testpassword123",
            vehicle_type="Bakkie",
            is_available=True,
            latitude=-26.2041,  # Johannesburg
            longitude=28.0473
        )
        
        # Mock authenticated scope
        self.driver_scope = {
            "user": self.driver,
            "url_route": {"kwargs": {"driver_id": str(self.driver.id)}}
        }
    
    async def setup_auth_user(self):
        """Setup an authenticated user for testing"""
        self.user = await database_sync_to_async(User.objects.create)(
            email="user@example.co.za",
            password="testpassword123"
        )
        
        # Mock authenticated scope
        self.user_scope = {
            "user": self.user,
            "url_route": {"kwargs": {"driver_id": str(self.driver.id)}}
        }
    
    @patch('trips.consumers.database_sync_to_async')
    async def test_driver_location_consumer(self, mock_database_sync):
        """Test DriverLocationConsumer functionality with South African coordinates"""
        await self.setup_auth_driver()
        
        # Mock database operations
        mock_database_sync.side_effect = lambda f: f
        
        # Setup WebSocket communicator
        communicator = WebsocketCommunicator(
            DriverLocationConsumer.as_asgi(), 
            f"/ws/trips/driver/location/{self.driver.id}/"
        )
        communicator.scope.update(self.driver_scope)
        
        # Connect to the WebSocket
        connected, _ = await communicator.connect()
        self.assertTrue(connected)
        
        # Send location update (driver moving from Joburg to Sandton)
        location_data = {
            "latitude": -26.1067,
            "longitude": 28.0568
        }
        await communicator.send_json_to(location_data)
        
        # Should receive broadcast message back
        response = await communicator.receive_json_from()
        self.assertEqual(response["latitude"], -26.1067)
        self.assertEqual(response["longitude"], 28.0568)
        self.assertEqual(response["driver_id"], str(self.driver.id))
        
        # Disconnect
        await communicator.disconnect()

    @patch('trips.utils.get_route_data')
    @patch('trips.consumers.database_sync_to_async')
    async def test_trip_request_consumer(self, mock_database_sync, mock_get_route_data):
        """Test TripRequestConsumer functionality with SA locations"""
        await self.setup_auth_driver()
        await self.setup_auth_user()
        
        # Mock route data function (Sandton to Pretoria)
        mock_get_route_data.return_value = {
            "distance_km": 55.0,
            "duration_min": 45.0
        }
        
        # Mock database operations
        mock_database_sync.side_effect = lambda f: f
        
        # Setup WebSocket communicator
        communicator = WebsocketCommunicator(
            TripRequestConsumer.as_asgi(), 
            f"/ws/trips/user/request/{self.driver.id}/"
        )
        communicator.scope.update(self.user_scope)
        
        # Connect to the WebSocket
        connected, _ = await communicator.connect()
        self.assertTrue(connected)
        
        # Send trip creation request
        trip_data = {
            "action": "create_trip",
            "vehicle_type": "Bakkie",
            "pickup": "Sandton City, Johannesburg",
            "destination": "Pretoria Central",
            "pickup_lat": -26.1067,
            "pickup_lon": 28.0568,
            "dest_lat": -25.7479,
            "dest_lon": 28.2293,
            "surge": False
        }
        await communicator.send_json_to(trip_data)
        
        # Should receive trip creation confirmation
        response = await communicator.receive_json_from()
        self.assertIn("trip_id", response)
        self.assertIn("estimated_fare", response)
        self.assertEqual(response["distance_km"], 55.0)
        self.assertEqual(response["estimated_time_minutes"], 45.0)
        
        # Disconnect
        await communicator.disconnect()


class SouthAfricaAPIViewTests(TestCase):
    """Tests for API views with South African locations"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Create test user and authenticate
        self.user = User.objects.create_user(
            email="user@example.co.za",
            password="testpassword123"
        )
        self.client.force_authenticate(user=self.user)
        
        # Create test drivers
        self.driver1 = Driver.objects.create(
            email="driver1@example.co.za",
            password="testpassword123",
            vehicle_type="Bakkie",
            is_available=True,
            latitude=-26.2041,  # Johannesburg
            longitude=28.0473
        )
        
        # Create test trip
        self.trip = Trip.objects.create(
            user=self.user,
            driver=self.driver1,
            pickup="Sandton City, Johannesburg",
            destination="Pretoria Central",
            vehicle_type="Bakkie"
        )
    
    @patch('trips.utils.find_nearest_drivers')
    def test_find_drivers_view(self, mock_find_drivers):
        """Test FindDriversView functionality with South African locations"""
        # Mock the find_nearest_drivers function
        mock_find_drivers.return_value = [
            {
                "driver": {
                    "id": str(self.driver1.id),
                    "email": "driver1@example.co.za",
                    "vehicle_type": "Bakkie"
                },
                "distance": 12.5
            }
        ]
        
        # Make API request from Sandton to Johannesburg
        url = reverse('find-drivers')
        data = {
            "pickup_lat": "-26.1067",
            "pickup_lon": "28.0568",
            "dest_lat": "-26.2041",
            "dest_lon": "28.0473",
            "vehicle_type": ["Bakkie"]
        }
        response = self.client.post(url, data, format='json')
        
        # Assert response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("drivers", response.data)
        self.assertEqual(len(response.data["drivers"]), 1)
    
    def test_update_trip_status_view(self):
        """Test UpdateTripStatusView functionality"""
        url = reverse('update-trip-status', args=[self.trip.id])
        data = {
            "trip_id": str(self.trip.id),
            "status": "picked up"
        }
        response = self.client.post(url, data, format='json')
        
        # Assert response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check if trip status was updated
        updated_trip = Trip.objects.get(id=self.trip.id)
        self.assertEqual(updated_trip.status, "picked up")
        
        # Check if driver availability was updated
        updated_driver = Driver.objects.get(id=self.driver1.id)
        self.assertFalse(updated_driver.is_available)
        
        # Test completing a trip
        data = {
            "trip_id": str(self.trip.id),
            "status": "completed"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check if driver's completed trips count was updated
        updated_driver = Driver.objects.get(id=self.driver1.id)
        self.assertEqual(updated_driver.total_trips_completed, 1)
    
    @patch('trips.utils.get_route_data')
    def test_calculate_fare_view(self, mock_get_route_data):
        """Test CalculateFareView functionality with South African distances"""
        # Mock route data for Sandton to Pretoria
        mock_get_route_data.return_value = {
            "distance_km": 55.0,
            "duration_min": 45.0
        }
        
        url = reverse('calculate-fare')
        data = {
            "pickup_lat": "-26.1067",
            "pickup_lon": "28.0568",
            "dest_lat": "-25.7479",
            "dest_lon": "28.2293",
            "vehicle_type": ["Bakkie"]
        }
        response = self.client.post(url, data, format='json')
        
        # Assert response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("estimated_fare", response.data)
        self.assertEqual(response.data["distance_km"], 55.0)
        self.assertEqual(response.data["estimated_time_minutes"], 45.0)
        
        # Calculate expected fare for verification
        # Base fare for Bakkie (80) + 55km * 10 + 45min * 2 = 630
        expected_fare = 80 + 55 * 10 + 45 * 2
        self.assertEqual(response.data["estimated_fare"], expected_fare)


class SouthAfricaIntegrationTests(TestCase):
    """Test complete trip flow from start to finish in South Africa"""
    
    def setUp(self):
        # Create test user
        self.user = User.objects.create(
            email="user@example.co.za",
            password="testpassword123"
        )
        
        # Create test driver
        self.driver = Driver.objects.create(
            email="driver@example.co.za",
            password="testpassword123",
            vehicle_type="Bakkie",
            is_available=True,
            latitude=-26.2041,  # Johannesburg
            longitude=28.0473
        )
        
        # API client
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    @patch('trips.utils.get_route_data')
    @patch('trips.utils.find_nearest_drivers')
    def test_complete_trip_flow(self, mock_find_drivers, mock_get_route_data):
        """Test complete flow from finding a driver to completing a trip"""
        # Mock functions
        mock_get_route_data.return_value = {
            "distance_km": 55.0,
            "duration_min": 45.0
        }
        
        mock_find_drivers.return_value = [
            {
                "driver": {
                    "id": str(self.driver.id),
                    "email": "driver@example.co.za",
                    "vehicle_type": "Bakkie"
                },
                "distance": 12.5
            }
        ]
        
        # Step 1: Find drivers for a trip from Sandton to Pretoria
        url = reverse('find-drivers')
        data = {
            "pickup_lat": "-26.1067",
            "pickup_lon": "28.0568",
            "dest_lat": "-25.7479",
            "dest_lon": "28.2293",
            "vehicle_type": ["Bakkie"]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("drivers", response.data)
        
        # Step 2: Calculate fare
        url = reverse('calculate-fare')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        estimated_fare = response.data["estimated_fare"]
        
        # Step 3: Create a trip manually (since WebSocket is tested separately)
        trip = Trip.objects.create(
            user=self.user,
            driver=self.driver,
            pickup="Sandton City, Johannesburg",
            destination="Pretoria Central",
            pickup_lat=-26.1067,
            pickup_long=28.0568,
            dest_lat=-25.7479,
            dest_long=28.2293,
            vehicle_type="Bakkie",
            accepted_fare=Decimal(estimated_fare)
        )
        
        # Step 4: Update trip status through the lifecycle
        url = reverse('update-trip-status', args=[trip.id])
        
        # Status: Picked up
        data = {
            "trip_id": str(trip.id),
            "status": "picked up"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Status: In Progress
        data = {
            "trip_id": str(trip.id),
            "status": "in progress"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Status: Completed
        data = {
            "trip_id": str(trip.id),
            "status": "completed"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify final trip state
        updated_trip = Trip.objects.get(id=trip.id)
        self.assertEqual(updated_trip.status, "completed")
        
        # Verify driver state
        updated_driver = Driver.objects.get(id=self.driver.id)
        self.assertEqual(updated_driver.total_trips_completed, 1)
