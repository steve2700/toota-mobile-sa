from django.urls import path
from .views import FindDriversView, UpdateTripStatusView, CalculateFareView

urlpatterns = [
    path("find-driver/", FindDriversView.as_view(), name="find-drivers"),
    path("calculate-fare/", CalculateFareView.as_view(), name="calculate-fare"),
    path("<uuid:trip_id>/status/", UpdateTripStatusView.as_view(), name="update-trip-status"),
]

