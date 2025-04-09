import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from dotenv import load_dotenv
from .models import Trip
from authentication.models import Driver
from .serializers import (
    CheckTripStatusSerializer
)
from .utils import find_nearest_drivers

load_dotenv()
logger = logging.getLogger(__name__)


class CheckTripStatusView(APIView):
    @swagger_auto_schema(
        operation_description="Check trip status (e.g., pending -> accepted -> in_progress -> completed).",
        request_body=CheckTripStatusSerializer,
        responses={200: "Trip status updated.", 400: "Invalid data."}
    )
    def post(self, request):
        serializer = CheckTripStatusSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"error": "Invalid input data", "details": serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)

        trip_id = serializer.validated_data["trip_id"]

        try:
            trip = Trip.objects.get(id=trip_id)
        except Trip.DoesNotExist:
            return Response({"error": "Trip not found."}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"trip_status": trip.status}, status=status.HTTP_200_OK)

# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class WebSocketAvailableDriversDocView(APIView):
    """
    Dummy view to document WebSocket endpoint for getting available drivers in real-time.
    """

    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Connect to WebSocket for real-time nearest drivers",
        operation_description="""
        WebSocket Endpoint: `ws://toota-mobile-sa.onrender.com/ws/trips/drivers/all/`

        **Expected WebSocket Payload**:
        ```json
        {
          "user_latitude": "6.5244",
          "user_longitude": "3.3792",
        }
        ```

        **Server Sends Back**:
        ```json
        {
          "type": "nearest_drivers",
          "nearest_drivers": [
            [
              {
                "id": 12,
                "name": "John",
                "latitude": 6.53,
                "longitude": 3.37,
                ...
              },
              {
                "distance": "1.2km",
                "duration": "5mins"
              }
            ]
          ]
        }
        ```

        WebSocket sends `ping` every 30 seconds to keep the connection alive.
        """,
        responses={200: openapi.Response("WebSocket documentation view")}
    )
    def get(self, request):
        return Response({
            "message": "This view documents the WebSocket consumer for available drivers.",
            "websocket_endpoint": "ws://toota-mobile-sa.onrender.com/ws/trips/drivers/all/"
        })


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class WebSocketTripRequestDocView(APIView):
    """
    Dummy view to document WebSocket endpoint for handling trip requests in real-time.
    """

    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Connect to WebSocket for real-time trip requests",
        operation_description="""
        WebSocket Endpoint: `ws://toota-mobile-sa.onrender.com/ws/trips/user/`

        **Expected WebSocket Payloads**:
        1. **Create Trip**:
        ```json
        {
          "action": "create_trip",
          "vehicle_type": "sedan",
          "pickup": "123 Main St",
          "destination": "456 Elm St",
          "pickup_lat": 6.5244,
          "pickup_lon": 3.3792,
          "dest_lat": 6.6000,
          "dest_lon": 3.4000,
          "load_description": "2 boxes of goods"
        }
        ```

        2. **Confirm Driver**:
        ```json
        {
          "action": "confirm_driver",
          "trip_id": "123e4567-e89b-12d3-a456-426614174000",
          "driver_id": "789e1234-e89b-12d3-a456-426614174111"
        }
        ```

        **Server Sends Back**:
        - For `create_trip`:
        ```json
        {
          "message": "Trip created successfully - select a driver",
          "trip_id": "123e4567-e89b-12d3-a456-426614174000",
          "estimated_fare": 1500.0,
          "distance_km": 12.5,
          "estimated_time": "25 mins",
          "pickup": "123 Main St",
          "destination": "456 Elm St",
          "vehicle_type": "sedan",
          "load_description": "2 boxes of goods",
          "user_info": {
            "id": "1",
            "name": "John Doe",
            "phone": "+1234567890"
          },
          "available_drivers": [
            {
              "id": "789e1234-e89b-12d3-a456-426614174111",
              "name": "Driver A",
              "distance": "1.2km",
              "duration": "5 mins"
            }
          ],
          "status": "pending"
        }
        ```

        - For `confirm_driver`:
        ```json
        {
          "message": "Awaiting driver response",
          "trip_id": "123e4567-e89b-12d3-a456-426614174000",
          "status": "pending",
          "driver_info": {
            "id": "789e1234-e89b-12d3-a456-426614174111",
            "name": "Driver A",
            "phone": "+1234567890",
            "vehicle_type": "sedan",
            "rating": 4.8
          },
          "payment_info": {
            "payment_method": "card",
            "payment_status": "success",
            "amount": 1500.0,
            "currency": "NGN"
          }
        }
        ```

        WebSocket sends `ping` every 30 seconds to keep the connection alive.
        """,
        responses={200: openapi.Response("WebSocket documentation view")}
    )
    def get(self, request):
        return Response({
            "message": "This view documents the WebSocket consumer for trip requests.",
            "websocket_endpoint": "ws://toota-mobile-sa.onrender.com/ws/trips/user/"
        })