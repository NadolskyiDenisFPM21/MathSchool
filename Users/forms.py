from django import forms
from django.contrib.auth.forms import UserCreationForm
from Users.models import User

class StudentRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=100, required=True, label='Ім’я', widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=100, required=True, label='Прізвище', widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(max_length=100, required=True, label='Email', widget=forms.EmailInput(attrs={'class': 'form-control'}))
    username = forms.CharField(max_length=100, required=True, label='Логін', widget=forms.TextInput(attrs={'class': 'form-control'}))
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label='Підтвердження паролю', widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username', 'password1', 'password2']
