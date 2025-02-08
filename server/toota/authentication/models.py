from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import uuid

###############################################################################
# Base Manager: Shared logic for creating users
###############################################################################
class BaseCustomUserManager(BaseUserManager):
    """
    Base manager for custom user models. It centralizes user creation logic,
    ensuring email normalization, password setting, and common validations.
    """
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError(_("The Email field must be set"))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_active', False)  # Require verification by default
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))

        return self._create_user(email, password, **extra_fields)

###############################################################################
# Abstract Base Model: Common fields for all user types
###############################################################################
class AbstractCustomUser(AbstractBaseUser, PermissionsMixin):
    """
    Abstract user model that holds fields and methods common to both clients and drivers.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, max_length=255)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    is_active = models.BooleanField(default=False)  # Requires verification
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        abstract = True

###############################################################################
# Client User Model
###############################################################################
class ClientUser(AbstractCustomUser):
    """
    Client user model that extends the abstract custom user with client-specific fields.
    """
    physical_address = models.TextField(blank=True, null=True)

    objects = BaseCustomUserManager()

    def __str__(self):
        return self.email

###############################################################################
# Driver Model
###############################################################################
class Driver(AbstractCustomUser):
    """
    Driver model that extends the abstract custom user with driver-specific fields.
    """
    license_number = models.CharField(max_length=50, unique=True)
    license_expiry = models.DateField()
    VEHICLE_CHOICES = [
        ('1 ton Truck', '1 ton Truck'),
        ('1.5 ton Truck', '1.5 ton Truck'),
        ('2 ton Truck', '2 ton Truck'),
        ('4 ton Truck', '4 ton Truck'),
        ('Bakkie', 'Bakkie'),
        ('8 ton Truck', '8 ton Truck'),
    ]
    vehicle_type = models.CharField(max_length=50, choices=VEHICLE_CHOICES)
    vehicle_registration = models.CharField(max_length=50, unique=True)
    car_images = models.ImageField(upload_to='driver_car_images/', blank=True, null=True)
    number_plate = models.CharField(max_length=50, unique=True)
    # Override profile_pic upload location for drivers
    profile_pic = models.ImageField(upload_to='driver_profile_pics/', blank=True, null=True)
    current_location = models.CharField(max_length=255, blank=True, null=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    total_trips_completed = models.PositiveIntegerField(default=0)
    earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    objects = BaseCustomUserManager()

    def __str__(self):
        return f"{self.email} - {self.vehicle_type}"

###############################################################################
# OTP Model: For handling email verification
###############################################################################
class OTP(models.Model):
    """
    Model to handle email verification via a 4-digit OTP code.
    """
    user = models.OneToOneField(ClientUser, on_delete=models.CASCADE, related_name='otp')
    code = models.CharField(max_length=4)  # 4-digit OTP code
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"OTP for {self.user.email}"

    def is_expired(self):
        """
        Checks if the OTP has expired (e.g., after 1 hour).
        """
        expiration_time = timezone.now() - timezone.timedelta(hours=1)
        return self.created_at < expiration_time

