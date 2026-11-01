from rest_framework import serializers

from lms.models import Course, Lesson


class LessonSerializer(serializers.ModelSerializer):
    """Сериализатор уроков с проверкой владельца курса."""

    owner = serializers.PrimaryKeyRelatedField(read_only=True)

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
    """Сериализатор курса с количеством и списком уроков."""

    owner = serializers.PrimaryKeyRelatedField(read_only=True)

    lessons_count = serializers.SerializerMethodField()

    lessons = LessonSerializer(
        many=True,
        read_only=True,
    )

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
        )

    def get_lessons_count(self, obj):
        """Возвращает количество уроков курса."""
        return obj.lessons.count()
