import json
from rest_framework.test import APIClient
from django.test import TestCase

class FareCalculationTestCase(TestCase):
    def setUp(self):
        # Set up your test user
        self.client = APIClient()
        self.user = self.create_test_user()

        # Authenticate the user
        self.client.force_authenticate(user=self.user)

    def create_test_user(self):
        # Create a test user, add your logic to create and return a user
        from django.contrib.auth import get_user_model
        user = get_user_model().objects.create_user(email='nyaruwatastewart27@gmail.com', password='gogochuchu27')
        return user

    def test_calculate_fare_bakkie(self):
        # Example coordinates for Cape Town and Johannesburg (South Africa)
        payload = {
            "pickup_lat": -33.9249,
            "pickup_lon": 18.4241,
            "dest_lat": -26.2041,
            "dest_lon": 28.0473,
            "vehicle_type": ["bakkie"],  # Test with vehicle type "bakkie"
            "surge": False
        }

        # Send POST request to calculate fare
        response = self.client.post('/api/calculate-fare/', payload, format='json')

        # Assert successful response and check fields in the response
        self.assertEqual(response.status_code, 200)
        self.assertIn('estimated_fare', response.data)
        self.assertIn('distance_km', response.data)
        self.assertIn('estimated_time_minutes', response.data)

        # Check if the fare is calculated and data is returned correctly
        estimated_fare = response.data['estimated_fare']
        distance_km = response.data['distance_km']
        estimated_time_minutes = response.data['estimated_time_minutes']

        print(f"Fare (bakkie): {estimated_fare}")
        print(f"Distance (km): {distance_km}")
        print(f"Estimated Time (minutes): {estimated_time_minutes}")

    def test_calculate_fare_1tontruck(self):
        # Example coordinates for Cape Town and Johannesburg (South Africa)
        payload = {
            "pickup_lat": -33.9249,
            "pickup_lon": 18.4241,
            "dest_lat": -26.2041,
            "dest_lon": 28.0473,
            "vehicle_type": ["1 ton Truck"],  # Test with vehicle type "1 ton truck"
            "surge": False
        }

        # Send POST request to calculate fare
        response = self.client.post('/api/calculate-fare/', payload, format='json')

        # Assert successful response and check fields in the response
        self.assertEqual(response.status_code, 200)
        self.assertIn('estimated_fare', response.data)
        self.assertIn('distance_km', response.data)
        self.assertIn('estimated_time_minutes', response.data)

        # Check if the fare is calculated and data is returned correctly
        estimated_fare = response.data['estimated_fare']
        distance_km = response.data['distance_km']
        estimated_time_minutes = response.data['estimated_time_minutes']

        print(f"Fare (sedan): {estimated_fare}")
        print(f"Distance (km): {distance_km}")
        print(f"Estimated Time (minutes): {estimated_time_minutes}")

    def test_calculate_fare_with_surge(self):
        # Example coordinates for Cape Town and Johannesburg (South Africa)
        payload = {
            "pickup_lat": -33.9249,
            "pickup_lon": 18.4241,
            "dest_lat": -26.2041,
            "dest_lon": 28.0473,
            "vehicle_type": ["bakkie"],  # Test with "bakkie" and surge pricing enabled
            "surge": True
        }

        # Send POST request to calculate fare
        response = self.client.post('/api/calculate-fare/', payload, format='json')

        # Assert successful response and check fields in the response
        self.assertEqual(response.status_code, 200)
        self.assertIn('estimated_fare', response.data)
        self.assertIn('distance_km', response.data)
        self.assertIn('estimated_time_minutes', response.data)

        # Check if the fare is calculated and data is returned correctly
        estimated_fare = response.data['estimated_fare']
        distance_km = response.data['distance_km']
        estimated_time_minutes = response.data['estimated_time_minutes']

        print(f"Fare (bakkie with surge): {estimated_fare}")
        print(f"Distance (km): {distance_km}")
        print(f"Estimated Time (minutes): {estimated_time_minutes}")

