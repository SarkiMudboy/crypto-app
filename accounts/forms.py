from typing import List
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.password_validation import validate_password
from django import forms
from .models import User


class UserCreationForm(UserCreationForm):

    class Meta:
        model = User
        fields = ("email",)


class UserChangeForm(UserChangeForm):

    class Meta:
        model = User
        fields = ("email",)


# class RegisterUserForm(forms.ModelForm):

#     password = forms.CharField(required=True, widget=forms.PasswordInput)
#     password2 = forms.CharField(write_only=True, required=True)

#     class Meta:
#         model: AbstractBaseUser = User
#         fields: List[str] = ["email", "first_name", "last_name", "password", "password2"]

#     def clean_email(self):
#         email = self.cleaned_data['email']
#         if User.objects.filter(email=email).exists():
#             raise forms.ValidationError("This email is already in use.")
#         return email

#     def clean_password(self):
#         password = self.cleaned_data.get('password')
#         validate_password(password)
#         return password