from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import uuid
from cloudinary.models import CloudinaryField
from django.contrib.postgres.fields import ArrayField
from phonenumber_field.modelfields import PhoneNumberField
from django.core.exceptions import ValidationError

###############################################################################
# Base Manager
###############################################################################
class BaseCustomUserManager(BaseUserManager):
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError(_("The Email field must be set"))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_active', False)
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
# Abstract Base User
###############################################################################
class AbstractCustomUser(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    email = models.EmailField(unique=True, max_length=255)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    profile_pic = CloudinaryField('image')
    phone_number = PhoneNumberField(unique=True)
    physical_address = models.TextField()
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        abstract = True

###############################################################################
# User Model
###############################################################################
class User(AbstractCustomUser):
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='users',
        blank=True,
        verbose_name=_('groups'),
        help_text=_('The groups this user belongs to.')
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='user_permissions',
        blank=True,
        verbose_name=_('user permissions'),
        help_text=_('Specific permissions for this user.')
    )

    objects = BaseCustomUserManager()

    def __str__(self):
        return self.email

###############################################################################
# Driver Model
###############################################################################
class Driver(AbstractCustomUser):
    license_number = models.CharField(max_length=50, unique=True)
    license_expiry = models.DateField()
    VEHICLE_CHOICES = [
        ('MotorBike', 'MotorBike'),
        ('1 ton Truck', '1 ton Truck'),
        ('1.5 ton Truck', '1.5 ton Truck'),
        ('2 ton Truck', '2 ton Truck'),
        ('4 ton Truck', '4 ton Truck'),
        ('Bakkie', 'Bakkie'),
        ('8 ton Truck', '8 ton Truck'),
    ]
    vehicle_type = models.CharField(max_length=50, choices=VEHICLE_CHOICES)
    vehicle_registration = models.CharField(max_length=50, unique=True)
    car_images = models.JSONField(default=list) 
    license_image = CloudinaryField('image', null=True, blank=True) 
    number_plate = models.CharField(max_length=50, unique=True)
    vehicle_load_capacity = models.DecimalField(max_digits=4, decimal_places=1, help_text="Capacity in tons (e.g., 1.5)")
    current_location = models.CharField(max_length=255, blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    is_available = models.BooleanField(default=True)
    total_trips_completed = models.PositiveIntegerField(default=0)
    earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_verified_by_admin = models.BooleanField(default=False)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='driver_users',
        blank=True,
        verbose_name=_('groups'),
        help_text=_('The groups this driver belongs to.')
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='driver_user_permissions',
        blank=True,
        verbose_name=_('user permissions'),
        help_text=_('Specific permissions for this driver.')
    )

    objects = BaseCustomUserManager()

    def __str__(self):
        return f"{self.email} - {self.vehicle_type}"

    def clean(self):
        super().clean()
        if self.license_expiry and self.license_expiry < timezone.now().date():
            raise ValidationError({'license_expiry': _("License expiry date must be in the future.")})
        if self.vehicle_load_capacity and not (0.5 <= self.vehicle_load_capacity <= 10.0):
            raise ValidationError({'vehicle_load_capacity': _("Vehicle load capacity must be between 0.5 and 10 tons.")})

###############################################################################
# OTP Model
###############################################################################
class OTP(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='otp', null=True, blank=True)
    driver = models.OneToOneField(Driver, on_delete=models.CASCADE, related_name='otp', null=True, blank=True)
    code = models.CharField(max_length=4)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        if self.user:
            return f"OTP for {self.user.email}"
        elif self.driver:
            return f"OTP for {self.driver.email}"
        return "Unassigned OTP"

    def is_expired(self):
        expiration_time = timezone.now() - timezone.timedelta(minutes=60)
        return self.created_at < expiration_time

