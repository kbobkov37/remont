from django.shortcuts import redirect
from django.urls import include, path
from django_otp import user_has_device

from accounts.utils import is_otp_verified, user_is_verified
from remont.admin_site import admin_site


def index(request):
    if request.user.is_authenticated:
        if is_otp_verified(request) or user_is_verified(request.user):
            return redirect("accounts:dashboard")
        if user_has_device(request.user):
            return redirect("accounts:verify_2fa")
        return redirect("accounts:setup_2fa")
    return redirect("accounts:login")


urlpatterns = [
    path("", index, name="home"),
    path("admin/", admin_site.urls),
    path("accounts/", include("accounts.urls")),
]
