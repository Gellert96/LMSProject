from django.urls import path

from users.views import PaymentListAPIView, UserRetrieveAPIView

urlpatterns = [
    path(
        "payments/",
        PaymentListAPIView.as_view(),
        name="payment-list",
    ),
    path(
        "users/<int:pk>/",
        UserRetrieveAPIView.as_view(),
        name="user-detail",
    ),
]
