from django.urls import path
from .views import SchemaListView, SchemaCreateView, SchemaDetailView, SchemaUpdateView

app_name = "schemas"

urlpatterns = [
    path("", SchemaListView.as_view(), name="schema_list"),
    path("new/", SchemaCreateView.as_view(), name="schema_create"),
    path("schemas/<int:pk>/", SchemaDetailView.as_view(), name="schema_detail"),
    path("schemas/<int:pk>/edit/", SchemaUpdateView.as_view(), name="schema_update"),
]
