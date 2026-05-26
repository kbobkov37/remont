from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", views.PortalLoginView.as_view(), name="login"),
    path("login/verify/", views.Verify2FAView.as_view(), name="verify_2fa"),
    path("setup-2fa/", views.setup_2fa_view, name="setup_2fa"),
    path("qrcode/<int:pk>/", views.qrcode_view, name="qrcode"),
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("logout/", views.logout_view, name="logout"),
]
