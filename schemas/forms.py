from django import forms
from django.forms import inlineformset_factory, BaseInlineFormSet
from schemas.models import Schema, SchemaColumn


class SchemaForm(forms.ModelForm):
    class Meta:
        model = Schema
        fields = ["name", "column_separator", "string_character"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "column_separator": forms.Select(attrs={"class": "form-select"}),
            "string_character": forms.Select(attrs={"class": "form-select"}),
        }


class SchemaColumnForm(forms.ModelForm):
    class Meta:
        model = SchemaColumn
        fields = ["name", "type", "order", "params"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "type": forms.Select(attrs={"class": "form-select"}),
            "order": forms.NumberInput(attrs={"class": "form-control"}),
            "params": forms.HiddenInput(),
        }

    # Order = 0 for first column form
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk and not self.initial.get("order"):
            self.fields["order"].initial = 0


# Unique Order number validation
class BaseSchemaColumnFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        orders = []
        for form in self.forms:
            if hasattr(form, "cleaned_data") and form.cleaned_data.get("DELETE"):
                continue
            order = form.cleaned_data.get("order")
            if order in orders:
                raise forms.ValidationError(
                    "Each column must have a unique order number."
                )
            orders.append(order)


# Inline formset to manage SchemaColumn objects within a Schema form
SchemaColumnFormSet = inlineformset_factory(
    Schema,
    SchemaColumn,
    form=SchemaColumnForm,
    formset=BaseSchemaColumnFormSet,
    extra=1,
    can_delete=True,
)


class GenerateDatasetForm(forms.Form):
    row_count = forms.IntegerField(
        min_value=1,
        max_value=1000000,
        label="Number of rows",
        widget=forms.NumberInput(attrs={"class": "form-control", "placeholder": "Rows to generate"})
    )
