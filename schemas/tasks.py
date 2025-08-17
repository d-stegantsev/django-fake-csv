from celery import shared_task
from django.core.files.base import ContentFile
from typing import Union, Any, Optional, Dict

from schemas.models import Dataset, SchemaColumn
import csv
import io
from faker import Faker
from random import randint
from datetime import datetime, date
import dateparser

# Faker instance for generating fake data
faker = Faker()


@shared_task
def generate_csv_file(dataset_id: int) -> None:
    """
    Celery task to generate a CSV file with fake data for a given dataset.
    """
    try:
        dataset = Dataset.objects.get(pk=dataset_id)
        schema = dataset.schema
        columns = schema.columns.order_by("order")

        # Create an in-memory string buffer for the CSV data
        csv_buffer = io.StringIO()
        writer = csv.writer(
            csv_buffer,
            delimiter=schema.column_separator,
            quotechar=schema.string_character,
            quoting=csv.QUOTE_ALL,
        )

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
        dataset.file.save(file_name, ContentFile(csv_buffer.getvalue().encode("utf-8")))

        dataset.status = Dataset.Status.READY
        dataset.save()

    except Exception as e:
        # If an error occurs, mark dataset as error and store the error message
        dataset = Dataset.objects.get(pk=dataset_id)
        dataset.status = Dataset.Status.ERROR
        dataset.error_message = str(e)
        dataset.save()


def parse_date(date_str: Union[str, date]) -> Union[date, str]:
    """
    Convert a string or date object to a Python date object.
    If parsing fails, return an empty string.
    """
    if isinstance(date_str, date):
        return date_str

    if not isinstance(date_str, str):
        return ""

    for fmt in ("%d.%m.%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue

    # Default: return empty string for unknown type
    return ""


def fake_value_for_column(col: SchemaColumn) -> Any:
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
    params: Optional[Dict[str, Any]] = col.params

    if col.type == "date":
        start_date_raw = params.get("start_date") if params else None
        end_date_raw = params.get("end_date") if params else None

        # Parse safely
        start_parsed = dateparser.parse(start_date_raw) if start_date_raw else None
        end_parsed = dateparser.parse(end_date_raw) if end_date_raw else None

        start_date = start_parsed.date() if start_parsed else None
        end_date = end_parsed.date() if end_parsed else None

        return faker.date_between(start_date=start_date, end_date=end_date)

    # Default: return empty string for unknown type
    return ""
