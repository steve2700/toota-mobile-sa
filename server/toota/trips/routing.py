from django.urls import path
from .consumers import (DriverLocationConsumer, PassengerGetLocationConsumer,
                        TripRequestConsumer, DriverTripConsumer)

websocket_urlpatterns = [
    path("ws/trips/driver/location/<str:driver_id>/", DriverLocationConsumer.as_asgi()),
    path("ws/trips/user/location/<str:driver_id>/", PassengerGetLocationConsumer.as_asgi()),
    path("ws/trips/user/request/<str:driver_id>/", TripRequestConsumer.as_asgi()),
    path("ws/trips/driver/response/<str:driver_id>/", DriverTripConsumer.as_asgi()),
]

