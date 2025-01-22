from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

VEHICLE_TYPES = [
    ('1_ton_truck', '1 Ton Truck'),
    ('2_ton_truck', '2 Ton Truck'),
    ('4_ton_truck', '4 Ton Truck'),
    ('8_ton_truck', '8 Ton Truck'),
    ('bakkie', 'Bakkie'),
    ('motorbike', 'Motorbike'),
    ('pickup', 'Pickup Truck'),
    ('minivan', 'Minivan'),
]

class Trip(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trips', help_text="User creating the trip")
    driver = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='assigned_trips', null=True, blank=True, help_text="Driver assigned to the trip")
    pickup_location = models.CharField(max_length=255, help_text="Exact address for pickup")
    dropoff_location = models.CharField(max_length=255, help_text="Exact address for dropoff")
    load_description = models.TextField(help_text="Description of the load or cargo")
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPES, help_text="Preferred vehicle type")
    bid_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Amount bid by the user")
    suggested_fare = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="System-generated suggested fare")
    distance_in_km = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Calculated distance in kilometers")
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], default='pending', help_text="Current status of the trip")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Trip from {self.pickup_location} to {self.dropoff_location} - {self.vehicle_type}"

class Vehicle(models.Model):
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPES, unique=True, help_text="Type of vehicle")
    base_rate_per_km = models.DecimalField(max_digits=6, decimal_places=2, help_text="Base rate per kilometer for this vehicle type")
    capacity_in_tons = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, help_text="Load capacity in tons")

    def __str__(self):
        return f"{self.vehicle_type} - {self.capacity_in_tons} tons"

class DriverProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='driver_profile')
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPES, help_text="Type of vehicle the driver operates")
    current_location = models.CharField(max_length=255, null=True, blank=True, help_text="Current location of the driver")
    is_available = models.BooleanField(default=True, help_text="Whether the driver is available for trips")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} - {self.vehicle_type}"
