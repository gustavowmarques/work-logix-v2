from django.db import models

class Client(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    company = models.ForeignKey(
        'core.Company',
        on_delete=models.CASCADE,
        limit_choices_to={'is_property_manager': True},
        help_text="Select the PM agency managing this site."
    )
    notes = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Clients"

    def __str__(self):
        return self.name
