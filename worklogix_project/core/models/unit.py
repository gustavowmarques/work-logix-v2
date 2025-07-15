from django.db import models
from .client import Client
from .company import Company
from core.models.user import CustomUser

class UnitGroup(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='unit_groups')
    num_apartments = models.PositiveIntegerField(default=0)
    num_duplexes = models.PositiveIntegerField(default=0)
    num_houses = models.PositiveIntegerField(default=0)
    num_commercial_units = models.PositiveIntegerField(default=0)
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)

class Unit(models.Model):
    UNIT_TYPES = [
        ('apartment', 'Apartment'),
        ('duplex', 'Duplex'),
        ('house', 'House'),
        ('commercial', 'Commercial Unit'),
    ]

    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='units')
    name = models.CharField(max_length=100)
    unit_type = models.CharField(max_length=20, choices=UNIT_TYPES, default='apartment')
    group = models.ForeignKey(UnitGroup, on_delete=models.CASCADE, null=True, blank=True)
    eircode = models.CharField(max_length=10, blank=True, null=True)
    street = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    county = models.CharField(max_length=100, blank=True, null=True)


    def __str__(self):
        return f"{self.client.name} - {self.name}"
