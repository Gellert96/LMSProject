from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APITestCase

from lms.models import Course, Lesson
from lms.serializers import CourseSerializer


class CourseLessonTests(TestCase):
    """Проверка моделей курсов и уроков."""

    def setUp(self):
        User = get_user_model()

        self.user = User.objects.create_user(
            email="modeltest@example.com",
            password="TestPassword123!",
        )

        self.course = Course.objects.create(
            owner=self.user,
            title="Основы Python",
            description="Курс для начинающих.",
        )

        self.lesson1 = Lesson.objects.create(
            owner=self.user,
            course=self.course,
            title="Первый урок",
            description="Знакомство с Python.",
            video_url="https://www.youtube.com/watch?v=video1",
        )

        self.lesson2 = Lesson.objects.create(
            owner=self.user,
            course=self.course,
            title="Второй урок",
            description="Изучение переменных.",
            video_url="https://www.youtube.com/watch?v=video2",
        )

    def test_course_has_multiple_lessons(self):
        """У одного курса может быть несколько уроков."""

        self.assertEqual(self.course.lessons.count(), 2)
        self.assertIn(self.lesson1, self.course.lessons.all())
        self.assertIn(self.lesson2, self.course.lessons.all())

    def test_deleting_course_deletes_lessons(self):
        """Удаление курса удаляет связанные уроки."""

        self.course.delete()

        self.assertEqual(Lesson.objects.count(), 0)


class CourseAPITests(APITestCase):
    """Проверка CRUD для курсов."""

    def setUp(self):
        User = get_user_model()

        self.user = User.objects.create_user(
            email="coursetest@example.com",
            password="TestPassword123!",
        )

        self.client.force_authenticate(user=self.user)

        self.course = Course.objects.create(
            owner=self.user,
            title="Основы Python",
            description="Начальный курс.",
        )

    def test_list_courses(self):
        """Получение списка своих курсов с пагинацией."""

        response = self.client.get("/api/courses/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertIn("next", response.data)
        self.assertIn("previous", response.data)

    def test_create_course(self):
        """Создание курса с автоматическим назначением владельца."""

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

        new_course = Course.objects.get(pk=response.data["id"])

        self.assertEqual(new_course.owner_id, self.user.id)

    def test_retrieve_course(self):
        """Просмотр собственного курса."""

        response = self.client.get(f"/api/courses/{self.course.id}/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data["title"],
            "Основы Python",
        )

    def test_update_course(self):
        """Редактирование собственного курса."""

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
        """Удаление собственного курса."""

        response = self.client.delete(f"/api/courses/{self.course.id}/")

        self.assertEqual(response.status_code, 204)

        self.assertFalse(Course.objects.filter(id=self.course.id).exists())


class LessonAPITests(APITestCase):
    """Проверка CRUD для уроков."""

    def setUp(self):
        User = get_user_model()

        self.user = User.objects.create_user(
            email="lessontest@example.com",
            password="TestPassword123!",
        )

        self.client.force_authenticate(user=self.user)

        self.course = Course.objects.create(
            owner=self.user,
            title="Основы Python",
            description="Курс для начинающих.",
        )

        self.lesson = Lesson.objects.create(
            owner=self.user,
            course=self.course,
            title="Введение",
            description="Первый урок.",
            video_url="https://www.youtube.com/watch?v=video1",
        )

    def test_list_lessons(self):
        """Получение списка своих уроков с пагинацией."""

        response = self.client.get("/api/lessons/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertIn("next", response.data)
        self.assertIn("previous", response.data)

    def test_create_lesson(self):
        """Создание урока с разрешённой ссылкой YouTube."""

        response = self.client.post(
            "/api/lessons/create/",
            {
                "course": self.course.id,
                "title": "Переменные",
                "description": "Второй урок.",
                "video_url": "https://www.youtube.com/watch?v=video2",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Lesson.objects.count(), 2)

        new_lesson = Lesson.objects.get(pk=response.data["id"])

        self.assertEqual(
            new_lesson.owner_id,
            self.user.id,
        )

        self.assertEqual(
            new_lesson.course_id,
            self.course.id,
        )

    def test_retrieve_lesson(self):
        """Просмотр собственного урока."""

        response = self.client.get(f"/api/lessons/{self.lesson.id}/")

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            response.data["title"],
            "Введение",
        )

    def test_update_lesson(self):
        """Редактирование собственного урока."""

        response = self.client.patch(
            f"/api/lessons/{self.lesson.id}/update/",
            {
                "title": "Введение в Python",
                "video_url": "https://www.youtube.com/watch?v=updated",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)

        self.lesson.refresh_from_db()

        self.assertEqual(
            self.lesson.title,
            "Введение в Python",
        )

        self.assertEqual(
            self.lesson.video_url,
            "https://www.youtube.com/watch?v=updated",
        )

    def test_delete_lesson(self):
        """Удаление собственного урока."""

        response = self.client.delete(f"/api/lessons/{self.lesson.id}/delete/")

        self.assertEqual(response.status_code, 204)

        self.assertFalse(Lesson.objects.filter(id=self.lesson.id).exists())

    def test_delete_course_with_lessons(self):
        """Удаление курса также удаляет его уроки."""

        response = self.client.delete(f"/api/courses/{self.course.id}/")

        self.assertEqual(response.status_code, 204)
        self.assertEqual(Lesson.objects.count(), 0)


class CourseSerializerTests(TestCase):
    """Проверка вложенной сериализации курса."""

    def setUp(self):
        User = get_user_model()

        self.user = User.objects.create_user(
            email="serializertest@example.com",
            password="TestPassword123!",
        )

        self.course = Course.objects.create(
            owner=self.user,
            title="Основы Python",
            description="Курс для начинающих.",
        )

        self.lesson1 = Lesson.objects.create(
            owner=self.user,
            course=self.course,
            title="Введение",
            description="Первый урок.",
            video_url="https://www.youtube.com/watch?v=video1",
        )

        self.lesson2 = Lesson.objects.create(
            owner=self.user,
            course=self.course,
            title="Переменные",
            description="Второй урок.",
            video_url="https://www.youtube.com/watch?v=video2",
        )

    def test_lessons_count(self):
        """Сериализатор возвращает количество уроков."""

        serializer = CourseSerializer(self.course)

        self.assertEqual(
            serializer.data["lessons_count"],
            2,
        )

    def test_nested_lessons(self):
        """Сериализатор возвращает информацию об уроках."""

        serializer = CourseSerializer(self.course)

        lessons = serializer.data["lessons"]

        self.assertEqual(len(lessons), 2)
        self.assertEqual(lessons[0]["title"], "Введение")
        self.assertEqual(lessons[1]["title"], "Переменные")

        self.assertEqual(
            lessons[0]["course"],
            self.course.id,
        )

        self.assertEqual(
            lessons[0]["owner"],
            self.user.id,
        )
