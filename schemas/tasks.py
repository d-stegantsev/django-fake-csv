from celery import shared_task
from django.core.files.base import ContentFile
from schemas.models import Dataset
import csv
import io
from faker import Faker
from random import randint

# Faker instance for generating fake data
faker = Faker()


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
        dataset.file.save(file_name, ContentFile(csv_buffer.getvalue().encode("utf-8")))
        dataset.status = Dataset.Status.READY
        dataset.save()
    except Exception as e:
        # If an error occurs, mark dataset as error and store the error message
        dataset = Dataset.objects.get(pk=dataset_id)
        dataset.status = Dataset.Status.ERROR
        dataset.error_message = str(e)
        dataset.save()


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
        start_date = col.params.get("start_date", "-30y")
        end_date = col.params.get("end_date", "today")
        return faker.date_between(start_date=start_date, end_date=end_date)

    # Default: return empty string for unknown type
    return ""
