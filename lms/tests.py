from django.test import TestCase
from rest_framework.test import APITestCase

from lms.models import Course, Lesson


class CourseLessonTests(TestCase):
    """Тесты моделей курсов и уроков."""

    def setUp(self):
        self.course = Course.objects.create(
            title="Основы Python",
            description="Курс для начинающих.",
        )

        self.lesson1 = Lesson.objects.create(
            course=self.course,
            title="Первый урок",
            description="Знакомство с Python.",
            video_url="https://example.com/video1",
        )

        self.lesson2 = Lesson.objects.create(
            course=self.course,
            title="Второй урок",
            description="Изучение переменных.",
            video_url="https://example.com/video2",
        )

    def test_course_has_multiple_lessons(self):
        """Проверяет связь курса с несколькими уроками."""

        self.assertEqual(self.course.lessons.count(), 2)

        self.assertIn(
            self.lesson1,
            self.course.lessons.all(),
        )

        self.assertIn(
            self.lesson2,
            self.course.lessons.all(),
        )

    def test_deleting_course_deletes_lessons(self):
        """Проверяет каскадное удаление уроков."""

        self.course.delete()

        self.assertEqual(Lesson.objects.count(), 0)


class CourseAPITests(APITestCase):
    """Проверка CRUD для курсов."""

    def setUp(self):
        self.course = Course.objects.create(
            title="Основы Python",
            description="Начальный курс.",
        )

    def test_list_courses(self):
        response = self.client.get("/api/courses/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_create_course(self):
        response = self.client.post(
            "/api/courses/",
            {
                "title": "Django REST Framework",
                "description": "Разработка REST API.",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Course.objects.count(), 2)

    def test_retrieve_course(self):
        response = self.client.get(f"/api/courses/{self.course.id}/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data["title"],
            "Основы Python",
        )

    def test_update_course(self):
        response = self.client.patch(
            f"/api/courses/{self.course.id}/",
            {"title": "Продвинутый Python"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)

        self.course.refresh_from_db()
        self.assertEqual(
            self.course.title,
            "Продвинутый Python",
        )

    def test_delete_course(self):
        response = self.client.delete(f"/api/courses/{self.course.id}/")

        self.assertEqual(response.status_code, 204)
        self.assertFalse(Course.objects.filter(id=self.course.id).exists())


class LessonAPITests(APITestCase):
    """Проверка CRUD для уроков."""

    def setUp(self):
        self.course = Course.objects.create(
            title="Основы Python",
            description="Курс для начинающих.",
        )

        self.lesson = Lesson.objects.create(
            course=self.course,
            title="Введение",
            description="Первый урок.",
            video_url="https://example.com/video",
        )

    def test_list_lessons(self):
        response = self.client.get("/api/lessons/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_create_lesson(self):
        response = self.client.post(
            "/api/lessons/create/",
            {
                "course": self.course.id,
                "title": "Переменные",
                "description": "Второй урок.",
                "video_url": "https://example.com/video2",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Lesson.objects.count(), 2)

    def test_retrieve_lesson(self):
        response = self.client.get(f"/api/lessons/{self.lesson.id}/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data["title"],
            "Введение",
        )

    def test_update_lesson(self):
        response = self.client.patch(
            f"/api/lessons/{self.lesson.id}/update/",
            {"title": "Введение в Python"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)

        self.lesson.refresh_from_db()
        self.assertEqual(
            self.lesson.title,
            "Введение в Python",
        )

    def test_delete_lesson(self):
        response = self.client.delete(f"/api/lessons/{self.lesson.id}/delete/")

        self.assertEqual(response.status_code, 204)
        self.assertFalse(Lesson.objects.filter(id=self.lesson.id).exists())

    def test_delete_course_with_lessons(self):
        response = self.client.delete(f"/api/courses/{self.course.id}/")

        self.assertEqual(response.status_code, 204)
        self.assertEqual(Lesson.objects.count(), 0)
