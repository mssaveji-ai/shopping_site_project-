from django import forms
from django.core.validators import MaxLengthValidator

class RegisterForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
            'class': 'input',            
            'placeholder': 'Email'
        }), validators=[MaxLengthValidator(100)])
    password = forms.CharField(widget=forms.PasswordInput(attrs={
            'class':'input',
            'placeholder': 'password'
    }), validators=[MaxLengthValidator(100)])
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
            'class':'input',
            'placeholder': 'confirm_password'
    }), validators=[MaxLengthValidator(100)])

    def clean_confirm_password(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')

        if password != confirm_password:
            self.add_error('confirm_password', 'Passwords do not match')
        return confirm_password

class LoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
            'class': 'input',            
            'placeholder': 'Email'
        }), validators=[MaxLengthValidator(100)])
    password = forms.CharField(widget=forms.PasswordInput(attrs={
            'class':'input',
            'placeholder': 'password'
    }), validators=[MaxLengthValidator(100)])
