from django.urls import path
from .views import (
    CheckTripStatusView,
    WebSocketAvailableDriversDocView,
    WebSocketTripRequestDocView,
    WebSocketDriverTripStatusView,
    WebSocketDriverTripView
)

urlpatterns = [
    path("<uuid:trip_id>/status/", CheckTripStatusView.as_view(), name="update-trip-status"),

    # WebSocket Documentation Views
    path("docs/available-drivers/", WebSocketAvailableDriversDocView.as_view(), name="websocket-available-drivers"),
    path("docs/trip-request/", WebSocketTripRequestDocView.as_view(), name="websocket-trip-request"),
    path("docs/driver-trip-status/", WebSocketDriverTripStatusView.as_view(), name="websocket-driver-trip-status"),
    path("docs/driver-trip/", WebSocketDriverTripView.as_view(), name="websocket-driver-trip"),
]
