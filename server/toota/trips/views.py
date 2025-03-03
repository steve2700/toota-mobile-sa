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
    permission_classes = [IsAuthenticated]  # make sure the user is authenticated

    @swagger_auto_schema(
        operation_description="Find nearest available drivers.",
        request_body=TripDescriptionSerializer,
        responses={200: "List of nearest drivers.", 400: "Invalid input data."}
    )
    def post(self, request):
        """
        Handles POST request to fetch available drivers near the pickup location.
        """
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
    # permission_classes = [IsAuthenticated] # make sure the user is authenticated

    @swagger_auto_schema(
        operation_description="Update trip status (e.g., pending -> accepted -> in_progress -> completed).",
        request_body=UpdateTripStatusSerializer,
        responses={200: "Trip status updated.", 400: "Invalid data."}
    )
    def post(self, request):
        """
        Handles trip status updates.
        """
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


class CalculateFareView(APIView):
    """
    POST endpoint to calculate and return an estimated fare for a trip.
    Expected payload includes pickup and destination coordinates,
    vehicle_type, and an optional surge flag.
    """
    @swagger_auto_schema(
        operation_description="Calculate the fare for a trip based on vehicle type, distance, and time.",
        request_body=TripDescriptionSerializer,
        responses={200: openapi.Response(description="Fare calculated successfully.")}
    )
    def post(self, request, *args, **kwargs):
        serializer = TripDescriptionSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data

            pickup_lat = data.get('pickup_lat')
            pickup_lon = data.get('pickup_lon')
            dest_lat = data.get('dest_lat')
            dest_lon = data.get('dest_lon')
            surge = data.get('surge', False)
            vehicle_types = data.get('vehicle_type')
            vehicle_type = vehicle_types[0] if vehicle_types else None

            # Get real route data
            route_data = get_route_data(pickup_lat, pickup_lon, dest_lat, dest_lon)
            distance_km = route_data["distance_km"]
            estimated_time_str = route_data["duration"]

            # Parse the estimated time to convert it into minutes (or other units if required)
            estimated_time_minutes = 0.0
            if "hour" in estimated_time_str:
                # Handle case where hours are present (e.g., "1 hour 10 min")
                hours = 0
                minutes = 0
                seconds = 0

                # Extract hours, minutes, and seconds if present
                parts = estimated_time_str.split(' ')
                for i in range(len(parts)):
                    if 'hour' in parts[i]:
                        hours = int(parts[i-1])  # The number before 'hour' is the number of hours
                    elif 'min' in parts[i]:
                        minutes = int(parts[i-1])  # The number before 'min' is the number of minutes
                    elif 'sec' in parts[i]:
                        seconds = int(parts[i-1])  # The number before 'sec' is the number of seconds

                estimated_time_minutes = hours * 60 + minutes + seconds / 60
            elif "min" in estimated_time_str:
                # Handle case where only minutes are present (e.g., "40 min")
                estimated_time_minutes = float(estimated_time_str.replace(" min", ""))
            elif "sec" in estimated_time_str:
                # Handle case where only seconds are present (e.g., "30 sec")
                estimated_time_minutes = float(estimated_time_str.replace(" sec", "")) / 60

            trip = Trip(
                vehicle_type=vehicle_type,
                pickup=f'{pickup_lat},{pickup_lon}',
                destination=f'{dest_lat},{dest_lon}'
            )
            estimated_fare = trip.calculate_fare(distance_km, estimated_time_minutes, surge)

            return Response({
                'estimated_fare': estimated_fare,
                'distance_km': distance_km,
                'estimated_time': estimated_time_str  # Now it's in readable format
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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