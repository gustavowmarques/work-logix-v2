from django.db import models
from django.conf import settings
from django.utils import timezone
from core.models.client import Client
from core.models.unit import Unit
from core.models.business_type import BusinessType
from core.models.company import Company

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

class WorkOrder(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')

    client = models.ForeignKey(Client, on_delete=models.CASCADE, null=True, blank=True)
    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    business_type = models.ForeignKey(BusinessType, on_delete=models.CASCADE, null=True, blank=True)

    preferred_contractor = models.ForeignKey(Company, related_name='preferred_orders', on_delete=models.SET_NULL, null=True, blank=True)
    second_contractor = models.ForeignKey(Company, related_name='second_orders', on_delete=models.SET_NULL, null=True, blank=True)
    assigned_contractor = models.ForeignKey(Company, related_name='assigned_orders', on_delete=models.SET_NULL, null=True, blank=True)

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
