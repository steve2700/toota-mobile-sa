import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import DriverProfile, Trip
from .utils import calculate_distance

class TripConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.trip_id = self.scope['url_route']['kwargs']['trip_id']
        self.room_group_name = f'trip_{self.trip_id}'

        # Join trip group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave trip group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        trip_id = data.get('trip_id')

        try:
            trip = Trip.objects.get(id=trip_id)
            pickup_lat, pickup_lon = data['pickup_lat'], data['pickup_lon']
            selected_vehicle = trip.vehicle_type

            # Find nearby drivers with the selected vehicle type
            drivers = DriverProfile.objects.filter(
                is_available=True,
                vehicle_type=selected_vehicle
            )

            nearby_drivers = []
            expanded_radius = 5  # Initial search radius in km
            max_radius = 20  # Max radius limit
            driver_found = False

            while not driver_found and expanded_radius <= max_radius:
                for driver in drivers:
                    distance = calculate_distance(pickup_lat, pickup_lon, driver.latitude, driver.longitude)
                    if distance <= expanded_radius:
                        nearby_drivers.append({
                            'driver_id': driver.user.id,
                            'driver_name': driver.user.username,
                            'distance': round(distance, 2),
                            'latitude': driver.latitude,
                            'longitude': driver.longitude,
                        })
                if nearby_drivers:
                    driver_found = True
                else:
                    expanded_radius += 5  # Expand the search radius

            if nearby_drivers:
                # Notify user about nearby drivers
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'update_user',
                        'drivers': nearby_drivers
                    }
                )
            else:
                # Notify user if no drivers found within max radius
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'update_user',
                        'message': 'No drivers found. Expanding search radius...'
                    }
                )
        except Trip.DoesNotExist:
            await self.send(json.dumps({'error': 'Invalid trip ID'}))

    async def update_user(self, event):
        # Send message to WebSocket user with the updated data
        await self.send(text_data=json.dumps(event))
