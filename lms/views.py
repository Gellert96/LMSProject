from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from lms.models import Course, Lesson, Subscription
from lms.paginators import LMSPagination
from lms.serializers import CourseSerializer, LessonSerializer
from users.permissions import IsModerator, IsOwner


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


class LessonListAPIView(generics.ListAPIView):
    """Список доступных пользователю уроков."""

    serializer_class = LessonSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = LMSPagination

    def get_queryset(self):
        user = self.request.user

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


class LessonDestroyAPIView(generics.DestroyAPIView):
    """Удаление урока только его владельцем."""

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = (
        permissions.IsAuthenticated,
        ~IsModerator,
        IsOwner,
    )


class SubscriptionAPIView(APIView):
    """Добавляет или удаляет подписку на курс."""

    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        user = request.user
        course_id = request.data.get("course_id")

        if course_id is None:
            return Response(
                {"error": "Необходимо указать course_id."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        course = get_object_or_404(Course, pk=course_id)

        subscription = Subscription.objects.filter(
            user=user,
            course=course,
        )

        if subscription.exists():
            subscription.delete()

            return Response(
                {"message": "Подписка удалена."},
                status=status.HTTP_200_OK,
            )

        Subscription.objects.create(
            user=user,
            course=course,
        )

        return Response(
            {"message": "Подписка добавлена."},
            status=status.HTTP_201_CREATED,
        )
