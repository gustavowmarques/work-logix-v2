from django.contrib.auth.models import AbstractUser
from django.db import models

ROLE_CHOICES = [
    ('admin', 'Admin'),
    ('property_manager', 'Property Manager'),
    ('contractor', 'Contractor'),
    ('assistant', 'Assistant'),
]

class CustomUser(AbstractUser):
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    company = models.ForeignKey('core.Company', on_delete=models.SET_NULL, null=True, blank=True, related_name='users')

    def __str__(self):
        return f"{self.username} ({self.role})"
