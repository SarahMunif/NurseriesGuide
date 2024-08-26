from django import forms
from .models import Web_Review
class Web_ReviewForm(forms.ModelForm):
    class Meta:
        model = Web_Review
        exclude = ['parent']