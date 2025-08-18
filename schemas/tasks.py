from celery import shared_task
from django.core.files.base import ContentFile
from typing import Union, Any, Optional, Dict, Callable

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


def fake_text(col: "SchemaColumn") -> str:
    # Generate random text with configurable min/max length
    min_length = col.params.get("min_length", 10)
    max_length = col.params.get("max_length", 50)
    txt = faker.text(max_nb_chars=max_length)
    if len(txt) < min_length:
        # Ensure at least 5 characters for Faker and non-negative
        remaining = max(min_length - len(txt), 5)
        txt += " " + faker.text(max_nb_chars=remaining)
    return txt[:max_length]


def fake_integer(col: "SchemaColumn") -> int:
    # Generate random integer within min/max range from params
    min_val = col.params.get("min", 0)
    max_val = col.params.get("max", 100)
    return randint(min_val, max_val)


def fake_date(col: "SchemaColumn") -> str:
    # Generate a date between start_date and end_date from params
    params: Optional[Dict[str, Any]] = col.params
    start_date_raw = params.get("start_date") if params else None
    end_date_raw = params.get("end_date") if params else None

    # Safely parse strings to date objects
    start_parsed = dateparser.parse(start_date_raw) if start_date_raw else None
    end_parsed = dateparser.parse(end_date_raw) if end_date_raw else None
    start_date = start_parsed.date() if start_parsed else None
    end_date = end_parsed.date() if end_parsed else None

    # Return as string for CSV compatibility
    return faker.date_between(start_date=start_date, end_date=end_date).isoformat()


# Mapper: type -> generator function
FAKE_GENERATORS: Dict[str, Callable[["SchemaColumn"], Any]] = {
    "full_name": lambda col: faker.name(),
    "job": lambda col: faker.job(),
    "email": lambda col: faker.email(),
    "domain_name": lambda col: faker.domain_name(),
    "phone_number": lambda col: faker.phone_number(),
    "company_name": lambda col: faker.company(),
    "address": lambda col: faker.address().replace("\n", ", "),
    "text": fake_text,
    "integer": fake_integer,
    "date": fake_date,
}


def fake_value_for_column(col: "SchemaColumn") -> Any:
    generator = FAKE_GENERATORS.get(col.type)
    return generator(col) if generator else ""
