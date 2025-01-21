from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Trip
from .serializers import TripSerializer

class CreateTripView(APIView):
    def post(self, request):
        serializer = TripSerializer(data=request.data)
        if serializer.is_valid():
            # Create the trip and set the initial status as "finding_driver"
            trip = serializer.save(user=request.user, status='finding_driver')

            # Return the trip ID so that the client can connect to the WebSocket
            return Response({'trip_id': trip.id}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
