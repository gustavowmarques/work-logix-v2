from django.db import models
from core.models.business_type import BusinessType


class Company(models.Model):
    # Basic company information
    name = models.CharField(max_length=255)
    address = models.TextField(blank=True, null=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    website = models.URLField(blank=True, null=True)

    # Flags for role/type
    is_contractor = models.BooleanField(default=False)
    is_client = models.BooleanField(default=False)
    is_property_manager = models.BooleanField(default=False)

    # Field for business type
    business_type = models.ForeignKey(
        BusinessType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='companies'
    )

    class Meta:
        verbose_name_plural = "Companies"

    def __str__(self):
        return self.name
