# registrations/forms.py

from django import forms
from .models import Registration

class RegistrationForm(forms.ModelForm):
    class Meta:
        model = Registration
        fields = "__all__"  

class RegistrationStatusForm(forms.ModelForm):
    class Meta:
        model = Registration
        fields = "__all__" 
