from django.urls import path
from .consumers import (DriverLocationConsumer, UserGetLocationConsumer,
                        TripRequestConsumer, DriverTripConsumer, DriverUpdateTripStatusConsumer, UserGetTripStatusConsumer)

websocket_urlpatterns = [
    path("ws/trips/driver/location/", DriverLocationConsumer.as_asgi()),
    path("ws/trips/user/location/<str:driver_id>/", UserGetLocationConsumer.as_asgi()),
    path("ws/trips/user/request/", TripRequestConsumer.as_asgi()),
    path("ws/trips/driver/response/", DriverTripConsumer.as_asgi()),
    path("ws/trips/driver/status/update/<str:trip_id>/", DriverUpdateTripStatusConsumer.as_asgi()),
    path("ws/trips/user/status/<str:trip_id>/", UserGetTripStatusConsumer.as_asgi()),
]

