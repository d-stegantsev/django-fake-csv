from django import forms
from django.forms import inlineformset_factory
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


SchemaColumnFormSet = inlineformset_factory(
    Schema,
    SchemaColumn,
    form=SchemaColumnForm,
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
