from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from lms.serializers import CourseSerializer, LessonSerializer
from users.models import Payment, User


class PaymentSerializer(serializers.ModelSerializer):
    """Сериализатор платежей."""

    class Meta:
        model = Payment
        fields = (
            "id",
            "user",
            "payment_date",
            "course",
            "lesson",
            "amount",
            "payment_method",
        )


class PaymentHistorySerializer(serializers.ModelSerializer):
    """История платежей с подробностями курса и урока."""

    course = CourseSerializer(read_only=True)
    lesson = LessonSerializer(read_only=True)

    class Meta:
        model = Payment
        fields = (
            "id",
            "payment_date",
            "course",
            "lesson",
            "amount",
            "payment_method",
        )


class UserSerializer(serializers.ModelSerializer):
    """Профиль пользователя с историей платежей."""

    payments = PaymentHistorySerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "phone",
            "city",
            "avatar",
            "payments",
        )


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Регистрация нового пользователя."""

    password = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password"},
    )

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "password",
            "first_name",
            "last_name",
            "phone",
            "city",
        )
        read_only_fields = ("id",)

    def validate_email(self, value):
        """Проверяет уникальность email без учёта регистра."""

        email = value.strip().lower()

        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError(
                "Пользователь с таким email уже существует."
            )

        return email

    def validate_password(self, value):
        """Проверяет надёжность пароля."""

        try:
            validate_password(value)
        except DjangoValidationError as error:
            raise serializers.ValidationError(error.messages) from error

        return value

    def create(self, validated_data):
        """Создаёт пользователя с хешированным паролем."""

        password = validated_data.pop("password")

        return User.objects.create_user(
            password=password,
            **validated_data,
        )


class PublicUserSerializer(serializers.ModelSerializer):
    """Общедоступная информация профиля."""

    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "city",
            "avatar",
        )


class UserUpdateSerializer(serializers.ModelSerializer):
    """Редактирование собственного профиля."""

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "phone",
            "city",
            "avatar",
        )
        read_only_fields = ("id",)
