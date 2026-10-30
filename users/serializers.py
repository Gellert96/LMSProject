
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
