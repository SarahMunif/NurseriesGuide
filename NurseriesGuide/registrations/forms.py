# registrations/forms.py

from django import forms
from .models import Registration ,Subscription,Review

class RegistrationForm(forms.ModelForm):
    class Meta:
        model = Registration
        fields = "__all__"  

class RegistrationStatusForm(forms.ModelForm):
    class Meta:
        model = Registration
        fields = "__all__" 
        exclude = ['child',"subscription"] 

class SubscriptionForm(forms.ModelForm):

    class Meta:
        model = Subscription
        fields = "__all__"
        exclude = ['nursery'] 

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        exclude = ['parent','nursery']