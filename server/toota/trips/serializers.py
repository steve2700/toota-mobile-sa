from rest_framework import serializers
from .models import Trip
from authentication.models import Driver


class TripDescriptionSerializer(serializers.Serializer):
    """
    Serializer for handling trip location input.
    """
    pickup_lat = serializers.FloatField(required=True)
    pickup_lon = serializers.FloatField(required=True)
    # Additional fields for destination coordinates and surge flag
    dest_lat = serializers.FloatField(required=True)
    dest_lon = serializers.FloatField(required=True)
    surge = serializers.BooleanField(required=False, default=False)
    vehicle_type = serializers.ListField(
        child=serializers.ChoiceField(choices=[
            ('Motorbike', 'Motorbike'),
            ('1 ton Truck', '1 ton Truck'),
            ('1.5 ton Truck', '1.5 ton Truck'),
            ('2 ton Truck', '2 ton Truck'),
            ('4 ton Truck', '4 ton Truck'),
            ('Bakkie', 'Bakkie'),
            ('8 ton Truck', '8 ton Truck'),
        ]),
        required=True
    )


class FindDriversSerializer(serializers.ModelSerializer):
    """
    Serializer for returning nearest available drivers.
    """    
    class Meta:
        model = Driver
        fields = '__all__'


class UpdateTripStatusSerializer(serializers.Serializer):
    """
    Serializer for updating trip status.
    """
    trip_id = serializers.IntegerField(required=True)
    status = serializers.ChoiceField(
        choices=["pending", "in_progress", "completed", "cancelled"],
        required=True
    )

