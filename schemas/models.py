from django.conf import settings
from django.db import models


class Schema(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="schemas")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class SchemaColumn(models.Model):
    class Type(models.TextChoices):
        FULL_NAME = "full_name", "Full Name"
        JOB = "job", "Job"
        EMAIL = "email", "Email"
        DOMAIN_NAME = "domain_name", "Domain Name"
        PHONE_NUMBER = "phone_number", "Phone Number"
        COMPANY_NAME = "company_name", "Company Name"
        TEXT = "text", "Text"
        INTEGER = "integer", "Integer"
        ADDRESS = "address", "Address"
        DATE = "date", "Date"

    schema = models.ForeignKey(Schema, on_delete=models.CASCADE, related_name="columns")
    name = models.CharField(max_length=100)
    type = models.CharField(
        max_length=32,
        choices=Type.choices,
    )
    order = models.PositiveIntegerField()
    params = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return self.name


class Dataset(models.Model):
    class Status(models.TextChoices):
        PROCESSING = "processing", "Processing"
        READY = "ready", "Ready"
        ERROR = "error", "Error"

    schema = models.ForeignKey(Schema, on_delete=models.CASCADE, related_name="datasets")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="datasets")
    created_at = models.DateTimeField(auto_now_add=True)
    row_count = models.PositiveIntegerField()
    status = models.CharField(
        max_length=32,
        choices=Status.choices,
        default=Status.PROCESSING,
    )
    file = models. FileField(upload_to='csv/', null=True)
    error_message = models.TextField(blank=True, null=True)
