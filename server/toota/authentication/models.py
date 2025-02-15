from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import uuid
from cloudinary.models import CloudinaryField
from phonenumber_field.modelfields import PhoneNumberField  # Requires django-phonenumber-field

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
    profile_pic = CloudinaryField('image', blank=True, null=True)
    phone_number = PhoneNumberField(blank=True, null=True)
    physical_address = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=False)  # Requires verification
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_superuser = models.BooleanField(default=False) # added for superuser

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        abstract = True

###############################################################################
# User Model
###############################################################################
class User(AbstractCustomUser):
    """
    User model that extends the abstract custom user with client-specific fields.
    """
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='users',
        blank=True,
        help_text=_('The groups this user belongs to.'),
        verbose_name=_('groups')
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='user_permissions',
        blank=True,
        help_text=_('Specific permissions for this user.'),
        verbose_name=_('user permissions')
    )

    objects = BaseCustomUserManager()

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
    current_location = models.CharField(max_length=255, blank=True, null=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    total_trips_completed = models.PositiveIntegerField(default=0)
    earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_available=models.BooleanField(default=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='driver_users',
        blank=True,
        help_text=_('The groups this driver belongs to.'),
        verbose_name=_('groups')
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='driver_user_permissions',
        blank=True,
        help_text=_('Specific permissions for this driver.'),
        verbose_name=_('user permissions')
    )

    objects = BaseCustomUserManager()

    def __str__(self):
        return f"{self.email} - {self.vehicle_type or 'No Vehicle Data'}"

###############################################################################
# OTP Model: For handling email verification (shared by Users and Drivers)
###############################################################################
class OTP(models.Model):
    """
    Model to handle email verification via a 4-digit OTP code.
    The OTP is valid for 60 minutes.
    This model supports both client users and drivers by allowing only one of the
    relationships to be set.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='otp', null=True, blank=True)
    driver = models.OneToOneField(Driver, on_delete=models.CASCADE, related_name='otp', null=True, blank=True)
    code = models.CharField(max_length=4)  # 4-digit OTP code
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        if self.user:
            return f"OTP for {self.user.email}"
        elif self.driver:
            return f"OTP for {self.driver.email}"
        else:
            return "Unassigned OTP"

    def is_expired(self):
        """
        Checks if the OTP has expired (after 60 minutes).
        """
        expiration_time = timezone.now() - timezone.timedelta(minutes=60)
        return self.created_at < expiration_time

