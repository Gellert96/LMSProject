
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from lms.models import Course, Lesson


class YouTubeValidatorTests(APITestCase):
    """Проверки разрешённых и запрещённых видеоссылок."""

    def setUp(self):
        User = get_user_model()

        self.user = User.objects.create_user(
            email="validator@example.com",
            password="TestPassword123!",
        )

        self.client.force_authenticate(user=self.user)

        self.course = Course.objects.create(
            owner=self.user,
            title="Тестовый курс",
            description="Курс для проверки ссылок",
        )

    def test_create_lesson_with_youtube_url(self):
        """Урок с YouTube-ссылкой успешно создаётся."""

        response = self.client.post(
            "/api/lessons/create/",
            {
                "course": self.course.id,
                "title": "Урок YouTube",
                "description": "Разрешённая ссылка",
                "video_url": "https://www.youtube.com/watch?v=abc123",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Lesson.objects.count(), 1)

    def test_create_lesson_with_other_domain(self):
        """Нельзя создать урок со ссылкой на другой сайт."""

        response = self.client.post(
            "/api/lessons/create/",
            {
                "course": self.course.id,
                "title": "Урок Vimeo",
                "description": "Запрещённая ссылка",
                "video_url": "https://vimeo.com/123456",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("video_url", response.data)
        self.assertEqual(Lesson.objects.count(), 0)

    def test_create_lesson_with_fake_youtube_domain(self):
        """Поддельный домен YouTube не проходит проверку."""

        response = self.client.post(
            "/api/lessons/create/",
            {
                "course": self.course.id,
                "title": "Поддельный YouTube",
                "description": "Проверка домена",
                "video_url": "https://youtube.com.evil.com/video",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("video_url", response.data)

    def test_update_lesson_with_invalid_url(self):
        """Нельзя заменить ссылку урока на сторонний сайт."""

        lesson = Lesson.objects.create(
            owner=self.user,
            course=self.course,
            title="Исходный урок",
            description="Описание",
            video_url="https://www.youtube.com/watch?v=abc123",
        )

        response = self.client.patch(
            f"/api/lessons/{lesson.id}/update/",
            {"video_url": "https://example.com/video"},
            format="json",
        )

        self.assertEqual(response.status_code, 400)

        lesson.refresh_from_db()
        self.assertEqual(
            lesson.video_url,
            "https://www.youtube.com/watch?v=abc123",
        )
