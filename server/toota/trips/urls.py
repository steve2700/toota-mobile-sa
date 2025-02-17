from django.urls import path
from .views import FindDriversView
from .views import UpdateTripStatusView

urlpatterns = [
    path("find-driver/", FindDriversView.as_view(), name="find-drivers"),
    path("<uuid:trip_id>/status/", UpdateTripStatusView.as_view(), name="update-trip-status"),
]
