from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView

from schemas.models import Schema


class SchemaListView(LoginRequiredMixin, ListView):
    model = Schema
    template_name = "schemas/schema_list.html"
    context_object_name = "schema_list"

    def get_queryset(self):
        return Schema.objects.filter(user=self.request.user).order_by("-updated_at")