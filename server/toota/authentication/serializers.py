from rest_framework import serializers
from django.contrib.auth import authenticate
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .models import User, OTP
from .utils import generate_otp, send_otp_email
from django.utils import timezone
from datetime import timedelta


class UserSignupSerializer(serializers.ModelSerializer):
    """
    Serializer for user signup. Handles email and password validation.
    """
    password = serializers.CharField(write_only=True, min_length=8, max_length=128)

    class Meta:
        model = User
        fields = ['email', 'password']

    def validate_email(self, value):
        """
        Validate that the email is properly formatted and not already registered.
        """
        validate_email(value)  # Checks if the email is valid.
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already in use.")
        return value

    def validate_password(self, value):
        """
        Validate that the password meets security requirements.
        """
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        if not any(char.isdigit() for char in value):
            raise serializers.ValidationError("Password must contain at least one digit.")
        if not any(char.isalpha() for char in value):
            raise serializers.ValidationError("Password must contain at least one letter.")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(email=validated_data['email'], password=validated_data['password'])
        otp_code = generate_otp()
        OTP.objects.create(user=user, code=otp_code)
        send_otp_email(user.email, otp_code)
        return user

class EmailVerificationSerializer(serializers.Serializer):
    """
    Serializer for verifying email with OTP.
    """
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=4)

    def validate(self, data):
        try:
            user = User.objects.get(email=data['email'])
            otp = OTP.objects.get(user=user, code=data['otp'])
            if otp.is_expired():
                raise serializers.ValidationError("OTP has expired.")
            if otp.is_verified:
                raise serializers.ValidationError("OTP is already verified.")
        except (User.DoesNotExist, OTP.DoesNotExist):
            raise serializers.ValidationError("Invalid email or OTP.")
        return data

    def save(self):
        user = User.objects.get(email=self.validated_data['email'])
        otp = OTP.objects.get(user=user, code=self.validated_data['otp'])
        otp.is_verified = True
        otp.save()
        user.is_active = True  # Activate user after email verification
        user.save()

class ResendOTPSerializer(serializers.Serializer):
    """
    Serializer for resending OTP.
    """
    email = serializers.EmailField()

    def validate_email(self, value):
        """
        Ensure the email exists and belongs to an inactive user.
        """
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("No user found with this email address.")

        if user.is_active:
            raise serializers.ValidationError("This account is already verified.")

        return value

    def save(self):
        """
        Generate and send a new OTP if allowed.
        """
        email = self.validated_data['email']
        user = User.objects.get(email=email)

        # Check if an OTP exists and was recently sent
        otp, created = OTP.objects.get_or_create(user=user)
        if not created:
            last_sent_time = otp.created_at
            if timezone.now() - last_sent_time < timedelta(minutes=1):  # Prevent frequent resends
                raise serializers.ValidationError("You can request a new OTP after 1 minute.")

        # Generate and send a new OTP
        otp.code = generate_otp()
        otp.created_at = timezone.now()
        otp.is_verified = False  # Mark as not verified
        otp.save()
        send_otp_email(user.email, otp.code)  # Utilize email utility
        return user

class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user login. Returns an authentication token.
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(email=data['email'], password=data['password'])
        if not user:
            raise serializers.ValidationError("Invalid email or password.")
        if not user.is_active:
            raise serializers.ValidationError("Email is not verified.")
        return {'user': user}



class KYCSerializer(serializers.ModelSerializer):
    """
    Serializer for updating KYC details, including optional profile picture validation.
    """
    profile_pic = serializers.ImageField(required=False)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'physical_address', 'profile_pic']

    def validate_first_name(self, value):
        """
        Validate that the first name contains only letters.
        """
        if not value.isalpha():
            raise serializers.ValidationError("First name should contain only letters.")
        return value

    def validate_last_name(self, value):
        """
        Validate that the last name contains only letters.
        """
        if not value.isalpha():
            raise serializers.ValidationError("Last name should contain only letters.")
        return value

    def validate_physical_address(self, value):
        """
        Validate that the physical address is sufficiently descriptive.
        """
        if len(value) < 10:
            raise serializers.ValidationError("Physical address must be at least 10 characters long.")
        if not any(char.isdigit() for char in value):
            raise serializers.ValidationError("Physical address must contain at least one number.")
        if not any(char.isalpha() for char in value):
            raise serializers.ValidationError("Physical address must contain at least one letter.")
        return value

    def validate_profile_pic(self, value):
        """
        Validate that the profile picture file size does not exceed 2 MB.
        """
        max_size_mb = 2  # Maximum file size in MB
        max_size_bytes = max_size_mb * 1024 * 1024  # Convert MB to bytes

        if value.size > max_size_bytes:
            raise serializers.ValidationError(f"Profile picture size should not exceed {max_size_mb} MB.")
        return value

