from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import ClientUser as User, Driver


###############################################################################
# Base Serializers
###############################################################################

class BaseSignupSerializer(serializers.ModelSerializer):
    """
    Base serializer for signup operations.
    Expects inheriting serializers to specify the model and fields.
    """
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = None
        fields = ('email', 'password', 'first_name', 'last_name')
    
    def create(self, validated_data):
        # Delegate creation to the model's custom manager's create_user method
        return self.Meta.model.objects.create_user(**validated_data)


class BaseLoginSerializer(serializers.Serializer):
    """
    Base serializer for login operations.
    Validates email and password, returning the authenticated user.
    """
    email = serializers.EmailField()
    password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )
    
    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        user = authenticate(request=self.context.get('request'), email=email, password=password)
        if not user:
            raise serializers.ValidationError("Unable to log in with provided credentials.")
        data['user'] = user
        return data

###############################################################################
# User Serializers
###############################################################################

class UserSignupSerializer(BaseSignupSerializer):
    """
    Serializer for client user signup.
    Includes additional fields such as physical_address and profile_pic.
    """
    class Meta(BaseSignupSerializer.Meta):
        model = User
        fields = BaseSignupSerializer.Meta.fields + ('physical_address', 'profile_pic',)


class UserLoginSerializer(BaseLoginSerializer):
    """
    Serializer for client user login.
    Validates that the authenticated user is a User instance.
    """
    def validate(self, data):
        data = super().validate(data)
        user = data.get('user')
        if not isinstance(user, User):
            raise serializers.ValidationError("Invalid credentials for a user.")
        return data


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for retrieving and updating client user profiles.
    The email field is read-only.
    """
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'physical_address', 'profile_pic')
        read_only_fields = ('email',)


###############################################################################
# Driver Serializers
###############################################################################

class DriverSignupSerializer(BaseSignupSerializer):
    """
    Serializer for driver signup.
    For drivers, only email and password are required.
    """
    class Meta(BaseSignupSerializer.Meta):
        model = Driver
        # Only include email and password; other driver-specific fields are omitted.
        fields = ('email', 'password',)


class DriverLoginSerializer(BaseLoginSerializer):
    """
    Serializer for driver login.
    Validates that the authenticated user is a Driver instance.
    """
    def validate(self, data):
        data = super().validate(data)
        user = data.get('user')
        if not isinstance(user, Driver):
            raise serializers.ValidationError("Invalid credentials for a driver.")
        return data


###############################################################################
# Common Serializers
###############################################################################

class EmailVerificationSerializer(serializers.Serializer):
    """
    Serializer for email verification.
    Expects an email and a 4-digit OTP.
    """
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=4)


class ResendOTPSerializer(serializers.Serializer):
    """
    Serializer for resending an OTP.
    Only requires the user's email.
    """
    email = serializers.EmailField()

