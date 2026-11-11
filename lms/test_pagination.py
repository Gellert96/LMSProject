from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from lms.models import Course, Lesson


class LMSPaginationTests(APITestCase):
    """Проверки пагинации курсов и уроков."""

    def setUp(self):
        User = get_user_model()

        self.user = User.objects.create_user(
            email="pagination@example.com",
            password="TestPassword123!",
        )

        self.client.force_authenticate(user=self.user)

        for number in range(12):
            course = Course.objects.create(
                owner=self.user,
                title=f"Курс {number}",
                description="Описание курса",
            )

            Lesson.objects.create(
                owner=self.user,
                course=course,
                title=f"Урок {number}",
                description="Описание урока",
                video_url="https://www.youtube.com/watch?v=abc123",
            )

    def test_courses_default_page_size(self):
        """По умолчанию возвращается пять курсов."""

        response = self.client.get("/api/courses/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 12)
        self.assertEqual(len(response.data["results"]), 5)
        self.assertIsNotNone(response.data["next"])

    def test_lessons_default_page_size(self):
        """По умолчанию возвращается пять уроков."""

        response = self.client.get("/api/lessons/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 12)
        self.assertEqual(len(response.data["results"]), 5)

    def test_courses_custom_page_size(self):
        """Пользователь может менять размер страницы."""

        response = self.client.get("/api/courses/?page_size=10")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 10)

    def test_lessons_second_page(self):
        """Вторая страница возвращает оставшиеся уроки."""

        response = self.client.get("/api/lessons/?page=2&page_size=10")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 2)

    def test_courses_max_page_size(self):
        """Размер страницы ограничен установленным максимумом."""

        response = self.client.get("/api/courses/?page_size=100")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 12)
