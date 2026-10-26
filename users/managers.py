from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    """Менеджер пользователей с авторизацией по email."""

    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        """Создаёт обычного пользователя."""

        if not email:
            raise ValueError("Email обязателен для регистрации.")

        email = self.normalize_email(email.strip())

        user = self.model(
            email=email,
            **extra_fields,
        )

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Создаёт администратора системы."""

        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("У суперпользователя is_staff должен быть True.")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("У суперпользователя is_superuser должен быть True.")

        if not password:
            raise ValueError("Для суперпользователя необходимо указать пароль.")

        return self.create_user(
            email=email,
            password=password,
            **extra_fields,
        )
