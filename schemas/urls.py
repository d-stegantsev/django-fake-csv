from django.urls import path
from .views import SchemaListView, SchemaCreateView

app_name = "schemas"

urlpatterns = [
    path("", SchemaListView.as_view(), name="schema_list"),
    path("new/", SchemaCreateView.as_view(), name="schema_create"),
]
