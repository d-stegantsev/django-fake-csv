from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView

from schemas.forms import SchemaForm, SchemaColumnFormSet, GenerateDatasetForm
from schemas.models import Schema, Dataset
from schemas.tasks import generate_csv_file


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
        formset = SchemaColumnFormSet(prefix="form")
        return render(request, self.template_name, {"form": form, "formset": formset})

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

        return render(request, self.template_name, {"form": form, "formset": formset})


class SchemaDetailView(LoginRequiredMixin, DetailView):
    model = Schema
    template_name = "schemas/schema_detail.html"
    context_object_name = "schema"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["columns"] = self.object.columns.all().order_by("order")
        context["generate_form"] = kwargs.get("generate_form") or GenerateDatasetForm()
        context["datasets"] = self.object.datasets.order_by("-created_at")
        return context

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

            generate_csv_file.delay(dataset.id)

            return redirect(self.request.path_info)

        context = self.get_context_data(generate_form=form)
        return self.render_to_response(context)


class SchemaUpdateView(LoginRequiredMixin, UpdateView):
    model = Schema
    form_class = SchemaForm
    template_name = "schemas/schema_update.html"
    context_object_name = "schema"
    success_url = reverse_lazy("schemas:schema_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["formset"] = SchemaColumnFormSet(self.request.POST, instance=self.object, prefix="form")
        else:
            context["formset"] = SchemaColumnFormSet(instance=self.object, prefix="form")
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context["formset"]
        if form.is_valid() and formset.is_valid():
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            return redirect(self.get_success_url())
        return self.render_to_response(self.get_context_data(form=form))


class SchemaDeleteView(DeleteView):
    model = Schema
    template_name = "schemas/schema_confirm_delete.html"
    success_url = reverse_lazy("schemas:schema_list")
