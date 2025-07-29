from django import forms
from django.forms import inlineformset_factory

from schemas.models import Schema, SchemaColumn


class SchemaForm(forms.ModelForm):
    class Meta:
        model = Schema
        fields = ["name"]


class SchemaColumnForm(forms.ModelForm):
    class Meta:
        model = SchemaColumn
        fields = ["name", "type", "order", "params"]
        widgets = {
            "params": forms.Textarea(attrs={"rows": 2}),
        }


SchemaColumnFormSet = inlineformset_factory(
    Schema,
    SchemaColumn,
    form=SchemaColumnForm,
    extra=1,
    can_delete=True
)
