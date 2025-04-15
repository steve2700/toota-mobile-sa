import logging
from dotenv import load_dotenv
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Trip
from .serializers import CheckTripStatusSerializer, DriverRatingSerializer
from .utils import find_nearest_drivers
from authentication.models import Driver

load_dotenv()
logger = logging.getLogger(__name__)


class CheckTripStatusView(APIView):
    @swagger_auto_schema(
        operation_description="Check trip status (e.g., pending → accepted → in_progress → completed).",
        request_body=CheckTripStatusSerializer,
        responses={200: "Trip status updated.", 400: "Invalid data."}
    )
    def post(self, request):
        serializer = CheckTripStatusSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"error": "Invalid input", "details": serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            trip = Trip.objects.get(id=serializer.validated_data["trip_id"])
        except Trip.DoesNotExist:
            return Response({"error": "Trip not found."}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"trip_status": trip.status}, status=status.HTTP_200_OK)

class SetDriverOnlineStatus(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Set the online status of a driver.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['is_online'],
            properties={
                'is_online': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Online status (True/False)')
            }
        ),
        responses={200: "Status updated successfully", 400: "Invalid input"}
    )
    def post(self, request):
        driver_id = request.user.id
        is_online = request.data.get("is_online")

        if driver_id is None or is_online is None:
            return Response({"error": "driver_id and is_online are required."},
                            status=status.HTTP_400_BAD_REQUEST)
        if not isinstance(is_online, bool):
            return Response({"error": "is_online must be a boolean."},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            driver = Driver.objects.get(id=driver_id)
        except Driver.DoesNotExist:
            return Response({"error": "Driver not found."}, status=status.HTTP_404_NOT_FOUND)
        if not driver.is_available:
            return Response({"error": "Cannot change status while trip is ongoing"},
                            status=status.HTTP_400_BAD_REQUEST)

        driver.is_online = is_online
        driver.save()

        return Response({"message": f"Driver is now {'online' if is_online else 'offline'}."}, status=status.HTTP_200_OK)

class DriverRating(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Rate a driver.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'driver': openapi.Schema(type=openapi.TYPE_STRING, description='Driver ID'),
                'rating': openapi.Schema(type=openapi.TYPE_NUMBER, format=openapi.FORMAT_FLOAT, description='Rating (1-5)'),
                'review': openapi.Schema(type=openapi.TYPE_STRING, description='Review text', default='')
            }
        ),
        responses={200: "Driver rated successfully.", 400: "Invalid data."}
    )
    def post(self, request):
        serializer = DriverRatingSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"error": "Invalid input", "details": serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)

        driver = serializer.validated_data["driver"]
        rating = serializer.validated_data["rating"]
        review = serializer.validated_data.get("review", "")

        DriverRating.objects.create(
            driver=driver,
            user=request.user,
            rating=rating,
            review=review
        )

        return Response({"message": "Driver rated successfully."}, status=status.HTTP_200_OK)
