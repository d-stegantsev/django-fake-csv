from celery import shared_task
from cloudinary_storage.storage import RawMediaCloudinaryStorage
from django.core.files.base import ContentFile

from schemas.models import Dataset
import csv
import io
from faker import Faker
from random import randint
from datetime import datetime, date
import logging

# Faker instance for generating fake data
faker = Faker()
logger = logging.getLogger(__name__)


@shared_task
def generate_csv_file(dataset_id):
    """
    Celery task to generate a CSV file with fake data for a given dataset.
    """
    try:
        dataset = Dataset.objects.get(pk=dataset_id)
        schema = dataset.schema
        columns = schema.columns.order_by("order")

        # Create an in-memory string buffer for the CSV data
        csv_buffer = io.StringIO()
        writer = csv.writer(csv_buffer, delimiter=schema.column_separator)

        # Write the header row (column names)
        writer.writerow([col.name for col in columns])

        # Write the data rows
        for _ in range(dataset.row_count):
            row = []
            for col in columns:
                value = fake_value_for_column(col)  # Generate value for each column
                row.append(value)
            writer.writerow(row)

        # Save the generated CSV as a file on the dataset
        file_name = f"dataset_{dataset.pk}.csv"
        content = ContentFile(csv_buffer.getvalue().encode("utf-8"))

        storage = RawMediaCloudinaryStorage()
        cloud_name = storage.save(f"csv/{file_name}", content)

        dataset.file.name = cloud_name
        dataset.status = Dataset.Status.READY
        dataset.save()

        logger.info("Storage used: %s", storage.__class__.__name__)
        logger.info("Saved name: %s", dataset.file.name)
        logger.info("Public URL: %s", storage.url(dataset.file.name))
        logger.info("Dataset.file.url: %s", dataset.file.url)

    except Exception as e:
        # If an error occurs, mark dataset as error and store the error message
        dataset = Dataset.objects.get(pk=dataset_id)
        dataset.status = Dataset.Status.ERROR
        dataset.error_message = str(e)
        dataset.save()


def parse_date(date_str):
    """
        Convert a string or date object to a Python date object.

        Accepts either a string in the format 'DD.MM.YYYY' or 'YYYY-MM-DD',
        or an already existing datetime.date object. Returns a datetime.date object
        suitable for use in faker date functions.

        Args:
            date_str (str or date): The input date as a string or date object.

        Returns:
            date: The parsed date as a datetime.date object.

        Raises:
            ValueError: If the input cannot be parsed as a date.
        """
    if isinstance(date_str, date):
        return date_str
    for fmt in ("%d.%m.%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(date_str, fmt).date()
        except (ValueError, TypeError):
            continue
    raise ValueError(f"Can't parse date string `{date_str}`")


def fake_value_for_column(col):
    """
    Generate a fake value for a schema column based on its type and parameters.
    """

    # Fake full name
    if col.type == "full_name":
        return faker.name()

    # Fake job title
    if col.type == "job":
        return faker.job()

    # Fake email address
    if col.type == "email":
        return faker.email()

    # Fake domain name
    if col.type == "domain_name":
        return faker.domain_name()

    # Fake phone number
    if col.type == "phone_number":
        return faker.phone_number()

    # Fake company name
    if col.type == "company_name":
        return faker.company()

    # Fake random text with configurable length
    if col.type == "text":
        min_length = col.params.get("min_length", 10)
        max_length = col.params.get("max_length", 50)
        txt = faker.text(max_nb_chars=max_length)
        # If too short, append more text
        if len(txt) < min_length:
            txt += " " + faker.text(max_nb_chars=(min_length - len(txt)))
        return txt[:max_length]

    # Fake random integer within a range
    if col.type == "integer":
        min_val = col.params.get("min", 0)
        max_val = col.params.get("max", 100)
        return randint(min_val, max_val)

    # Fake address (single line)
    if col.type == "address":
        return faker.address().replace("\n", ", ")

    # Fake date within a specified range
    if col.type == "date":
        start_date_raw = col.params.get("start_date", "-30y")
        end_date_raw = col.params.get("end_date", "today")
        if isinstance(start_date_raw, str) and (start_date_raw.startswith("-") or start_date_raw == "today"):
            start_date = start_date_raw
        else:
            start_date = parse_date(start_date_raw)
        if isinstance(end_date_raw, str) and (end_date_raw.startswith("-") or end_date_raw == "today"):
            end_date = end_date_raw
        else:
            end_date = parse_date(end_date_raw)
        return faker.date_between(start_date=start_date, end_date=end_date)

    # Default: return empty string for unknown type
    return ""
