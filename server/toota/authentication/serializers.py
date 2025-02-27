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
        model = None  # To be specified in child serializers
        fields = ('email', 'password')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.Meta.model:
            self.fields['email'].validators = [
                UniqueValidator(queryset=self.Meta.model.objects.all(), message="This email is already in use.")
            ]

    def create(self, validated_data):
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

<<<<<<< HEAD
<<<<<<< HEAD
=======
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

>>>>>>> d5a8e94 (feat: finished trip implementation:)
=======
>>>>>>> 0a68f80 (add the trip and auth)
