from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework.test import APITestCase

from lms.models import Course, Lesson


class LMSPermissionTests(APITestCase):
    """Проверка прав владельцев и модераторов."""

    def setUp(self):
        User = get_user_model()

        self.owner = User.objects.create_user(
            email="owner@example.com",
            password="TestPassword123!",
        )

        self.other_user = User.objects.create_user(
            email="other@example.com",
            password="TestPassword123!",
        )

        self.moderator = User.objects.create_user(
            email="moderator@example.com",
            password="TestPassword123!",
        )

        group, _ = Group.objects.get_or_create(
            name="moderators",
        )
        self.moderator.groups.add(group)

        self.course = Course.objects.create(
            owner=self.owner,
            title="Основы Python",
            description="Курс Python",
        )

        self.lesson = Lesson.objects.create(
            owner=self.owner,
            course=self.course,
            title="Переменные",
            description="Первый урок",
            video_url="https://example.com/video",
        )

    def test_unauthorized_access_denied(self):
        """Неавторизованный пользователь не видит курсы."""

        response = self.client.get("/api/courses/")

        self.assertEqual(response.status_code, 401)

    def test_owner_can_view_own_course(self):
        """Владелец может просматривать свой курс."""

        self.client.force_authenticate(user=self.owner)

        response = self.client.get(f"/api/courses/{self.course.id}/")

        self.assertEqual(response.status_code, 200)

    def test_other_user_cannot_view_course(self):
        """Другой пользователь не видит чужой курс."""

        self.client.force_authenticate(user=self.other_user)

        response = self.client.get(f"/api/courses/{self.course.id}/")

        self.assertEqual(response.status_code, 404)

    def test_course_owner_assigned_automatically(self):
        """Создатель курса автоматически становится владельцем."""

        self.client.force_authenticate(user=self.other_user)

        response = self.client.post(
            "/api/courses/",
            {
                "title": "Django",
                "description": "Новый курс",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)

        course = Course.objects.get(pk=response.data["id"])

        self.assertEqual(
            course.owner_id,
            self.other_user.id,
        )

    def test_lesson_owner_assigned_automatically(self):
        """Создатель урока автоматически становится владельцем."""

        self.client.force_authenticate(user=self.owner)

        response = self.client.post(
            "/api/lessons/create/",
            {
                "course": self.course.id,
                "title": "Функции",
                "description": "Новый урок",
                "video_url": "https://example.com/functions",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)

        lesson = Lesson.objects.get(pk=response.data["id"])

        self.assertEqual(
            lesson.owner_id,
            self.owner.id,
        )

    def test_moderator_can_edit_course(self):
        """Модератор может изменять чужой курс."""

        self.client.force_authenticate(user=self.moderator)

        response = self.client.patch(
            f"/api/courses/{self.course.id}/",
            {"title": "Обновлённый курс"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)

    def test_moderator_cannot_create_course(self):
        """Модератор не может создавать курсы."""

        self.client.force_authenticate(user=self.moderator)

        response = self.client.post(
            "/api/courses/",
            {
                "title": "Запрещённый курс",
                "description": "Проверка разрешений",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 403)

    def test_moderator_cannot_delete_course(self):
        """Модератор не может удалять курсы."""

        self.client.force_authenticate(user=self.moderator)

        response = self.client.delete(f"/api/courses/{self.course.id}/")

        self.assertEqual(response.status_code, 403)

    def test_moderator_cannot_create_lesson(self):
        """Модератор не может создавать уроки."""

        self.client.force_authenticate(user=self.moderator)

        response = self.client.post(
            "/api/lessons/create/",
            {
                "course": self.course.id,
                "title": "Новый урок",
                "description": "Проверка",
                "video_url": "https://example.com/video2",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 403)

    def test_moderator_cannot_delete_lesson(self):
        """Модератор не может удалять уроки."""

        self.client.force_authenticate(user=self.moderator)

        response = self.client.delete(f"/api/lessons/{self.lesson.id}/delete/")

        self.assertEqual(response.status_code, 403)

    def test_cannot_create_lesson_in_another_users_course(self):
        """Нельзя создать урок внутри чужого курса."""

        self.client.force_authenticate(user=self.other_user)

        response = self.client.post(
            "/api/lessons/create/",
            {
                "course": self.course.id,
                "title": "Чужой урок",
                "description": "Проверка безопасности",
                "video_url": "https://example.com/video2",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)

        self.assertEqual(
            Lesson.objects.filter(title="Чужой урок").count(),
            0,
        )

    def test_owner_can_update_own_course(self):
        """Владелец может редактировать свой курс."""

        self.client.force_authenticate(user=self.owner)

        response = self.client.patch(
            f"/api/courses/{self.course.id}/",
            {"title": "Продвинутый Python"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)

        self.course.refresh_from_db()
        self.assertEqual(self.course.title, "Продвинутый Python")

    def test_owner_can_delete_own_course(self):
        """Владелец может удалять свой курс."""

        self.client.force_authenticate(user=self.owner)

        response = self.client.delete(f"/api/courses/{self.course.id}/")

        self.assertEqual(response.status_code, 204)
        self.assertFalse(Course.objects.filter(pk=self.course.id).exists())

    def test_other_user_cannot_update_course(self):
        """Нельзя редактировать чужой курс."""

        self.client.force_authenticate(user=self.other_user)

        response = self.client.patch(
            f"/api/courses/{self.course.id}/",
            {"title": "Чужое изменение"},
            format="json",
        )

        self.assertEqual(response.status_code, 404)

    def test_other_user_cannot_delete_course(self):
        """Нельзя удалять чужой курс."""

        self.client.force_authenticate(user=self.other_user)

        response = self.client.delete(f"/api/courses/{self.course.id}/")

        self.assertEqual(response.status_code, 404)
        self.assertTrue(Course.objects.filter(pk=self.course.id).exists())

    def test_other_user_cannot_view_lesson(self):
        """Нельзя просматривать чужой урок."""

        self.client.force_authenticate(user=self.other_user)

        response = self.client.get(f"/api/lessons/{self.lesson.id}/")

        self.assertEqual(response.status_code, 403)

    def test_other_user_cannot_update_lesson(self):
        """Нельзя редактировать чужой урок."""

        self.client.force_authenticate(user=self.other_user)

        response = self.client.patch(
            f"/api/lessons/{self.lesson.id}/update/",
            {"title": "Чужое изменение"},
            format="json",
        )

        self.assertEqual(response.status_code, 403)

    def test_other_user_cannot_delete_lesson(self):
        """Нельзя удалять чужой урок."""

        self.client.force_authenticate(user=self.other_user)

        response = self.client.delete(f"/api/lessons/{self.lesson.id}/delete/")

        self.assertEqual(response.status_code, 403)
        self.assertTrue(Lesson.objects.filter(pk=self.lesson.id).exists())

    def test_moderator_can_view_and_update_lesson(self):
        """Модератор может просматривать и изменять чужие уроки."""

        self.client.force_authenticate(user=self.moderator)

        response = self.client.get(f"/api/lessons/{self.lesson.id}/")
        self.assertEqual(response.status_code, 200)

        response = self.client.patch(
            f"/api/lessons/{self.lesson.id}/update/",
            {"title": "Проверенный урок"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)

        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.title, "Проверенный урок")
