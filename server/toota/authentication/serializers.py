from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from phonenumber_field.serializerfields import PhoneNumberField
from .models import User, Driver
from cloudinary.uploader import upload


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

        # Dynamically set the UniqueValidator based on the model in Meta.
        if self.Meta.model:
            self.fields['email'].validators = [
                UniqueValidator(queryset=self.Meta.model.objects.all(), message="This email is already in use.")
            ]

    def create(self, validated_data):
        # Delegate creation to the model's custom manager's create_user method.
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
    Validates that the authenticated user is a User instance.
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
        # The PhoneNumberField does its own validation; you can add additional checks if desired.
        if len(str(value)) < 10 or len(str(value)) > 15:
            raise serializers.ValidationError("Phone number must be between 10 and 15 digits.")
        return value

    def validate_profile_pic(self, value):
        # Limit profile picture size to 2 MB and ensure it's JPEG or PNG.
        max_size_mb = 2
        if value.size > max_size_mb * 1024 * 1024:
            raise serializers.ValidationError(f"Profile picture size must not exceed {max_size_mb} MB.")
        
        # Check file extension
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
    Only requires the users email.
    """
    email = serializers.EmailField()

class DriverKYCUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating KYC details for a driver.
    Validates first name, last name, physical address, phone number, profile picture,
    driver license, car images, vehicle registration number, vehicle type, and load capacity.
    """
    phone_number = PhoneNumberField(required=True)
    profile_pic = serializers.ImageField(required=True)  # Profile picture is now required
    license_image = serializers.ImageField(required=True, write_only=True, help_text="Upload a picture of your driver license.")
    car_images = serializers.ListField(
        child=serializers.ImageField(),
        min_length=2,
        max_length=2,
        required=True,
        help_text="Upload exactly 2 images of your vehicle."
    )
    vehicle_type = serializers.ChoiceField(choices=Driver.VEHICLE_CHOICES, required=True)
    vehicle_load_capacity = serializers.DecimalField(required=True, min_value=0.5, max_value=10.0, max_digits=5, decimal_places=2)

    class Meta:
        model = Driver
        fields = [
            'first_name',
            'last_name',
            'phone_number',
            'physical_address',
            'profile_pic',
            'license_image',
            'vehicle_registration',
            'car_images',
            'vehicle_type',
            'vehicle_load_capacity'
        ]

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
        if Driver.objects.filter(phone_number=value).exclude(id=self.instance.id if self.instance else None).exists():
            raise serializers.ValidationError("Phone number is already registered.")
        return value

    def validate_profile_pic(self, value):
        # Limit profile picture size to 2 MB and ensure it's JPEG or PNG
        max_size_mb = 2
        if value.size > max_size_mb * 1024 * 1024:
            raise serializers.ValidationError(f"Profile picture size must not exceed {max_size_mb} MB.")
        
        # Check file extension
        allowed_extensions = ['jpg', 'jpeg', 'png']
        ext = value.name.split('.')[-1].lower()
        if ext not in allowed_extensions:
            raise serializers.ValidationError("Profile picture must be in JPEG or PNG format.")
        return value

    def validate_license_image(self, value):
        # Ensure the license image is an image file (JPEG or PNG)
        max_size_mb = 2  # Limit size to 2MB
        if value.size > max_size_mb * 1024 * 1024:
            raise serializers.ValidationError(f"License image must not exceed {max_size_mb} MB.")
        
        allowed_extensions = ['jpg', 'jpeg', 'png']
        ext = value.name.split('.')[-1].lower()
        if ext not in allowed_extensions:
            raise serializers.ValidationError("License image must be in JPEG or PNG format.")
        return value

    def validate_car_images(self, value):
        if len(value) != 2:
            raise serializers.ValidationError("Please upload exactly 2 car images.")
        for image in value:
            # Ensure car images are images and within the file size limit
            max_size_mb = 2  # Limit size to 2MB
            if image.size > max_size_mb * 1024 * 1024:
                raise serializers.ValidationError(f"Each car image must not exceed {max_size_mb} MB.")
            allowed_extensions = ['jpg', 'jpeg', 'png']
            ext = image.name.split('.')[-1].lower()
            if ext not in allowed_extensions:
                raise serializers.ValidationError("Car images must be in JPEG or PNG format.")
        return value

    def validate_vehicle_registration(self, value):
        if not value.strip():
            raise serializers.ValidationError("Vehicle registration is required.")
        if Driver.objects.filter(vehicle_registration=value).exclude(id=self.instance.id if self.instance else None).exists():
            raise serializers.ValidationError("Vehicle registration already exists.")
        return value

    def validate_vehicle_type(self, value):
        allowed = [choice[0] for choice in Driver.VEHICLE_CHOICES]
        if value not in allowed:
            raise serializers.ValidationError(f"Vehicle type must be one of: {', '.join(allowed)}")
        return value

    def validate_vehicle_load_capacity(self, value):
        if not (0.5 <= value <= 10.0):
            raise serializers.ValidationError("Vehicle load capacity must be between 0.5 and 10 tons.")
        return value

    def update(self, instance, validated_data):
        # Handle the updating of car images and license image here
        car_images = validated_data.pop('car_images', None)
        license_image = validated_data.pop('license_image', None)
        
        # Update the fields that aren't related to file uploads
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # Handle uploading the license image to Cloudinary if provided
        if license_image:
            try:
                license_image_upload = upload(license_image)
                instance.license_image = license_image_upload['secure_url']  # Cloudinary URL of the uploaded image
            except Exception as e:
                raise serializers.ValidationError(f"Failed to upload license image: {str(e)}")
        
        # Handle uploading car images to Cloudinary if provided
        if car_images:
            uploaded_car_images = []
            for image in car_images:
                try:
                    uploaded_image = upload(image)
                    uploaded_car_images.append(uploaded_image['secure_url'])  # Cloudinary URL of the uploaded image
                except Exception as e:
                    raise serializers.ValidationError(f"Failed to upload car image: {str(e)}")
            instance.car_images = uploaded_car_images  # Assign the uploaded URLs to the car_images field

        # Save the instance
        instance.save()
        return instance

