from django import forms
from .models import Customer  # Import the relevant model
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class SignInForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name']  


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']