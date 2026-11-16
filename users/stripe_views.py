from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import permissions, serializers, status
from rest_framework.exceptions import APIException, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from stripe import StripeError

from lms.models import Course
from users.models import Payment
from users.stripe_services import create_checkout, retrieve_checkout


class StripeUnavailable(APIException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = "Тестовый ключ Stripe не настроен."
    default_code = "stripe_unavailable"


class StripeRequestFailed(APIException):
    status_code = status.HTTP_502_BAD_GATEWAY
    default_detail = "Stripe не смог обработать запрос. Попробуйте позже."
    default_code = "stripe_request_failed"


class CheckoutRequestSerializer(serializers.Serializer):
    course_id = serializers.IntegerField(min_value=1)


class CheckoutPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = (
            "id",
            "user",
            "course",
            "amount",
            "currency",
            "payment_method",
            "status",
            "payment_date",
            "stripe_product_id",
            "stripe_price_id",
            "stripe_session_id",
            "payment_url",
        )
        read_only_fields = fields


class StripeCheckoutAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    @extend_schema(
        summary="Создать сессию оплаты курса",
        description="Цена берётся из карточки курса. Ответ содержит ссылку Stripe Checkout.",
        request=CheckoutRequestSerializer,
        responses={
            201: CheckoutPaymentSerializer,
            400: OpenApiResponse(
                description="Ошибка в course_id или у курса нет цены."
            ),
            401: OpenApiResponse(description="Требуется аутентификация."),
            404: OpenApiResponse(description="Курс не найден."),
            502: OpenApiResponse(description="Stripe не смог создать сессию."),
            503: OpenApiResponse(description="Тестовый ключ Stripe не настроен."),
        },
    )
    def post(self, request):
        serializer = CheckoutRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        course = get_object_or_404(
            Course,
            pk=serializer.validated_data["course_id"],
        )
        amount = course.price

        if amount is None or amount <= 0:
            raise ValidationError(
                {"course_id": "У курса должна быть положительная цена."}
            )

        if not settings.STRIPE_SECRET_KEY.startswith("sk_test_"):
            raise StripeUnavailable()

        try:
            checkout = create_checkout(course=course, amount=amount)
        except StripeError as exc:
            raise StripeRequestFailed() from exc

        if not checkout["payment_url"]:
            raise StripeRequestFailed()

        payment = Payment.objects.create(
            user=request.user,
            course=course,
            amount=amount,
            currency="rub",
            payment_method=Payment.PaymentMethod.STRIPE,
            status=Payment.Status.PENDING,
            **checkout,
        )

        return Response(
            CheckoutPaymentSerializer(payment).data,
            status=status.HTTP_201_CREATED,
        )


class StripePaymentStatusAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    @extend_schema(
        summary="Синхронизировать статус платежа со Stripe",
        description="По ID собственного платежа проверяет состояние сессии в Stripe.",
        request=None,
        responses={
            200: CheckoutPaymentSerializer,
            401: OpenApiResponse(description="Требуется аутентификация."),
            404: OpenApiResponse(description="Платёж Stripe не найден у пользователя."),
            502: OpenApiResponse(
                description="Stripe не смог вернуть состояние сессии."
            ),
            503: OpenApiResponse(description="Тестовый ключ Stripe не настроен."),
        },
    )
    def post(self, request, pk):
        payments = Payment.objects.filter(
            user=request.user,
            payment_method=Payment.PaymentMethod.STRIPE,
        ).exclude(stripe_session_id="")
        payment = get_object_or_404(payments, pk=pk)

        if not settings.STRIPE_SECRET_KEY.startswith("sk_test_"):
            raise StripeUnavailable()

        try:
            checkout = retrieve_checkout(session_id=payment.stripe_session_id)
        except StripeError as exc:
            raise StripeRequestFailed() from exc

        if checkout["payment_status"] == "paid":
            payments.filter(pk=payment.pk).exclude(status=Payment.Status.PAID).update(
                status=Payment.Status.PAID,
                payment_date=timezone.localdate(),
            )
        elif checkout["status"] == "expired":
            payments.filter(pk=payment.pk, status=Payment.Status.PENDING).update(
                status=Payment.Status.EXPIRED,
            )

        payment.refresh_from_db()
        return Response(CheckoutPaymentSerializer(payment).data)
