from django.conf import settings
from django.db import models
from cloudinary_storage.storage import RawMediaCloudinaryStorage


class Schema(models.Model):
    """
    Represents a CSV schema definition.
    Stores user settings for CSV generation (column separator, string character, etc).
    """

    class ColumnSeparator(models.TextChoices):
        # Possible separators for columns in generated CSV files
        COMMA = ",", "Comma ( , )"
        SEMICOLON = ";", "Semicolon ( ; )"
        PIPE = "|", "Pipe ( | )"
        COLON = ":", "Colon ( : )"

    class StringCharacter(models.TextChoices):
        # Possible characters for quoting strings in CSV
        DOUBLE_QUOTE = '"', 'Double quote ( " )'
        SINGLE_QUOTE = "'", "Single quote ( ' )"
        BACKTICK = "`", "Backtick ( ` )"

    name = models.CharField(max_length=100)  # Schema name (displayed to the user)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="schemas"
    )  # Owner of the schema

    column_separator = models.CharField(
        max_length=10,
        choices=ColumnSeparator.choices,
        default=ColumnSeparator.COMMA,
    )  # Separator used in the generated CSV

    string_character = models.CharField(
        max_length=10,
        choices=StringCharacter.choices,
        default=StringCharacter.DOUBLE_QUOTE,
    )  # Character used for wrapping string values in CSV

    created_at = models.DateTimeField(auto_now_add=True)  # Creation timestamp
    updated_at = models.DateTimeField(auto_now=True)      # Last modification timestamp

    def __str__(self):
        return self.name


class SchemaColumn(models.Model):
    """
    Represents a column in a CSV schema.
    Stores the column's name, type, order, and additional parameters for data generation.
    """

    class Type(models.TextChoices):
        # Supported data types for columns (linked to fake data generation)
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

    schema = models.ForeignKey(
        Schema,
        on_delete=models.CASCADE,
        related_name="columns"
    )  # Link to the parent schema

    name = models.CharField(max_length=100)  # Column display name
    type = models.CharField(
        max_length=32,
        choices=Type.choices,
    )  # Column type (affects data generation)
    order = models.PositiveIntegerField()  # Order/position of the column in the CSV
    params = models.JSONField(default=dict, blank=True)  # Extra params for column type (range, length, etc.)

    def __str__(self):
        return self.name


class Dataset(models.Model):
    """
    Represents a generated dataset (CSV file) for a given schema.
    Stores generation settings, output file, and status.
    """

    class Status(models.TextChoices):
        # Status of the dataset generation process
        PROCESSING = "processing", "Processing"
        READY = "ready", "Ready"
        ERROR = "error", "Error"

    schema = models.ForeignKey(
        Schema,
        on_delete=models.CASCADE,
        related_name="datasets"
    )  # Link to parent schema

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="datasets"
    )  # User who requested/generates the dataset

    created_at = models.DateTimeField(auto_now_add=True)  # Dataset creation time
    row_count = models.PositiveIntegerField()             # Number of rows to generate

    status = models.CharField(
        max_length=32,
        choices=Status.choices,
        default=Status.PROCESSING,
    )  # Generation status (processing/ready/error)

    file = models.FileField(
        upload_to="csv/",
        storage=RawMediaCloudinaryStorage(),
        null=True,
        blank=True,
    )  # Generated CSV file
    error_message = models.TextField(blank=True, null=True)  # Error message if generation failed
