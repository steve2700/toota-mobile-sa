from django.db import models
import uuid
from django.contrib.auth import get_user_model

User = get_user_model()

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
    CURRENCY_CHOICES = [
        ('NGN', 'NGN'),
        ('KES', 'KES'),
        ('ZAR', 'ZAR'),
        ('GHS', 'GHS'),
    ]
    LOCATION_CHOICES = [
        ('South Africa', 'ZA'),
        ('Kenya', 'KE'),
        ('Ghana', 'GH'),
        ('Nigeria', 'NG'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey("authentication.User", on_delete=models.CASCADE, related_name="payments")  # Link to User
    driver = models.ForeignKey("authentication.Driver", on_delete=models.SET_NULL, null=True, blank=True, related_name="payments")
    trip_id = models.UUIDField()  # Reference to Trip
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    location = models.CharField(max_length=20, choices=LOCATION_CHOICES, default="South Africa")  # Location of payment
    currency = models.CharField(max_length=4, choices=CURRENCY_CHOICES)
    gateway = models.CharField(
        max_length=20,
        choices=[
            ('flutterwave', 'Flutterwave'),
            ('paystack', 'Paystack')
        ],
        null = True,
        blank = True
    )
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    transaction_id = models.CharField(max_length=100, unique=True, blank=True, null=True)
    payment_reference = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True)

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


