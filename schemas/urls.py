from django.urls import path
from .views import SchemaListView

app_name = "schemas"

urlpatterns = [
    path("", SchemaListView.as_view(), name="schema_list"),
]