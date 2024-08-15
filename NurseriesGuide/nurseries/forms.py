from django import forms
from .models import Nursery


class NurseryForm(forms.ModelForm):

    class Meta:
        model = Nursery
        fields = "__all__"