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
        extra_fields.setdefault('is_active', False)  # Email verification required
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
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    is_active = models.BooleanField(default=False)  # Email verification required
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

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
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    physical_address = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    license_number = models.CharField(max_length=50, unique=True)
    license_expiry = models.DateField()
    license_file = models.FileField(upload_to='driver_licenses/', blank=True, null=True)
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
    vehicle_load_capacity = models.CharField(
        max_length=50,
        choices=[
            ('500 kg', '500 kg'),
            ('1 ton', '1 ton'),
            ('2 tons', '2 tons'),
            ('5 tons', '5 tons'),
            ('10 tons', '10 tons'),
        ],
        blank=True,
        null=True
    )
    vehicle_registration = models.CharField(max_length=50, unique=True)
    car_images = models.ImageField(upload_to='driver_car_images/', blank=True, null=True)
    number_plate = models.CharField(max_length=50, unique=True)
    profile_pic = models.ImageField(upload_to='driver_profile_pics/', blank=True, null=True)
    current_location = models.CharField(max_length=255, blank=True, null=True)
    is_online = models.BooleanField(default=False)  # Track online status
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    total_trips_completed = models.PositiveIntegerField(default=0)
    earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_active = models.BooleanField(default=False)  # Must be vetted
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

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


class VerificationWarning(models.Model):
    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High')
    ]

    DECISION_CHOICES = [
        ('accept', 'Accept'),
        ('review', 'Review'),
        ('reject', 'Reject')
    ]

    code = models.CharField(max_length=50)
    description = models.TextField()
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES)
    confidence = models.FloatField()
    decision = models.CharField(max_length=10, choices=DECISION_CHOICES)
    category = models.CharField(max_length=50)
    additional_data = models.JSONField(null=True, blank=True)
    verification = models.ForeignKey('IDVerification', on_delete=models.CASCADE, related_name='warnings')
    

class IDVerification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='verifications',null=True)
    transaction_id = models.CharField(max_length=100)
    success = models.BooleanField(default=False)
    execution_time = models.FloatField()
    review_score = models.IntegerField()
    reject_score = models.IntegerField()
    decision = models.CharField(max_length=20)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    document_number = models.CharField(max_length=50)
    date_of_birth = models.DateField()
    sex = models.CharField(max_length=1)
    document_type = models.CharField(max_length=50)
    expiry_date = models.DateField()
    issue_date = models.DateField()
    height = models.CharField(max_length=20, null=True, blank=True)
    weight = models.CharField(max_length=20, null=True, blank=True)
    hair_color = models.CharField(max_length=20, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    is_expired = models.BooleanField(default=False)
    is_fake = models.BooleanField(default=False)
    image_edited = models.BooleanField(default=False)
    is_sanctioned = models.BooleanField(default=False)
    has_forgery = models.BooleanField(default=False)
    screen_detected = models.BooleanField(default=False)
    face_verification_failed = models.BooleanField(default=False)
    is_black_white = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def is_verified(self):
        """
        Returns True only if the API decision is 'accept' and there are no critical warnings
        """
        return (
            self.decision == 'accept' and
            not any([
                self.is_expired,
                self.is_fake,
                self.image_edited,
                self.is_sanctioned,
                self.has_forgery,
                self.screen_detected,
                self.face_verification_failed,
                self.is_black_white
            ])
        )

    @property
    def warning_summary(self):
        """
        Returns a summary of all active warnings
        """
        warnings = []
        if self.is_expired:
            warnings.append("Document is expired")
        if self.is_fake:
            warnings.append("Potentially fake document")
        if self.image_edited:
            warnings.append("Image was edited")
        if self.is_sanctioned:
            warnings.append("Found in sanctions database")
        if self.has_forgery:
            warnings.append("Possible forgery detected")
        if self.screen_detected:
            warnings.append("Screen capture detected")
        if self.face_verification_failed:
            warnings.append("Face verification failed")
        if self.is_black_white:
            warnings.append("Black and white copy")
        return ', '.join(warnings)
