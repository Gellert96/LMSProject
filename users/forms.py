from django import forms
from django.contrib.auth.forms import (
    BaseUserCreationForm,
    ReadOnlyPasswordHashField,
)

from users.models import User


class AdminUserCreationForm(BaseUserCreationForm):
    """Создание пользователя через Django Admin."""

    class Meta:
        model = User
        fields = ("email",)


class AdminUserChangeForm(forms.ModelForm):
    """Редактирование пользователя через Django Admin."""

    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = "__all__"
