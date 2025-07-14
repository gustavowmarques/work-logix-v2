from django.db import models

class Company(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField(blank=True, null=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    website = models.URLField(blank=True, null=True)

    is_contractor = models.BooleanField(default=False)
    is_client = models.BooleanField(default=False)
    is_property_manager = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Companies"

    def __str__(self):
        return self.name
