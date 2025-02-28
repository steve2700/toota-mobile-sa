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

