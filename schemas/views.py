from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView

from schemas.forms import SchemaForm, SchemaColumnFormSet
from schemas.models import Schema


class SchemaListView(LoginRequiredMixin, ListView):
    model = Schema
    template_name = "schemas/schema_list.html"
    context_object_name = "schemas"

    def get_queryset(self):
        return Schema.objects.filter(user=self.request.user).order_by("-updated_at")


class SchemaCreateView(LoginRequiredMixin, CreateView):
    model = Schema
    form_class = SchemaForm
    template_name = "schemas/schema_create.html"
    success_url = reverse_lazy("schemas:schema_list")

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        formset = SchemaColumnFormSet()
        return render(request, self.template_name, {"form": form, "formset": formset})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        formset = SchemaColumnFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            schema = form.save(commit=False)
            schema.user = request.user
            schema.save()
            formset.instance = schema
            formset.save()
            return redirect(self.success_url)

        return render(request, self.template_name, {"form": form, "formset": formset})
