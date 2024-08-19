from django import forms
from .models import Nursery,Activity,Staff,Gallery

class ActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = "__all__"
        exclude = ['nursery'] 

class StaffForm(forms.ModelForm):

    class Meta:
        model = Staff
        fields = "__all__"
        exclude = ['nursery'] 
class GalleryForm(forms.ModelForm):

    class Meta:
        model = Gallery
        fields = "__all__"
        exclude = ['nursery'] 
class NurseryOwnerForm(forms.ModelForm):
    class Meta:
        model = Nursery
        fields = "__all__"
        exclude = ['owner', 'status']  # Exclude both owner and status fields

class NurseryForm(forms.ModelForm):
    class Meta:
        model = Nursery
        fields = "__all__"
        exclude = ['owner'] 
        widgets = {
            'neighborhood': forms.HiddenInput(),
        }

