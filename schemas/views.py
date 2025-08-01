from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView

from schemas.forms import SchemaForm, SchemaColumnFormSet, GenerateDatasetForm
from schemas.models import Schema, Dataset
from schemas.tasks import generate_csv_file


# List all schemas for the current user
class SchemaListView(LoginRequiredMixin, ListView):
    model = Schema
    template_name = "schemas/schema_list.html"
    context_object_name = "schemas"

    # Return only schemas belonging to the logged-in user, sorted by last update
    def get_queryset(self):
        return Schema.objects.filter(user=self.request.user).order_by("-updated_at")


# Create a new schema and its columns
class SchemaCreateView(LoginRequiredMixin, CreateView):
    model = Schema
    form_class = SchemaForm
    template_name = "schemas/schema_edit.html"
    success_url = reverse_lazy("schemas:schema_list")

    # Add the column formset and empty form to the template context
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        formset = SchemaColumnFormSet(prefix="form")
        context["formset"] = formset
        context["empty_form"] = formset.empty_form
        return context

    # Handle GET requests: display empty schema form and column formset
    def get(self, request, *args, **kwargs):
        form = self.form_class()
        formset = SchemaColumnFormSet(prefix="form")
        return render(request, self.template_name, {
            "form": form,
            "formset": formset,
            "empty_form": formset.empty_form,
        })

    # Handle POST requests: validate and save schema + columns
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        formset = SchemaColumnFormSet(request.POST, prefix="form")
        if form.is_valid() and formset.is_valid():
            schema = form.save(commit=False)
            schema.user = request.user
            schema.save()
            formset.instance = schema
            formset.save()
            return redirect(self.success_url)
        # If not valid, re-render with errors
        return render(request, self.template_name, {
            "form": form,
            "formset": formset,
            "empty_form": formset.empty_form,
        })


# Show schema details, columns, generate data, and display datasets
class SchemaDetailView(LoginRequiredMixin, DetailView):
    model = Schema
    template_name = "schemas/schema_detail.html"
    context_object_name = "schema"

    # Add columns, generate form, and datasets to the template context
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["columns"] = self.object.columns.all().order_by("order")
        context["generate_form"] = kwargs.get("generate_form") or GenerateDatasetForm()
        context["datasets"] = self.object.datasets.order_by("-created_at")
        return context

    # Handle POST requests: trigger fake data generation
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = GenerateDatasetForm(request.POST)
        if form.is_valid():
            dataset = Dataset.objects.create(
                schema=self.object,
                user=request.user,
                row_count=form.cleaned_data["row_count"],
                status=Dataset.Status.PROCESSING,
            )
            # Run async CSV file generation (Celery)
            generate_csv_file.delay(dataset.id)
            return redirect(self.request.path_info)

        # If the form is invalid, show errors
        context = self.get_context_data(generate_form=form)
        return self.render_to_response(context)


# Edit an existing schema and its columns
class SchemaUpdateView(LoginRequiredMixin, UpdateView):
    model = Schema
    form_class = SchemaForm
    template_name = "schemas/schema_edit.html"
    context_object_name = "schema"
    success_url = reverse_lazy("schemas:schema_list")

    # Provide the correct formset (pre-filled or with POST data)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            formset = SchemaColumnFormSet(self.request.POST, instance=self.object, prefix="form")
        else:
            formset = SchemaColumnFormSet(instance=self.object, prefix="form")
        context["formset"] = formset
        context["empty_form"] = formset.empty_form
        return context

    # Validate and save both the main schema form and the columns formset
    def form_valid(self, form):
        context = self.get_context_data()
        formset = context["formset"]
        if form.is_valid() and formset.is_valid():
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            return redirect(self.get_success_url())
        # If errors, re-render the form
        return self.render_to_response(self.get_context_data(form=form))


# Confirm and delete a schema
class SchemaDeleteView(DeleteView):
    model = Schema
    template_name = "schemas/schema_confirm_delete.html"
    success_url = reverse_lazy("schemas:schema_list")
