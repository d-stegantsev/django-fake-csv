from celery import shared_task
from django.core.files.base import ContentFile
from schemas.models import Dataset
import csv
import io


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
    # TODO: Implement data generation for all types
    if col.type == "full_name":
        from faker import Faker
        return Faker().name()
    if col.type == "email":
        from faker import Faker
        return Faker().email()
    if col.type == "text":
        from faker import Faker
        return Faker().text(max_nb_chars=col.params.get("max_length", 20))
    # ... інші типи ...
    return ""
