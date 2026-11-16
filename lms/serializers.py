from rest_framework import serializers

from lms.models import Course, Lesson, Subscription
from lms.validators import validate_youtube_url


class LessonSerializer(serializers.ModelSerializer):
    """Сериализатор урока с проверкой ссылки на видео и курса."""

    owner = serializers.PrimaryKeyRelatedField(read_only=True)
    video_url = serializers.URLField(validators=[validate_youtube_url])

    class Meta:
        model = Lesson
        fields = (
            "id",
            "title",
            "description",
            "preview",
            "video_url",
            "course",
            "owner",
        )

    def validate_course(self, value):
        """Проверяет право добавить урок в выбранный курс."""

        request = self.context.get("request")

        if request is None or not request.user.is_authenticated:
            return value

        if self.instance is not None and self.instance.course_id == value.pk:
            return value

        if value.owner_id != request.user.pk:
            raise serializers.ValidationError(
                "Вы можете добавлять уроки только в свои курсы."
            )

        return value


class CourseSerializer(serializers.ModelSerializer):
    """Сериализатор курса с уроками и признаком подписки."""

    owner = serializers.PrimaryKeyRelatedField(read_only=True)
    lessons_count = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = (
            "id",
            "title",
            "preview",
            "description",
            "owner",
            "lessons_count",
            "lessons",
            "is_subscribed",
        )

    def get_lessons_count(self, obj) -> int:
        """Возвращает количество уроков курса."""

        return obj.lessons.count()

    def get_is_subscribed(self, obj) -> bool:
        """Проверяет подписку текущего пользователя на курс."""

        request = self.context.get("request")

        if request is None or not request.user.is_authenticated:
            return False

        return Subscription.objects.filter(
            user_id=request.user.pk,
            course_id=obj.pk,
        ).exists()
