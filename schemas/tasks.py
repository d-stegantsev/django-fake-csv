from celery import shared_task
from django.core.files.base import ContentFile
from schemas.models import Dataset
import csv
import io
from faker import Faker
from random import randint


faker = Faker()


@shared_task
def generate_csv_file(dataset_id):
    try:
        dataset = Dataset.objects.get(pk=dataset_id)
        schema = dataset.schema
        columns = schema.columns.order_by("order")

        # Generating CSV in memory
        csv_buffer = io.StringIO()
        writer = csv.writer(csv_buffer, delimiter=schema.column_separator)

        # Header
        writer.writerow([col.name for col in columns])

        # Body
        for _ in range(dataset.row_count):
            row = []
            for col in columns:
                value = fake_value_for_column(col)  # твоя функція для генерації фейкових значень
                row.append(value)
            writer.writerow(row)

        # Wright to file
        file_name = f"dataset_{dataset.pk}.csv"
        dataset.file.save(file_name, ContentFile(csv_buffer.getvalue().encode("utf-8")))
        dataset.status = Dataset.Status.READY
        dataset.save()
    except Exception as e:
        dataset = Dataset.objects.get(pk=dataset_id)
        dataset.status = Dataset.Status.ERROR
        dataset.error_message = str(e)
        dataset.save()


def fake_value_for_column(col):

    if col.type == "full_name":
        return faker.name()

    if col.type == "job":
        return faker.job()

    if col.type == "email":
        return faker.email()

    if col.type == "domain_name":
        return faker.domain_name()

    if col.type == "phone_number":
        return faker.phone_number()

    if col.type == "company_name":
        return faker.company()

    if col.type == "text":
        min_length = col.params.get("min_length", 10)
        max_length = col.params.get("max_length", 50)
        txt = faker.text(max_nb_chars=max_length)
        if len(txt) < min_length:
            txt += " " + faker.text(max_nb_chars=(min_length - len(txt)))
        return txt[:max_length]

    if col.type == "integer":
        min_val = col.params.get("min", 0)
        max_val = col.params.get("max", 100)
        return randint(min_val, max_val)

    if col.type == "address":
        return faker.address().replace("\n", ", ")

    if col.type == "date":
        start_date = col.params.get("start_date", "-30y")
        end_date = col.params.get("end_date", "today")
        return faker.date_between(start_date=start_date, end_date=end_date)

    return ""
