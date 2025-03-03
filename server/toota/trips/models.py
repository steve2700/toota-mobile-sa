from django.db import models
from django.core.validators import MinLengthValidator
import uuid
from django.contrib.auth import get_user_model

User = get_user_model()  # Get the user model dynamically
class Trip(models.Model):
    class StatusChoices(models.TextChoices):
        PENDING = "pending", "Pending"
        PICKEDUP = "picked up", "Picked up"
        PROGRESS = "in progress", "In Progress"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    # Pricing configurations
    VEHICLE_BASE_FARES = {
        '1 ton Truck': 100.0,
        '1.5 ton Truck': 120.0,
        '2 ton Truck': 150.0,
        '4 ton Truck': 200.0,
        'Bakkie': 80.0,
        '8 ton Truck': 300.0,
        'Motorbike': 50.0,
    }
    COST_PER_KM = 10.0
    COST_PER_MINUTE = 2.0
    SURGE_MULTIPLIER = 1.5  # Example surge multiplier

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey("authentication.User", on_delete=models.CASCADE)
    driver = models.ForeignKey("authentication.Driver", on_delete=models.SET_NULL, null=True, blank=True)
    pickup_lat = models.FloatField(null=True, blank=True)
    pickup_long = models.FloatField(null=True, blank=True)
    dest_lat = models.FloatField(null=True, blank=True)
    dest_long = models.FloatField(null=True, blank=True)
    load_description = models.TextField(null=True, blank=True)
    accepted_fare = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    vehicle_type = models.CharField(
        choices=[
            ('1 ton Truck', '1 ton Truck'),
            ('1.5 ton Truck', '1.5 ton Truck'),
            ('2 ton Truck', '2 ton Truck'),
            ('4 ton Truck', '4 ton Truck'),
            ('Bakkie', 'Bakkie'),
            ('8 ton Truck', '8 ton Truck'),
            ('Motorbike', 'Motorbike'),
        ],
        max_length=20,
        null=True,
        blank=True
    )
    pickup = models.CharField(max_length=255, validators=[MinLengthValidator(3)])
    destination = models.CharField(max_length=255, validators=[MinLengthValidator(3)])
    status = models.CharField(
        choices=StatusChoices.choices, 
        default=StatusChoices.PENDING,
        max_length=20
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.pickup} to {self.destination} and status is {self.status}"

    def calculate_fare(self, distance_km, estimated_time_minutes, surge=False):
        """
        Calculate the total fare based on:
          - Base fare according to the vehicle type.
          - Cost per kilometer.
          - Cost per minute.
          - Optional surge pricing.
        """
        base_fare = self.VEHICLE_BASE_FARES.get(self.vehicle_type, 100.0)
        distance_cost = distance_km * self.COST_PER_KM
        time_cost = estimated_time_minutes * self.COST_PER_MINUTE
        total_fare = base_fare + distance_cost + time_cost
        
        if surge:
            total_fare *= self.SURGE_MULTIPLIER
        
        return round(total_fare, 2)



class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
    ]
    
    PAYMENT_METHODS = [
        ('card', 'Card'),
        ('mobile_money', 'Mobile Money'),
        ('bank_transfer', 'Bank Transfer'),
        ('cash', 'Cash'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="payments")  # Link to User
    trip_id = models.UUIDField()  # Reference to Trip
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # Ensure precision
    currency = models.CharField(max_length=3, default="NGN")  # Default to NGN
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    transaction_id = models.CharField(max_length=100, unique=True, blank=True, null=True)  # Flutterwave transaction ID
    payment_reference = models.CharField(max_length=100, blank=True, null=True)  # Any additional payment ref
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')  # Track payment status
    created_at = models.DateTimeField(auto_now_add=True)  # Auto timestamp when created
    updated_at = models.DateTimeField(auto_now=True)  # Auto update when modified

    class Meta:
        ordering = ['-created_at']  # Show latest payments first
        indexes = [
            models.Index(fields=['transaction_id']),
            models.Index(fields=['trip_id']),
        ]

    def __str__(self):
        return f"{self.user} - {self.amount} {self.currency} ({self.status})"

    def save(self, *args, **kwargs):
        """Ensure transaction_id is generated before saving."""
        if not self.transaction_id:
            self.transaction_id = str(uuid.uuid4())  # Generate unique transaction ID
        super().save(*args, **kwargs)

