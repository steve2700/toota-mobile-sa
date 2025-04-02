from rest_framework import serializers
from authentication.models import Driver

class FindDriversSerializer(serializers.ModelSerializer):
    class Meta:
        model = Driver
        exclude = ['password']

class CheckTripStatusSerializer(serializers.Serializer):
    trip_id = serializers.UUIDField(required=True)
