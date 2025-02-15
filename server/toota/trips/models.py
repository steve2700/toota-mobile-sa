from django.db import models
from django.core.validators import MinLengthValidator
import uuid

class Trip(models.Model):
    class StatusChoices(models.TextChoices): 
        PENDING = "ongoing", "Ongoing"
        PROGRESS = "in_progress", "In Progress"
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


# Create your models here.
