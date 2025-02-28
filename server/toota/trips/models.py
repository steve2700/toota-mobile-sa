from django.db import models
from django.core.validators import MinLengthValidator
import uuid

class Trip(models.Model):
    class StatusChoices(models.TextChoices):
        PENDING = "pending", "Pending"
        PICKEDUP = "picked up", "Picked up"
        PROGRESS = "in progress", "In Progress"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

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
        ],
        null=True,
        blank=True
    )
    pickup = models.CharField(max_length=255, validators=[MinLengthValidator(3)])
    destination =models.CharField(max_length=255, validators=[MinLengthValidator(3)])
    status = models.CharField(
        choices=StatusChoices.choices, 
        default=StatusChoices.PENDING  # Set a default value
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.pickup} to {self.destination} and status is {self.status}"

import uuid
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()  # Get the user model dynamically

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

