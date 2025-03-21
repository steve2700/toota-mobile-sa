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
