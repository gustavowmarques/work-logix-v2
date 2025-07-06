from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.utils import timezone

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
    role = models.CharField(max_length=20, choices=ROLE_CHOICES=[
        ('admin', 'Admin'),
        ('pm', 'Property Manager'),
        ('contractor', 'Contractor'),
        ('assistant', 'Assistant'),
    ])

    company = models.ForeignKey(
        Company,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Associate user with a company (e.g., PM agency or contractor)."
    )

    # Display user as "username (Role)" in the admin or elsewhere
    def __str__(self):
        return f"{self.username} ({self.role})"


class Company(models.Model):
    """
    Represents a company, which can be either:
    - A Property Manager Agency
    - A Contractor company
    """

    COMPANY_TYPES = [
        ('pm_agency', 'Property Manager Agency'),
        ('contractor', 'Contractor'),
    ]

    name = models.CharField(max_length=255)
    company_type = models.CharField(max_length=20, choices=COMPANY_TYPES)
    address = models.TextField(blank=True, null=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    website = models.URLField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Companies"

    def __str__(self):
        return self.name


class WorkOrder(models.Model):
    """
    Represents a maintenance task or request.
    Created by a property manager and optionally assigned to a contractor.
    """
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
        ('returned', 'Returned'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='workorders_created')
    assigned_contractor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_workorders')
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"

class Client(models.Model):
    """
    Represents a client site (e.g., a building or estate) that is managed
    by a Property Manager Agency (Company).
    """
    name = models.CharField(max_length=255)
    address = models.TextField()
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        limit_choices_to={'company_type': 'pm_agency'},
        help_text="Select the Property Manager Agency that manages this client site.",
    )
    notes = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Clients"

    def __str__(self):
        return self.name
