from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import uuid

# User Manager
class UserManager(BaseUserManager):
    """Custom user manager for clients."""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_("The Email field must be set"))
        email = self.normalize_email(email)
        extra_fields.setdefault('is_active', False)  # User must verify email
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))

        return self.create_user(email, password, **extra_fields)

# Client User Model
class User(AbstractBaseUser):
    """Custom user model for clients."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, max_length=255)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    physical_address = models.TextField(blank=True, null=True)
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    is_active = models.BooleanField(default=False)  # Email verification required
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_superuser = models.BooleanField(default=False) # added for superuser

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email

# Driver Manager
class DriverManager(BaseUserManager):
    """Custom user manager for drivers."""

    def create_driver(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_("The Email field must be set"))
        email = self.normalize_email(email)
        extra_fields.setdefault('is_active', False)  # Driver must be verified
        driver = self.model(email=email, **extra_fields)
        driver.set_password(password)
        driver.save(using=self._db)
        return driver

# Driver Model
class Driver(AbstractBaseUser):
    """Custom user model for drivers."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, max_length=255)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    # license_number = models.CharField(max_length=50, unique=True)
    # license_expiry = models.DateField()
    vehicle_type = models.CharField(
        max_length=50,
        choices=[
            ('1 ton Truck', '1 ton Truck'),
            ('1.5 ton Truck', '1.5 ton Truck'),
            ('2 ton Truck', '2 ton Truck'),
            ('4 ton Truck', '4 ton Truck'),
            ('Bakkie', 'Bakkie'),
            ('8 ton Truck', '8 ton Truck'),
        ]
    )
    # vehicle_registration = models.CharField(max_length=50, unique=True)
    car_images = models.ImageField(upload_to='driver_car_images/', blank=True, null=True)
    # number_plate = models.CharField(max_length=50, unique=True)  # Ensuring it's unique
    profile_pic = models.ImageField(upload_to='driver_profile_pics/', blank=True, null=True)
    is_active = models.BooleanField(default=False)  # Must be vetted
    is_staff = models.BooleanField(default=False)
    current_location = models.CharField(max_length=255, blank=True, null=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    total_trips_completed = models.PositiveIntegerField(default=0)
    earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_available=models.BooleanField(default=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = DriverManager()

    def __str__(self):
        return f"{self.email} - {self.vehicle_type}"

# OTP Model
class OTP(models.Model):
    """Model to handle email verification via OTP."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='otp')
    code = models.CharField(max_length=4)  # 4-digit OTP code
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"OTP for {self.user.email}"

    def is_expired(self):
        """Check if the OTP is expired (e.g., after 1 hour)."""
        expiration_time = timezone.now() - timezone.timedelta(hours=1)
        return self.created_at < expiration_time

