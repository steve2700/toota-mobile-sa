import logging
from dotenv import load_dotenv
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Trip
from .serializers import CheckTripStatusSerializer
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


class WebSocketDocBaseView(APIView):
    permission_classes = [IsAuthenticated]

    def get_doc_response(self, message, endpoint):
        return Response({
            "message": message,
            "websocket_endpoint": endpoint
        })


class WebSocketAvailableDriversDocView(WebSocketDocBaseView):
    @swagger_auto_schema(
        operation_summary="Real-time nearest drivers WebSocket",
        operation_description="""
        WebSocket: `ws://toota-mobile-sa.onrender.com/ws/trips/drivers/all/`

        Expected:
        ```json
        {
          "user_latitude": "6.5244",
          "user_longitude": "3.3792"
        }
        ```

        Response:
        ```json
        {
          "type": "nearest_drivers",
          "nearest_drivers": [...]
        }
        ```
        """,
        responses={200: openapi.Response("WebSocket documentation view")}
    )
    def get(self, request):
        return self.get_doc_response(
            "Real-time nearest drivers WebSocket",
            "ws://toota-mobile-sa.onrender.com/ws/trips/drivers/all/"
        )


class WebSocketTripRequestDocView(WebSocketDocBaseView):
    @swagger_auto_schema(
        operation_summary="Trip requests in real-time via WebSocket",
        operation_description="""
        WebSocket: `ws://toota-mobile-sa.onrender.com/ws/trips/user/`
        
        Actions: `create_trip`, `confirm_driver`
        """,
        responses={200: openapi.Response("WebSocket documentation view")}
    )
    def get(self, request):
        return self.get_doc_response(
            "Real-time trip request WebSocket",
            "ws://toota-mobile-sa.onrender.com/ws/trips/user/"
        )


class WebSocketDriverTripStatusView(WebSocketDocBaseView):
    @swagger_auto_schema(
        operation_summary="Driver trip status WebSocket",
        operation_description="""
        WebSocket: `ws://toota-mobile-sa.onrender.com/ws/trips/driver/status/`
        """,
        responses={200: openapi.Response("WebSocket documentation view")}
    )
    def get(self, request):
        return self.get_doc_response(
            "Real-time driver trip status WebSocket",
            "ws://toota-mobile-sa.onrender.com/ws/trips/driver/status/"
        )


class WebSocketDriverTripView(WebSocketDocBaseView):
    @swagger_auto_schema(
        operation_summary="Driver trip management WebSocket",
        operation_description="""
        WebSocket: `ws://toota-mobile-sa.onrender.com/ws/trips/driver/`
        """,
        responses={200: openapi.Response("WebSocket documentation view")}
    )
    def get(self, request):
        return self.get_doc_response(
            "Real-time driver trip management WebSocket",
            "ws://toota-mobile-sa.onrender.com/ws/trips/driver/"
        )
