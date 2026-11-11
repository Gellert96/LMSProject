from rest_framework import serializers

from lms.models import Course, Lesson, Subscription
from lms.validators import validate_youtube_url


class LessonSerializer(serializers.ModelSerializer):
    """Сериализатор уроков с проверкой владельца и видеоссылки."""

    owner = serializers.PrimaryKeyRelatedField(read_only=True)

    video_url = serializers.URLField(
        validators=[validate_youtube_url],
    )

    class Meta:
        model = Lesson
        fields = (
            "id",
            "owner",
            "course",
            "title",
            "description",
            "preview",
            "video_url",
        )

    def validate_course(self, value):
        """Разрешает обычному пользователю выбирать только свои курсы."""

        request = self.context.get("request")

        if request is None or not request.user.is_authenticated:
            return value

        user = request.user

        if user.groups.filter(name="moderators").exists():
            return value

        if value.owner_id != user.pk:
            raise serializers.ValidationError(
                "Вы можете добавлять уроки только в свои курсы."
            )

        return value


class CourseSerializer(serializers.ModelSerializer):
    """Сериализатор курса с уроками и информацией о подписке."""

    owner = serializers.PrimaryKeyRelatedField(read_only=True)

    lessons_count = serializers.SerializerMethodField()

    lessons = LessonSerializer(
        many=True,
        read_only=True,
    )

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = (
            "id",
            "owner",
            "title",
            "preview",
            "description",
            "lessons_count",
            "lessons",
            "is_subscribed",
        )

    def get_lessons_count(self, obj):
        """Возвращает количество уроков курса."""
        return obj.lessons.count()

    def get_is_subscribed(self, obj):
        """Проверяет подписку текущего пользователя на курс."""

        request = self.context.get("request")

        if request is None or not request.user.is_authenticated:
            return False

        return Subscription.objects.filter(
            user=request.user,
            course=obj,
        ).exists()
