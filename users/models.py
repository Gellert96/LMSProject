from typing import ClassVar

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from lms.models import Course, Lesson
from users.managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    """Пользователь LMS с авторизацией по email."""

    email = models.EmailField(
        unique=True,
        verbose_name="Электронная почта",
    )

    first_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Имя",
    )

    last_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Фамилия",
    )

    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Телефон",
    )

    city = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Город",
    )

    avatar = models.ImageField(
        upload_to="avatars/",
        blank=True,
        null=True,
        verbose_name="Аватар",
    )

    is_staff = models.BooleanField(
        default=False,
        verbose_name="Доступ к админ-панели",
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="Активный пользователь",
    )

    date_joined = models.DateTimeField(
        default=timezone.now,
        verbose_name="Дата регистрации",
    )

    objects = UserManager()

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS: ClassVar[list[str]] = []

    def __str__(self):
        return self.email

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self):
        return self.first_name or self.email

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ("email",)


class Payment(models.Model):
    """Платёж за курс или отдельный урок."""

    class PaymentMethod(models.TextChoices):
        CASH = "cash", "Наличные"
        TRANSFER = "transfer", "Перевод на счёт"

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="payments",
        verbose_name="Пользователь",
    )

    payment_date = models.DateField(
        verbose_name="Дата оплаты",
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="payments",
        blank=True,
        null=True,
        verbose_name="Оплаченный курс",
    )

    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name="payments",
        blank=True,
        null=True,
        verbose_name="Оплаченный урок",
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Сумма оплаты",
    )

    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        verbose_name="Способ оплаты",
    )

    def clean(self):
        """Проверяет, что оплачен либо курс, либо урок."""
        super().clean()

        if bool(self.course_id) == bool(self.lesson_id):
            raise ValidationError("Необходимо указать либо курс, либо урок.")

    def __str__(self):
        return f"{self.user.email} — {self.amount}"

    class Meta:
        verbose_name = "Платёж"
        verbose_name_plural = "Платежи"
        ordering = ("-payment_date",)
        constraints: ClassVar[list[models.CheckConstraint]] = [
            models.CheckConstraint(
                condition=(
                    models.Q(course__isnull=False, lesson__isnull=True)
                    | models.Q(course__isnull=True, lesson__isnull=False)
                ),
                name="payment_exactly_one_item",
            ),
        ]
