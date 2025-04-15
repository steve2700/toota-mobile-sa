from rest_framework import serializers
from authentication.models import Driver
from trips.models import DriverRating

class FindDriversSerializer(serializers.ModelSerializer):
    class Meta:
        model = Driver
        exclude = ['password', 'last_login', 'is_superuser', 'is_staff', 'is_active', 'groups', 'user_permissions', 'created_at', 'updated_at',
                  'license_number', 'license_expiry', 'number_plate', 'physical_address', 'vehicle_registration', 'earnings']

class CheckTripStatusSerializer(serializers.Serializer):
    trip_id = serializers.UUIDField(required=True)

class DriverRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = DriverRating
        fields = ['driver', 'rating', 'review']

    def validate_rating(self, value):
        if not (1 <= value <= 5):
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value