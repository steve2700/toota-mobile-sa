from rest_framework import serializers
from .models import Trip
from authentication.models import Driver
<<<<<<< HEAD
from django.core.validators import MinValueValidator
from trips.models import Trip, Payment
=======
>>>>>>> origin/pricing-algorithm


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
<<<<<<< HEAD
        choices=["pending", "picked up", "in progress", "completed", "cancelled"],
        required=True
    )

class PaymentSerializer(serializers.ModelSerializer):
    # user = serializers.HiddenField(default=serializers.CurrentUserDefault())  # Auto-fill authenticated user
    amount = serializers.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(0.01)] # ensures there cannot be 0 or negative amount
    )
    payment_method = serializers.ChoiceField(choices=['card', 'mobile_money', 'bank_transfer', 'cash'])
    currency = serializers.CharField(max_length=3)  # Ensure it's a valid 3-letter currency code
    trip_id = serializers.UUIDField() # ensures valid uuid is provided

    class Meta:
        model = Payment
        fields = ['user', 'trip_id', 'amount', 'currency', 'payment_method', 'transaction_id', 'payment_reference', 'status', 'created_at']
        read_only_fields = ['transaction_id', 'payment_reference', 'status', 'created_at']  # These are set by the system

    def validate_trip_id(self, value):
        """Ensure the trip exists and is unpaid."""
        try:
            trip = Trip.objects.get(id=value)
            if Payment.objects.filter(trip_id=value, status='success').exists():
                raise serializers.ValidationError("This trip has already been paid for.")
            return value
        except Trip.DoesNotExist:
            raise serializers.ValidationError("Invalid trip ID. Trip does not exist.")

    def validate_currency(self, value):
        """Ensure currency is a valid 3-letter ISO code."""
        valid_currencies = ['USD', 'NGN', 'KES', 'ZAR', 'GHS']  # Add more if needed
        if value.upper() not in valid_currencies:
            raise serializers.ValidationError(f"Unsupported currency: {value}. Use one of {valid_currencies}")
        return value.upper()  # Convert to uppercase

    def create(self, validated_data):
        """Create a new payment transaction."""
        validated_data['transaction_id'] = self.generate_transaction_id()  # Generate unique transaction ID
        return super().create(validated_data)

    def generate_transaction_id(self):
        """Generate a unique transaction ID."""
        import uuid
        return str(uuid.uuid4())
=======
        choices=["pending", "in_progress", "completed", "cancelled"],
        required=True
    )

>>>>>>> origin/pricing-algorithm
