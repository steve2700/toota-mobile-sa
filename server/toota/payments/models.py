# payments/models.py

from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.utils import timezone

class PricingConfiguration(models.Model):
    """
    Stores pricing parameters for a specific vehicle type.
    These parameters are used to calculate trip fares.
    """
    VEHICLE_CHOICES = [
        ('motorbike', 'Motorbike'),
        ('bakkie', 'Bakkie'),
        ('1 ton Truck', '1 ton Truck'),
        ('1.5 ton Truck', '1.5 ton Truck'),
        ('2 ton Truck', '2 ton Truck'),
        ('4 ton Truck', '4 ton Truck'),
        ('8 ton Truck', '8 ton Truck'),
    ]
    vehicle_type = models.CharField(
        max_length=50,
        choices=VEHICLE_CHOICES,
        unique=True,
        help_text="Select the vehicle type."
    )
    base_fare = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Fixed starting price based on vehicle type."
    )
    cost_per_km = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Cost per kilometer."
    )
    cost_per_minute = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Cost per minute."
    )
    surge_multiplier = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=1.0,
        validators=[MinValueValidator(Decimal('1.0'))],
        help_text="Multiplier applied during peak hours or high demand."
    )

    def __str__(self):
        return f"Pricing for {self.vehicle_type}"

    def calculate_fare(self, distance_km, duration_minutes, apply_surge=False):
        """
        Calculate fare based on:
          - Base fare
          - Distance pricing (per kilometer)
          - Time-based pricing (per minute)
          - Surge pricing (if applicable)
        
        :param distance_km: Distance in kilometers (Decimal or float)
        :param duration_minutes: Duration in minutes (Decimal or float)
        :param apply_surge: Boolean indicating if surge pricing should be applied.
        :return: Total fare as Decimal
        """
        fare = self.base_fare + (self.cost_per_km * Decimal(distance_km)) + (self.cost_per_minute * Decimal(duration_minutes))
        if apply_surge:
            fare *= self.surge_multiplier
        return fare

class Trip(models.Model):
    """
    Represents a trip taken by a user.
    The fare is calculated using a PricingConfiguration.
    """
    user = models.ForeignKey('authentication.User', on_delete=models.CASCADE)
    driver = models.ForeignKey('authentication.Driver', on_delete=models.SET_NULL, null=True, blank=True)
    pricing_configuration = models.ForeignKey(PricingConfiguration, on_delete=models.CASCADE)
    distance_km = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Total distance of the trip in kilometers."
    )
    duration_minutes = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Total duration of the trip in minutes."
    )
    surge_active = models.BooleanField(default=False, help_text="Whether surge pricing applies.")
    fare = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Calculated fare for the trip.")
    created_at = models.DateTimeField(auto_now_add=True)

    def calculate_and_set_fare(self):
        """
        Calculate the fare using the pricing configuration and save it.
        """
        self.fare = self.pricing_configuration.calculate_fare(
            self.distance_km,
            self.duration_minutes,
            apply_surge=self.surge_active
        )
        self.save()

    def __str__(self):
        return f"Trip {self.id} for {self.user.email}"

