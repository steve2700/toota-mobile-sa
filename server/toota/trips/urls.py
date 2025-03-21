from django.urls import path
from .views import (CheckTripStatusView)

urlpatterns = [
    path("<uuid:trip_id>/status/", CheckTripStatusView.as_view(), name="update-trip-status"),
]
