from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from users.forms import AdminUserChangeForm, AdminUserCreationForm
from users.models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Управление пользователями LMS."""

    form = AdminUserChangeForm
    add_form = AdminUserCreationForm

    list_display = (
        "id",
        "email",
        "first_name",
        "last_name",
        "city",
        "is_active",
        "is_staff",
    )

    list_filter = (
        "is_active",
        "is_staff",
        "is_superuser",
        "groups",
    )

    search_fields = (
        "email",
        "first_name",
        "last_name",
        "phone",
        "city",
    )

    ordering = ("email",)

    filter_horizontal = (
        "groups",
        "user_permissions",
    )

    readonly_fields = (
        "last_login",
        "date_joined",
    )

    fieldsets = (
        (
            "Учётная запись",
            {
                "fields": (
                    "email",
                    "password",
                ),
            },
        ),
        (
            "Личная информация",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "phone",
                    "city",
                    "avatar",
                ),
            },
        ),
        (
            "Права доступа",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (
            "Даты",
            {
                "fields": (
                    "last_login",
                    "date_joined",
                ),
            },
        ),
    )

    add_fieldsets = (
        (
            "Создание пользователя",
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "password1",
                    "password2",
                    "first_name",
                    "last_name",
                    "phone",
                    "city",
                    "avatar",
                    "is_active",
                    "is_staff",
                ),
            },
        ),
    )
