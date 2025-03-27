from rest_framework import serializers
from .models import Payment
from trips.models import Trip


class PaymentSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    payment_method = serializers.ChoiceField(choices=['card', 'mobile_money', 'bank_transfer', 'cash'])
    currency = serializers.CharField(max_length=3)
    trip_id = serializers.UUIDField()
    location = serializers.CharField(max_length=3)

    class Meta:
        model = Payment
        fields = ['trip_id', 'currency', 'payment_method', 'user', 'amount', 'transaction_id',
                  'payment_reference', 'created_at', 'location']
        read_only_fields = ['amount', 'transaction_id', 'payment_reference', 'created_at']

    def validate_trip_id(self, value):
        try:
            trip = Trip.objects.get(id=value)
            if Payment.objects.filter(trip_id=value, status='success').exists():
                raise serializers.ValidationError("This trip has already been paid for.")
            return value
        except Trip.DoesNotExist:
            raise serializers.ValidationError("Invalid trip ID. Trip does not exist.")

    def validate_currency(self, value):
        valid_currencies = ['USD', 'NGN', 'KES', 'ZAR', 'GHS']
        if value.upper() not in valid_currencies:
            raise serializers.ValidationError(f"Unsupported currency: {value}. Use one of {valid_currencies}")
        return value.upper()
    
    def validate_location(self, value):
        valid_locations = ['ZA', 'KE', 'GH', 'NG']
        if value.upper() not in valid_locations:
            raise serializers.ValidationError(f"Unsupported location: {value}. Use one of {valid_locations}")
        return value.upper()
