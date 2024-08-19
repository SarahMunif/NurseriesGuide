# registrations/forms.py

from django import forms
from .models import Registration ,Subscription

class RegistrationForm(forms.ModelForm):
    class Meta:
        model = Registration
        fields = "__all__"  

class RegistrationStatusForm(forms.ModelForm):
    class Meta:
        model = Registration
        fields = "__all__" 
class SubscriptionForm(forms.ModelForm):

    class Meta:
        model = Subscription
        fields = "__all__"
        exclude = ['nursery'] 