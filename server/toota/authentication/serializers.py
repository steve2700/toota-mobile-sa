from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from phonenumber_field.serializerfields import PhoneNumberField
from .models import User, Driver

###############################################################################
# Base Serializers
###############################################################################

class BaseSignupSerializer(serializers.ModelSerializer):
    """
    Base serializer for signup operations.
    Expects inheriting serializers to specify the model and fields.
    """
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        validators=[validate_password]
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'physical_address', 'phone_number', 'profile_pic']

    def validate_first_name(self, value):
        if not value.isalpha():
            raise serializers.ValidationError("First name must contain only alphabetic characters.")
        return value

    def validate_last_name(self, value):
        if not value.isalpha():
            raise serializers.ValidationError("Last name must contain only alphabetic characters.")
        return value

    def validate_physical_address(self, value):
        if not value.strip():
            raise serializers.ValidationError("Physical address cannot be empty.")
        return value

    def validate_phone_number(self, value):
        if len(str(value)) < 10 or len(str(value)) > 15:
            raise serializers.ValidationError("Phone number must be between 10 and 15 digits.")
        return value

    def validate_profile_pic(self, value):
        max_size_mb = 2
        if value.size > max_size_mb * 1024 * 1024:
            raise serializers.ValidationError(f"Profile picture size must not exceed {max_size_mb} MB.")
        allowed_extensions = ['jpg', 'jpeg', 'png']
        ext = value.name.split('.')[-1].lower()
        if ext not in allowed_extensions:
            raise serializers.ValidationError("Profile picture must be in JPEG or PNG format.")
        return value
        model = None  # To be specified in child serializers
        fields = ('email', 'password')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.Meta.model:
            self.fields['email'].validators = [
                UniqueValidator(queryset=self.Meta.model.objects.all(), message="This email is already in use.")
            ]

class BaseLoginSerializer(serializers.Serializer):
    """
    Serializer for email verification.
    Expects an email and a 4-digit OTP.
    Base serializer for login operations.
    Validates email and password, returning the authenticated user.
    """
    email = serializers.EmailField()
    password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )


###############################################################################
# Driver Serializers (for completeness)
###############################################################################

class DriverSignupSerializer(BaseSignupSerializer):
    """
    Serializer for driver signup.
    For drivers, only email and password are required.
    """
    class Meta(BaseSignupSerializer.Meta):
        model = Driver
        fields = ('email', 'password')

class DriverLoginSerializer(BaseLoginSerializer):
    """
    Serializer for driver login.
    Validates that the authenticated user is a Driver instance.
    """
    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        try:
            driver = Driver.objects.get(email=email)
        except Driver.DoesNotExist:
            raise serializers.ValidationError("Invalid credentials for a driver.")
        if not driver.check_password(password):
            raise serializers.ValidationError("Invalid credentials for a driver.")
        data['user'] = driver
        return data

class EmailVerificationSerializer(serializers.Serializer):
    def create(self, validated_data):
        return self.Meta.model.objects.create_user(**validated_data)


class ResendOTPSerializer(serializers.Serializer):
    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        user = authenticate(request=self.context.get('request'), email=email, password=password)
        if not user:
            raise serializers.ValidationError("Unable to log in with provided credentials.")
        data['user'] = user
        return data

###############################################################################
# User Serializers (Signup/Login/Profile)
###############################################################################

class UserSignupSerializer(BaseSignupSerializer):
    """
    Serializer for client user signup.
    Only includes email and password; additional fields are handled during KYC.
    """
    class Meta(BaseSignupSerializer.Meta):
        model = User
        fields = BaseSignupSerializer.Meta.fields

class UserLoginSerializer(BaseLoginSerializer):
    """
    Serializer for user login.
    Validates email and password directly against the User model.
    """
    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid credentials for a user.")
        if not user.check_password(password):
            raise serializers.ValidationError("Invalid credentials for a user.")
        if not user.is_active:
            raise serializers.ValidationError("Account not verified.")
        data['user'] = user
        return data

class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for retrieving and updating client user profiles.
    The email field is read-only.
    """
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'physical_address', 'phone_number', 'profile_pic')
        read_only_fields = ('email',)

###############################################################################
# KYC Update Serializer
###############################################################################

class KYCUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating KYC details for a user.
    Validates first name, last name, physical address, phone number, and profile picture.
    """
    phone_number = PhoneNumberField(required=True)
    profile_pic = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'physical_address', 'phone_number', 'profile_pic']

    def validate_first_name(self, value):
        if not value.isalpha():
            raise serializers.ValidationError("First name must contain only alphabetic characters.")
        return value

    def validate_last_name(self, value):
        if not value.isalpha():
            raise serializers.ValidationError("Last name must contain only alphabetic characters.")
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
        if not value.strip():
            raise serializers.ValidationError("Physical address cannot be empty.")
        return value

    def validate_phone_number(self, value):
        if len(str(value)) < 10 or len(str(value)) > 15:
            raise serializers.ValidationError("Phone number must be between 10 and 15 digits.")
        return value

    def validate_profile_pic(self, value):
        max_size_mb = 2
        if value.size > max_size_mb * 1024 * 1024:
            raise serializers.ValidationError(f"Profile picture size must not exceed {max_size_mb} MB.")
        allowed_extensions = ['jpg', 'jpeg', 'png']
        ext = value.name.split('.')[-1].lower()
        if ext not in allowed_extensions:
            raise serializers.ValidationError("Profile picture must be in JPEG or PNG format.")
        return value

###############################################################################
# Driver Serializers (for completeness)
###############################################################################

class DriverSignupSerializer(BaseSignupSerializer):
    """
    Serializer for driver signup.
    For drivers, only email and password are required.
    """
    class Meta(BaseSignupSerializer.Meta):
        model = Driver
        fields = ('email', 'password')

class DriverLoginSerializer(BaseLoginSerializer):
    """
    Serializer for driver login.
    Validates that the authenticated user is a Driver instance.
    """
    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        try:
            driver = Driver.objects.get(email=email)
        except Driver.DoesNotExist:
            raise serializers.ValidationError("Invalid credentials for a driver.")
        if not driver.check_password(password):
            raise serializers.ValidationError("Invalid credentials for a driver.")
        data['user'] = driver
        return data

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
