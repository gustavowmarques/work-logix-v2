from django.db import models 
from django.conf import settings
from django.utils import timezone
from enum import Enum

from core.models.client import Client
from core.models.company import Company
from core.models.business_type import BusinessType

# ---------------------------------------------------
# ENUM FOR STATUS – improves maintainability
# ---------------------------------------------------
class WorkOrderStatus(Enum):
    NEW = "New"
    ASSIGNED = "Assigned"
    ACCEPTED = "Accepted"
    COMPLETED = "Completed"
    REJECTED = "Rejected"
    RETURNED = "Returned to Creator"

# Convert Enum to Django-friendly choices
WORK_ORDER_STATUSES = [(status.name, status.value) for status in WorkOrderStatus]

# ---------------------------------------------------
# PRIORITY CHOICES
# ---------------------------------------------------
PRIORITY_CHOICES = [
    ('low', 'Low'),
    ('medium', 'Medium'),
    ('high', 'High'),
    ('critical', 'Critical'),
]

# ---------------------------------------------------
# WORK ORDER MODEL
# ---------------------------------------------------
class WorkOrder(models.Model):
    # ---------------------------
    # Core details
    # ---------------------------
    title = models.CharField(max_length=255)
    description = models.TextField()
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='medium',
    )
    status = models.CharField(
        max_length=50,
        choices=WORK_ORDER_STATUSES,
        default=WorkOrderStatus.NEW.name,   # or 'new' if you store the value
    )

    # ---------------------------
    # Related objects
    # ---------------------------
    client = models.ForeignKey(
        'core.Client',
        on_delete=models.CASCADE,
        null=True, blank=True,
    )

    # Only ONE definition for `unit` — nullable + PROTECT
    unit = models.ForeignKey(
        'core.Unit',
        on_delete=models.PROTECT,
        null=True, blank=True,
        related_name="work_orders",
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    business_type = models.ForeignKey(
       'core.BusinessType',
        on_delete=models.CASCADE,
        null=True, blank=True,
    )

    # Persist the “common area” choice
    is_common_area = models.BooleanField(default=False)

    # ---------------------------
    # Contractor assignments
    # ---------------------------
    preferred_contractor = models.ForeignKey(
        Company,
        related_name='preferred_orders',
        on_delete=models.SET_NULL,
        null=True, blank=True,
    )
    second_contractor = models.ForeignKey(
        Company,
        related_name='second_orders',
        on_delete=models.SET_NULL,
        null=True, blank=True,
    )
    assigned_contractor = models.ForeignKey(
        Company,
        related_name='assigned_orders',
        on_delete=models.SET_NULL,
        null=True, blank=True,
    )

    # ---------------------------
    # Workflow state fields
    # ---------------------------
    accepted_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    completion_notes = models.TextField(blank=True, null=True)
    attachment = models.FileField(upload_to='workorder_attachments/', null=True, blank=True)

    # Track rejection logic
    rejected_by_first = models.BooleanField(default=False)
    rejected_by_second = models.BooleanField(default=False)
    returned_to_creator = models.BooleanField(default=False)

    # ---------------------------
    # Time tracking
    # ---------------------------
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
