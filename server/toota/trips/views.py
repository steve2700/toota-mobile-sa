import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Trip
from authentication.models import Driver
from .serializers import (
    TripDescriptionSerializer,
    UpdateTripStatusSerializer
)
from .utils import find_nearest_drivers, get_route_data

logger = logging.getLogger(__name__)


class FindDriversView(APIView):
    """
    API View to fetch the nearest available drivers.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Find nearest available drivers.",
        request_body=TripDescriptionSerializer,
        responses={200: "List of nearest drivers.", 400: "Invalid input data."}
    )
    def post(self, request):
        logger.info("Finding nearest available drivers.")
        serializer = TripDescriptionSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({"error": "Invalid input data", "details": serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)

        pickup_lat = serializer.validated_data["pickup_lat"]
        pickup_lon = serializer.validated_data["pickup_lon"]
        vehicle_type = serializer.validated_data["vehicle_type"]

        available_drivers = find_nearest_drivers(float(pickup_lat), float(pickup_lon), vehicle_type)

        if not available_drivers:
            return Response({"message": "No available drivers nearby"}, status=status.HTTP_200_OK)

        return Response({"message": "Available drivers found", "drivers": available_drivers},
                        status=status.HTTP_200_OK)


class UpdateTripStatusView(APIView):
    """
    API View to update the status of an existing trip.
    """
    # permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Update trip status (e.g., pending -> accepted -> in_progress -> completed).",
        request_body=UpdateTripStatusSerializer,
        responses={200: "Trip status updated.", 400: "Invalid data."}
    )
    def post(self, request):
        serializer = UpdateTripStatusSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"error": "Invalid input data", "details": serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)

        trip_id = serializer.validated_data["trip_id"]
        new_status = serializer.validated_data["status"]

        try:
            trip = Trip.objects.get(id=trip_id)
            driver = Driver.objects.get(id=trip.driver.id)
            if new_status == "picked up":
                driver.is_available = False
                driver.save()
            elif new_status == "completed":
                driver.total_trips_completed += 1
                driver.save()
        except Trip.DoesNotExist:
            return Response({"error": "Trip not found."}, status=status.HTTP_400_BAD_REQUEST)
        trip.status = new_status
        trip.save()
        return Response({"message": "Trip status updated successfully."}, status=status.HTTP_200_OK)

class PaymentView(APIView):
    """
    API View to handle trip payments.
    """
    # permission_classes = [IsAuthenticated] # make sure the user is authenticated

    @swagger_auto_schema(
        operation_description="Handle trip payments.",
        request_body=UpdateTripStatusSerializer,
        responses={200: "Payment processed.", 400: "Invalid data."}
    )
    def post(self, request):
        """
        Handles trip payments.
        """
        serializer = UpdateTripStatusSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"error": "Invalid input data", "details": serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)

        trip_id = serializer.validated_data["trip_id"]
        new_status = serializer.validated_data["status"]

        try:
            trip = Trip.objects.get(id=trip_id)
        except Trip.DoesNotExist:
            return Response({"error": "Trip not found."}, status=status.HTTP_400_BAD_REQUEST)

        if new_status == "completed":
            trip.status = new_status
            trip.save()
            return Response({"message": "Payment processed successfully."}, status=status.HTTP_200_OK)
        return Response({"error": "Invalid status for payment"}, status=status.HTTP_400_BAD_REQUEST)
