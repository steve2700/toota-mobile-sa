from django.urls import path
from .views import (
    CheckTripStatusView, SetDriverOnlineStatus
)

urlpatterns = [
    path("<uuid:trip_id>/status/", CheckTripStatusView.as_view(), name="update-trip-status"),
    path("driver/online-status/", SetDriverOnlineStatus.as_view(), name="set-driver-online-status")
]
