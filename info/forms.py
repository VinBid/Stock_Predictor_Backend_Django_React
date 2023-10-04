from django import forms
from .models import Customer  # Import the relevant model

class SignInForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name']  # Replace with actual fields from your model
