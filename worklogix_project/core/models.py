from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.utils import timezone

# ----------------------------------------
# Constants
# ----------------------------------------

ROLE_CHOICES = [
    ('admin', 'Admin'),
    ('property_manager', 'Property Manager'),
    ('contractor', 'Contractor'),
    ('assistant', 'Assistant'),
]

PRIORITY_CHOICES = [
    ('low', 'Low'),
    ('medium', 'Medium'),
    ('high', 'High'),
    ('critical', 'Critical'),
]

STATUS_CHOICES = [
    ('new', 'New'),
    ('assigned', 'Assigned'),
    ('accepted', 'Accepted'),
    ('completed', 'Completed'),
    ('rejected', 'Rejected'),
    ('returned', 'Returned to Creator'),
]

# ----------------------------------------
# User Model
# ----------------------------------------

class CustomUser(AbstractUser):
    """
    Extends the default Django User model to include a role and optional company link.
    """
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    company = models.ForeignKey(
        'Company',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users'
    )

    def __str__(self):
        return f"{self.username} ({self.role})"

# ----------------------------------------
# Company Model
# ----------------------------------------

class Company(models.Model):
    """
    Represents a company in the system: Contractor, PM agency, or Client.
    """
    name = models.CharField(max_length=255)
    address = models.TextField(blank=True, null=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    website = models.URLField(blank=True, null=True)

    is_contractor = models.BooleanField(default=False, help_text="Mark as contractor company")
    is_client = models.BooleanField(default=False, help_text="Mark as a managed building")
    is_property_manager = models.BooleanField(default=False, help_text="Mark as property management agency")

    class Meta:
        verbose_name_plural = "Companies"

    def __str__(self):
        return self.name

# ----------------------------------------
# Client Model
# ----------------------------------------

class Client(models.Model):
    """
    Represents a managed property (site/building) linked to a PM agency.
    """
    name = models.CharField(max_length=255)
    address = models.TextField()
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        limit_choices_to={'is_property_manager': True},
        help_text="Select the PM agency managing this site.",
    )
    notes = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Clients"

    def __str__(self):
        return self.name
    
class Unit(models.Model):
    """
    Represents an individual unit (e.g., apartment or office) in a client building.
    """
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, help_text="E.g., A101, Penthouse, Apt 3B")

    def __str__(self):
        return f"{self.client.name} - {self.name}"


# ----------------------------------------
# Business Type Model
# ----------------------------------------

class BusinessType(models.Model):
    """
    Defines categories like Plumbing, Electrical, Pest Control, etc.
    """
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

# ----------------------------------------
# Work Order Model
# ----------------------------------------

class WorkOrder(models.Model):
    """
    Represents a maintenance or repair task.
    Routed to preferred/secondary contractors and tracks status lifecycle.
    """
    title = models.CharField(max_length=255)
    description = models.TextField()
    priority = models.CharField(
    max_length=20,
    choices=PRIORITY_CHOICES,
    default='medium'  # ✅ This avoids prompts and sets a sensible default
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')

    client = models.ForeignKey('Client', on_delete=models.CASCADE, null=True, blank=True)
    unit = models.ForeignKey('Unit', on_delete=models.SET_NULL, null=True, blank=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    business_type = models.ForeignKey(BusinessType, on_delete=models.CASCADE, null=True, blank=True)


    preferred_contractor = models.ForeignKey('Company', related_name='preferred_orders', on_delete=models.SET_NULL, null=True, blank=True)
    second_contractor = models.ForeignKey('Company', related_name='second_orders', on_delete=models.SET_NULL, null=True, blank=True)
    assigned_contractor = models.ForeignKey('Company', related_name='assigned_orders', on_delete=models.SET_NULL, null=True, blank=True)

    accepted_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    completion_notes = models.TextField(blank=True, null=True)
    attachment = models.FileField(upload_to='workorder_attachments/', null=True, blank=True)

    rejected_by_first = models.BooleanField(default=False)
    rejected_by_second = models.BooleanField(default=False)
    returned_to_creator = models.BooleanField(default=False)

    due_date = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
