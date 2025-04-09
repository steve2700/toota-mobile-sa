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


class WebSocketDriverTripStatusView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Connect to WebSocket to update trip status",
        operation_description="""
        WebSocket Endpoint: `ws://toota-mobile-sa.onrender.com/ws/trips/driver/status/trip_id/`

        **Expected WebSocket Payload**:
        ```json
        {
          "trip_status": "arrived at pickup"
        }
        ```

        **Server Sends Back (if cash payment is pending)**:
        ```json
        {
          "payment_status": "arrived at pickup",
          "trip_id": "abc123",
          "message": "You must collect payment from user before pickup"
        }
        ```

        WebSocket sends `ping` every 30 seconds to keep the connection alive.
        """,
        responses={200: openapi.Response("WebSocket documentation view")}
    )
    def get(self, request, trip_id):
        return Response({
            "message": "This view documents the WebSocket consumer for updating trip status.",
            "websocket_endpoint": f"ws://toota-mobile-sa.onrender.com/ws/trips/driver/status/{trip_id}/"
        })


class WebSocketDriverTripView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Connect to WebSocket to handle trip requests in real-time",
        operation_description="""
        WebSocket Endpoint: `ws://toota-mobile-sa.onrender.com/ws/trips/driver/`

        **Expected WebSocket Payload**:
        ```json
        {
          "trip_id": "12345",
          "driver_response_status": "accepted"
        }
        ```

        **Server Sends Back**:
        1. If trip is accepted:
        ```json
        {
          "message": "Trip 12345 accepted"
        }
        ```

        2. If payment is not completed:
        ```json
        {
          "error": "Card payment not completed. Cannot accept trip."
        }
        ```

        3. If trip is rejected:
        ```json
        {
          "status": "rejected",
          "trip_id": "12345"
        }
        ```

        **Server Sends Ping**: 
        WebSocket sends a `ping` message every 30 seconds to keep the connection alive.

        WebSocket will notify the user when the trip is accepted, rejected, or updated.
        """,
        responses={200: openapi.Response("WebSocket documentation view")}
    )
    def get(self, request, trip_id):
        return Response({
            "message": "This view documents the WebSocket consumer for handling trip requests from drivers.",
            "websocket_endpoint": f"ws://toota-mobile-sa.onrender.com/ws/trips/driver/"
        })
