from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import AllowAny

from users.models import Payment, User
from users.serializers import PaymentSerializer, UserSerializer


class PaymentListAPIView(generics.ListAPIView):
    """Список платежей с фильтрацией и сортировкой."""

    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    filter_backends = (
        DjangoFilterBackend,
        OrderingFilter,
    )

    filterset_fields = (
        "course",
        "lesson",
        "payment_method",
    )

    ordering_fields = ("payment_date",)

    ordering = ("-payment_date",)


class UserRetrieveAPIView(generics.RetrieveAPIView):
    """Просмотр профиля пользователя с историей платежей."""

    queryset = User.objects.prefetch_related(
        "payments__course__lessons",
        "payments__lesson",
    )
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)
