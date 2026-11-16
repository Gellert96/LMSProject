from django.urls import path

from users.stripe_views import StripeCheckoutAPIView, StripePaymentStatusAPIView
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
    path(
        "payments/checkout/",
        StripeCheckoutAPIView.as_view(),
        name="stripe-checkout",
    ),
    path(
        "payments/<int:pk>/sync/",
        StripePaymentStatusAPIView.as_view(),
        name="stripe-payment-sync",
    ),
]
