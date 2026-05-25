from django import forms
from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin
from django.contrib.auth.models import Group
from django_otp.admin import OTPAdminAuthenticationForm, OTPAdminSite
from django_otp.plugins.otp_static.admin import StaticDeviceAdmin
from django_otp.plugins.otp_static.models import StaticDevice
from django_otp.plugins.otp_totp.admin import TOTPDeviceAdmin
from django_otp.plugins.otp_totp.models import TOTPDevice

from accounts.admin import UserAdmin
from accounts.models import User


class RemontOTPAdminAuthenticationForm(OTPAdminAuthenticationForm):
    otp_device = forms.ChoiceField(
        required=False,
        choices=[("", "---------")],
        widget=forms.Select,
    )

    def _update_form(self, user):
        super()._update_form(user)
        self.fields["otp_device"].choices = [("", "---------")] + self.device_choices(user)


class RemontTOTPDeviceAdmin(TOTPDeviceAdmin):
    autocomplete_fields = ["user"]
    radio_fields = {}

    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)
        initial.setdefault("user", request.user.pk)
        initial.setdefault("digits", 6)
        return initial


class RemontStaticDeviceAdmin(StaticDeviceAdmin):
    autocomplete_fields = ["user"]

    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)
        initial.setdefault("user", request.user.pk)
        return initial


class RemontOTPAdminSite(OTPAdminSite):
    site_header = "Remont — администрирование"
    site_title = "Remont Admin"
    index_title = "Панель управления"
    login_form = RemontOTPAdminAuthenticationForm


admin_site = RemontOTPAdminSite(name="admin")

admin_site.register(User, UserAdmin)
admin_site.register(Group, GroupAdmin)
admin_site.register(TOTPDevice, RemontTOTPDeviceAdmin)
admin_site.register(StaticDevice, RemontStaticDeviceAdmin)
