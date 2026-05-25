from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


class UserAdmin(BaseUserAdmin):
    list_display = ("username", "full_name", "email", "phone", "is_staff", "is_active")
    list_filter = ("is_staff", "is_active", "is_superuser")
    search_fields = ("username", "full_name", "email", "phone")
    ordering = ("username",)

    fieldsets = BaseUserAdmin.fieldsets + (
        ("Контактные данные", {"fields": ("full_name", "phone")}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (
            "Контактные данные",
            {
                "fields": (
                    "full_name",
                    "email",
                    "phone",
                ),
            },
        ),
    )
