from django.urls import path

from users.views import (
    PaymentListAPIView,
    UserListAPIView,
    UserRegistrationAPIView,
    UserRetrieveAPIView,
)

urlpatterns = [
    path(
        "register/",
        UserRegistrationAPIView.as_view(),
        name="user-register",
    ),
    path(
        "payments/",
        PaymentListAPIView.as_view(),
        name="payment-list",
    ),
    path(
        "users/",
        UserListAPIView.as_view(),
        name="user-list",
    ),
    path(
        "users/<int:pk>/",
        UserRetrieveAPIView.as_view(),
        name="user-detail",
    ),
]
