from rest_framework import serializers

from lms.models import Course, Lesson


class CourseSerializer(serializers.ModelSerializer):
    """Сериализатор курсов."""

    class Meta:
        model = Course
        fields = (
            "id",
            "title",
            "preview",
            "description",
        )


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
