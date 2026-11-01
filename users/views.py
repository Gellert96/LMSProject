from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, permissions

from users.models import Payment
from users.permissions import IsSelfOrReadOnly
from users.serializers import (
    PaymentSerializer,
    PublicUserSerializer,
    UserRegistrationSerializer,
    UserSerializer,
    UserUpdateSerializer,
)

User = get_user_model()


class PaymentListAPIView(generics.ListAPIView):
    """Список платежей текущего пользователя."""

    serializer_class = PaymentSerializer
    permission_classes = (permissions.IsAuthenticated,)

    filter_backends = (
        DjangoFilterBackend,
        filters.OrderingFilter,
    )

    filterset_fields = (
        "course",
        "lesson",
        "payment_method",
    )

    ordering_fields = ("payment_date",)

    def get_queryset(self):
        """Пользователь видит только собственные платежи."""
        return Payment.objects.filter(user=self.request.user)


class UserRegistrationAPIView(generics.CreateAPIView):
    """Регистрация новых пользователей без авторизации."""

    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer

    permission_classes = (permissions.AllowAny,)
    authentication_classes = ()


class UserRetrieveAPIView(generics.RetrieveUpdateDestroyAPIView):
    """Просмотр, редактирование и удаление профиля."""

    queryset = User.objects.all()
    permission_classes = (
        permissions.IsAuthenticated,
        IsSelfOrReadOnly,
    )

    def get_serializer_class(self):
        """Выбирает сериализатор с учётом пользователя и метода."""

        if self.request.method in ("PUT", "PATCH"):
            return UserUpdateSerializer

        requested_user_id = int(self.kwargs["pk"])

        if self.request.user.pk == requested_user_id:
            return UserSerializer

        return PublicUserSerializer


class UserListAPIView(generics.ListAPIView):
    """Список пользователей с публичной информацией."""

    queryset = User.objects.all()
    serializer_class = PublicUserSerializer
    permission_classes = (permissions.IsAuthenticated,)
