from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import User

INPUT_CLASS = {"class": "input"}


class RegistrationForm(UserCreationForm):
    full_name = forms.CharField(
        label="ФИО",
        max_length=255,
        widget=forms.TextInput(attrs={**INPUT_CLASS, "autocomplete": "name"}),
    )
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={**INPUT_CLASS, "autocomplete": "email"}),
    )
    phone = forms.CharField(
        label="Телефон",
        max_length=20,
        widget=forms.TextInput(attrs={**INPUT_CLASS, "autocomplete": "tel"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if "class" not in field.widget.attrs:
                field.widget.attrs["class"] = "input"

    class Meta:
        model = User
        fields = ("username", "full_name", "email", "phone", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.full_name = self.cleaned_data["full_name"]
        user.email = self.cleaned_data["email"]
        user.phone = self.cleaned_data["phone"]
        if commit:
            user.save()
        return user


class PortalAuthenticationForm(AuthenticationForm):
    """Первый шаг входа: логин и пароль."""

    username = forms.CharField(label="Логин")
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput)


class OTPVerifyForm(forms.Form):
    """Второй шаг входа: код 2FA."""

    otp_token = forms.CharField(
        label="Код из приложения 2FA",
        max_length=8,
        widget=forms.TextInput(
            attrs={
                "autocomplete": "one-time-code",
                "inputmode": "numeric",
                "pattern": "[0-9]*",
            }
        ),
    )


class TOTPSetupForm(forms.Form):
    """Подтверждение настройки TOTP при регистрации."""

    token = forms.CharField(
        label="Код из приложения",
        max_length=8,
        widget=forms.TextInput(
            attrs={
                "autocomplete": "one-time-code",
                "inputmode": "numeric",
            }
        ),
    )
