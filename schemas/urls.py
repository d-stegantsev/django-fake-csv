from django.urls import path
from schemas.views import (
    SchemaListView,
    SchemaCreateView,
    SchemaDetailView,
    SchemaUpdateView,
    SchemaDeleteView,
    SchemaStatusPartialView
)

app_name = "schemas"

urlpatterns = [
    path("", SchemaListView.as_view(), name="schema_list"),
    path("new/", SchemaCreateView.as_view(), name="schema_create"),
    path("schemas/<int:pk>/", SchemaDetailView.as_view(), name="schema_detail"),
    path("schemas/<int:pk>/edit/", SchemaUpdateView.as_view(), name="schema_update"),
    path("schemas/<int:pk>/delete/", SchemaDeleteView.as_view(), name="schema_delete"),
    path("schemas/<int:pk>/table-statuses/", SchemaStatusPartialView.as_view(), name="schema_table_statuses"),
]
