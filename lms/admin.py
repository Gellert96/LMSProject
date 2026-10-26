from django.contrib import admin

from lms.models import Course, Lesson


class LessonInline(admin.TabularInline):
    """Позволяет добавлять уроки прямо внутри курса."""

    model = Lesson
    extra = 1


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    """Управление курсами."""

    list_display = (
        "id",
        "title",
        "lessons_count",
    )

    search_fields = (
        "title",
        "description",
    )

    inlines = (LessonInline,)

    @admin.display(description="Количество уроков")
    def lessons_count(self, obj):
        return obj.lessons.count()


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    """Управление уроками."""

    list_display = (
        "id",
        "title",
        "course",
        "video_url",
    )

    list_filter = ("course",)

    search_fields = (
        "title",
        "description",
        "course__title",
    )
