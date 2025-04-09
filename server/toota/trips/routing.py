from django.urls import path
from .consumers import (DriverLocationConsumer, UserGetLocationConsumer,
                        TripRequestConsumer, DriverTripConsumer, DriverUpdateTripStatusConsumer, UserGetTripStatusConsumer,
                        UserGetAvailableDrivers)

websocket_urlpatterns = [
    path("ws/trips/driver/location/", DriverLocationConsumer.as_asgi()),
    path("ws/trips/user/location/<str:driver_id>/", UserGetLocationConsumer.as_asgi()),
    path("ws/trips/user/", TripRequestConsumer.as_asgi()),
    path("ws/trips/driver/", DriverTripConsumer.as_asgi()),
    path("ws/trips/driver/status/<str:trip_id>/", DriverUpdateTripStatusConsumer.as_asgi()),
    path("ws/trips/user/status/<str:trip_id>/", UserGetTripStatusConsumer.as_asgi()),
    path("ws/trips/drivers/all/", UserGetAvailableDrivers.as_asgi())
]
