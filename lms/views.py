from datetime import timedelta

from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_spectacular.utils import OpenApiResponse, extend_schema, inline_serializer
from rest_framework import generics, permissions, serializers, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from lms.models import Course, Lesson, Subscription
from lms.paginators import LMSPagination
from lms.serializers import CourseSerializer, LessonSerializer
from lms.tasks import notify_course_subscribers
from users.permissions import IsModerator, IsOwner


def record_course_update(course, updated_at):
    """Фиксирует обновление курса и планирует уведомление."""

    previous_update = course.updated_at
    course.updated_at = updated_at
    course.save(update_fields=["updated_at"])

    if previous_update is None or updated_at - previous_update >= timedelta(hours=4):
        notify_course_subscribers.delay_on_commit(course.pk)


class CourseViewSet(viewsets.ModelViewSet):
    """CRUD курсов с разграничением прав доступа."""

    serializer_class = CourseSerializer
    pagination_class = LMSPagination

    def get_queryset(self):
        user = self.request.user

        if not user.is_authenticated:
            return Course.objects.none()

        if user.groups.filter(name="moderators").exists():
            return Course.objects.all()

        return Course.objects.filter(owner=user)

    def get_permissions(self):
        if self.action == "create":
            permission_classes = (
                permissions.IsAuthenticated,
                ~IsModerator,
            )
        elif self.action in ("update", "partial_update", "retrieve"):
            permission_classes = (
                permissions.IsAuthenticated,
                IsModerator | IsOwner,
            )
        elif self.action == "destroy":
            permission_classes = (
                permissions.IsAuthenticated,
                ~IsModerator,
                IsOwner,
            )
        else:
            permission_classes = (permissions.IsAuthenticated,)

        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @transaction.atomic
    def perform_update(self, serializer):
        course = Course.objects.select_for_update().get(pk=serializer.instance.pk)
        serializer.instance = course
        serializer.save()
        record_course_update(course, timezone.now())


class LessonListAPIView(generics.ListAPIView):
    """Список доступных пользователю уроков."""

    serializer_class = LessonSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = LMSPagination

    def get_queryset(self):
        user = self.request.user

        if not user.is_authenticated:
            return Lesson.objects.none()

        if user.groups.filter(name="moderators").exists():
            return Lesson.objects.all()

        return Lesson.objects.filter(owner=user)


class LessonRetrieveAPIView(generics.RetrieveAPIView):
    """Просмотр своего урока или любого урока модератором."""

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = (
        permissions.IsAuthenticated,
        IsModerator | IsOwner,
    )


class LessonCreateAPIView(generics.CreateAPIView):
    """Создание урока обычным пользователем."""

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = (
        permissions.IsAuthenticated,
        ~IsModerator,
    )

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonUpdateAPIView(generics.UpdateAPIView):
    """Редактирование урока владельцем или модератором."""

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = (
        permissions.IsAuthenticated,
        IsModerator | IsOwner,
    )

    @transaction.atomic
    def perform_update(self, serializer):
        lesson = serializer.save()
        course = Course.objects.select_for_update().get(pk=lesson.course_id)
        record_course_update(course, timezone.now())


class LessonDestroyAPIView(generics.DestroyAPIView):
    """Удаление урока только его владельцем."""

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = (
        permissions.IsAuthenticated,
        ~IsModerator,
        IsOwner,
    )


class SubscriptionToggleResponseSerializer(serializers.Serializer):
    """Сообщение о добавлении или удалении подписки."""

    message = serializers.CharField()


class SubscriptionAPIView(APIView):
    """Добавляет или удаляет подписку на курс."""

    permission_classes = (permissions.IsAuthenticated,)

    @extend_schema(
        summary="Переключить подписку на курс",
        description=(
            "Создаёт подписку текущего пользователя на курс. "
            "Если подписка уже существует, удаляет её."
        ),
        request=inline_serializer(
            name="SubscriptionToggleRequest",
            fields={"course_id": serializers.IntegerField()},
        ),
        responses={
            200: OpenApiResponse(
                response=SubscriptionToggleResponseSerializer,
                description="Подписка удалена.",
            ),
            201: OpenApiResponse(
                response=SubscriptionToggleResponseSerializer,
                description="Подписка добавлена.",
            ),
            400: OpenApiResponse(
                response=inline_serializer(
                    name="SubscriptionErrorResponse",
                    fields={"error": serializers.CharField()},
                ),
                description="Не указан course_id.",
            ),
            401: OpenApiResponse(description="Требуется аутентификация."),
            404: OpenApiResponse(description="Курс не найден."),
        },
    )
    def post(self, request):
        user = request.user
        course_id = request.data.get("course_id")

        if course_id is None:
            return Response(
                {"error": "Необходимо указать course_id."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        course = get_object_or_404(Course, pk=course_id)
        subscriptions = Subscription.objects.filter(user=user, course=course)

        if subscriptions.exists():
            subscriptions.delete()
            return Response(
                {"message": "Подписка удалена."},
                status=status.HTTP_200_OK,
            )

        Subscription.objects.create(user=user, course=course)
        return Response(
            {"message": "Подписка добавлена."},
            status=status.HTTP_201_CREATED,
        )
