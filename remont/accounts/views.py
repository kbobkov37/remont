from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView as AuthLoginView
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import FormView
from django_otp import devices_for_user, login as otp_login, match_token, user_has_device
from django_otp.decorators import otp_required
from django_otp.middleware import OTPMiddleware
from django_otp.plugins.otp_totp.models import TOTPDevice
from django_otp.qr import write_qrcode_image

from .forms import OTPVerifyForm, PortalAuthenticationForm, RegistrationForm, TOTPSetupForm
from .utils import is_otp_verified, user_is_verified


class RegisterView(FormView):
    template_name = "accounts/register.html"
    form_class = RegistrationForm
    success_url = reverse_lazy("accounts:setup_2fa")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if is_otp_verified(request) or user_is_verified(request.user):
                return redirect("accounts:dashboard")
            return redirect("accounts:setup_2fa")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user, backend="django.contrib.auth.backends.ModelBackend")
        OTPMiddleware._init_user_fields(self.request.user)
        messages.success(
            self.request,
            "Аккаунт создан. Настройте двухфакторную аутентификацию.",
        )
        return super().form_valid(form)


class PortalLoginView(AuthLoginView):
    """Вход: логин/пароль, затем при необходимости — код 2FA."""

    template_name = "accounts/login.html"
    form_class = PortalAuthenticationForm
    redirect_authenticated_user = True

    def get_success_url(self):
        if is_otp_verified(self.request):
            return reverse("accounts:dashboard")
        if user_has_device(self.request.user):
            return reverse("accounts:verify_2fa")
        return reverse("accounts:setup_2fa")

    def form_valid(self, form):
        response = super().form_valid(form)
        OTPMiddleware._init_user_fields(self.request.user)
        if is_otp_verified(self.request):
            return response
        if user_has_device(self.request.user):
            messages.info(self.request, "Введите код двухфакторной аутентификации.")
            return response
        messages.warning(
            self.request,
            "2FA не настроена. Сначала подключите приложение-аутентификатор.",
        )
        return redirect("accounts:setup_2fa")


class Verify2FAView(FormView):
    template_name = "accounts/verify_2fa.html"
    form_class = OTPVerifyForm

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("accounts:login")
        if is_otp_verified(request) or user_is_verified(request.user):
            return redirect("accounts:dashboard")
        if not user_has_device(request.user):
            return redirect("accounts:setup_2fa")
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse("accounts:dashboard")

    def form_valid(self, form):
        token = form.cleaned_data["otp_token"]
        device = match_token(self.request.user, token)
        if device is None:
            form.add_error("otp_token", "Неверный код. Попробуйте снова.")
            return self.form_invalid(form)
        otp_login(self.request, device)
        OTPMiddleware._init_user_fields(self.request.user)
        messages.success(self.request, "Вход выполнен.")
        return super().form_valid(form)


@login_required
def setup_2fa_view(request):
    if is_otp_verified(request) or user_is_verified(request.user):
        if user_has_device(request.user, confirmed=True):
            return redirect("accounts:dashboard")

    device = (
        TOTPDevice.objects.filter(user=request.user, confirmed=False)
        .order_by("-pk")
        .first()
    )
    if device is None:
        device = TOTPDevice.objects.create(
            user=request.user,
            name="Основное устройство",
            confirmed=False,
        )

    form = TOTPSetupForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        if device.verify_token(form.cleaned_data["token"]):
            device.confirmed = True
            device.save()
            otp_login(request, device)
            OTPMiddleware._init_user_fields(request.user)
            messages.success(request, "2FA успешно подключена.")
            return redirect("accounts:dashboard")
        form.add_error("token", "Неверный код. Проверьте время на телефоне.")

    return render(
        request,
        "accounts/setup_2fa.html",
        {"form": form, "device": device, "config_url": device.config_url},
    )


@otp_required
def dashboard_view(request):
    devices = list(devices_for_user(request.user, confirmed=True))
    return render(
        request,
        "accounts/dashboard.html",
        {"devices": devices},
    )


def qrcode_view(request, pk):
    if not request.user.is_authenticated:
        return HttpResponse(status=403)
    device = TOTPDevice.objects.filter(pk=pk, user=request.user).first()
    if device is None:
        return HttpResponse(status=404)
    response = HttpResponse(content_type="image/svg+xml")
    write_qrcode_image(device.config_url, response)
    return response


def logout_view(request):
    logout(request)
    messages.info(request, "Вы вышли из системы.")
    return redirect("accounts:login")
