from django import forms
from .models import UserProfile
from django.contrib.auth.models import User
from django_recaptcha.fields import ReCaptchaField


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['age', 'address', 'mobile', 'gender']


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']


class Captcha(forms.Form):
    captcha = ReCaptchaField()
