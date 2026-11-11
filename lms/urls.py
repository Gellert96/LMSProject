from django.urls import include, path
from rest_framework.routers import DefaultRouter

from lms.views import (
    CourseViewSet,
    LessonCreateAPIView,
    LessonDestroyAPIView,
    LessonListAPIView,
    LessonRetrieveAPIView,
    LessonUpdateAPIView,
    SubscriptionAPIView,
)

router = DefaultRouter()
router.register("courses", CourseViewSet, basename="course")

urlpatterns = [
    # Курсы: CRUD через ViewSet
    path("", include(router.urls)),
    # Уроки: CRUD через отдельные обработчики
    path(
        "lessons/",
        LessonListAPIView.as_view(),
        name="lesson-list",
    ),
    path(
        "lessons/create/",
        LessonCreateAPIView.as_view(),
        name="lesson-create",
    ),
    path(
        "lessons/<int:pk>/",
        LessonRetrieveAPIView.as_view(),
        name="lesson-detail",
    ),
    path(
        "lessons/<int:pk>/update/",
        LessonUpdateAPIView.as_view(),
        name="lesson-update",
    ),
    path(
        "lessons/<int:pk>/delete/",
        LessonDestroyAPIView.as_view(),
        name="lesson-delete",
    ),
    # Подписки: добавление или удаление подписки на курс
    path(
        "subscriptions/",
        SubscriptionAPIView.as_view(),
        name="subscription-toggle",
    ),
]
