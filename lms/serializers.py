from rest_framework import serializers

from lms.models import Course, Lesson


class LessonSerializer(serializers.ModelSerializer):
    """Сериализатор уроков."""

    class Meta:
        model = Lesson
        fields = (
            "id",
            "course",
            "title",
            "description",
            "preview",
            "video_url",
        )


class CourseSerializer(serializers.ModelSerializer):
    """Сериализатор курса с количеством и списком уроков."""

    lessons_count = serializers.SerializerMethodField()

    lessons = LessonSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = Course
        fields = (
            "id",
            "title",
            "preview",
            "description",
            "lessons_count",
            "lessons",
        )

    def get_lessons_count(self, obj):
        """Возвращает количество уроков курса."""
        return obj.lessons.count()
