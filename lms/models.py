from django.db import models


class Course(models.Model):
    """Курс для онлайн-обучения."""

    title = models.CharField(
        max_length=255,
        verbose_name="Название курса",
    )

    preview = models.ImageField(
        upload_to="courses/",
        blank=True,
        null=True,
        verbose_name="Превью курса",
    )

    description = models.TextField(
        verbose_name="Описание курса",
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"
        ordering = ("title",)


class Lesson(models.Model):
    """Урок, принадлежащий определённому курсу."""

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="lessons",
        verbose_name="Курс",
    )

    title = models.CharField(
        max_length=255,
        verbose_name="Название урока",
    )

    description = models.TextField(
        verbose_name="Описание урока",
    )

    preview = models.ImageField(
        upload_to="lessons/",
        blank=True,
        null=True,
        verbose_name="Превью урока",
    )

    video_url = models.URLField(
        max_length=500,
        verbose_name="Ссылка на видео",
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"
        ordering = ("id",)
