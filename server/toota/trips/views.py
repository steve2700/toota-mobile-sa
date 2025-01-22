from rest_framework import generics, status
from rest_framework.response import Response
from .models import Trip, DriverProfile
from .serializers import TripSerializer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

class CreateTripView(generics.CreateAPIView):
    queryset = Trip.objects.all()
    serializer_class = TripSerializer

    def perform_create(self, serializer):
        # Assign the logged-in user as the trip creator
        serializer.save(user=self.request.user)

        # Notify nearby drivers
        trip = serializer.instance
        self.notify_nearby_drivers(trip)

    def notify_nearby_drivers(self, trip):
        # Find nearby drivers with matching vehicle type
        nearby_drivers = DriverProfile.objects.filter(
            vehicle_type=trip.vehicle_type,
            is_available=True
        )
        for driver in nearby_drivers:
            # Send WebSocket notification to each driver
            self.send_websocket_notification(driver.user, trip)

    def send_websocket_notification(self, driver, trip):
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'driver_{driver.id}',
            {
                'type': 'send_notification',
                'message': {
                    'trip_id': trip.id,
                    'pickup_location': trip.pickup_location,
                    'dropoff_location': trip.dropoff_location,
                    'vehicle_type': trip.vehicle_type,
                    'bid_amount': trip.bid_amount,
                }
            }
        )
