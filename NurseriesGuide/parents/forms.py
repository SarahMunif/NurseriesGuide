from .models import Parent ,Child
from django import forms


class ParentForm(forms.ModelForm):
    class Meta:
        model = Parent
        fields = "__all__"


class ChildForm(forms.ModelForm):
    class Meta:
        model = Child
        exclude = ['parent']
