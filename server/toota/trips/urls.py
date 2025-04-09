from django.urls import path
from .views import (CheckTripStatusView, 
                    WebSocketAvailableDriversDocView, WebSocketDriverTripStatusView, WebSocketDriverTripView)

urlpatterns = [
    path("<uuid:trip_id>/status/", CheckTripStatusView.as_view(), name="update-trip-status"),
    path("docs/available-drivers/", WebSocketAvailableDriversDocView.as_view(), name="websocket-available-drivers"),
    path("docs/driver-trip-status/", WebSocketDriverTripStatusView.as_view(), name="websocket-driver-trip-status"),
    path("docs/driver-trip/", WebSocketDriverTripView.as_view(), name="websocket-driver-trip"),
]
