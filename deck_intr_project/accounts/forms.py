from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'メールアドレス'})
    )
    username = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ユーザー名（任意）'})
    )
    password1 = forms.CharField(
        label='パスワード',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'パスワード'})
    )
    password2 = forms.CharField(
        label='パスワード（確認）',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'パスワード（確認）'})
    )
    
    class Meta:
        model = CustomUser
        fields = ('email', 'username')


class CustomAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        label='メールアドレス',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'メールアドレス'})
    )
    password = forms.CharField(
        label='パスワード',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'パスワード'})
    )