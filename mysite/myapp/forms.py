from django import forms
from .models import UserProfile
from django.contrib.auth.models import User
from django_recaptcha.fields import ReCaptchaField

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['age', 'address', 'mobile', 'gender']
