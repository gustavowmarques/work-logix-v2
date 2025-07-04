from django.contrib.auth.models import AbstractUser
from django.db import models

# Custom user model extending Django's AbstractUser
class CustomUser(AbstractUser):
    # Define the available user roles for this system
    ROLE_CHOICES = [
        ('admin', 'Admin'),           # Superuser with full control
        ('pm', 'Property Manager'),   # Manages companies and work orders
        ('contractor', 'Contractor'), # Performs assigned work
        ('assistant', 'Assistant'),   # View-only role, can message PM/Admin
    ]

    # Role field to assign a type to each user
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    # Display user as "username (Role)" in the admin or elsewhere
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
