from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase


class UserAuthenticationTests(APITestCase):
    """Проверки регистрации, JWT и прав пользователей."""

    def setUp(self):
        User = get_user_model()

        self.user = User.objects.create_user(
            email="student@example.com",
            password="TestPassword123!",
        )

        self.other_user = User.objects.create_user(
            email="other@example.com",
            password="TestPassword123!",
        )

    def test_registration_without_authentication(self):
        """Регистрация доступна без JWT."""

        response = self.client.post(
            "/api/register/",
            {
                "email": "newstudent@example.com",
                "password": "NewPassword123!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)

        User = get_user_model()
        self.assertTrue(User.objects.filter(email="newstudent@example.com").exists())

    def test_jwt_token(self):
        """Пользователь может получить JWT по email и паролю."""

        response = self.client.post(
            "/api/token/",
            {
                "email": "student@example.com",
                "password": "TestPassword123!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_users_list_requires_authentication(self):
        """Список пользователей недоступен без JWT."""

        response = self.client.get("/api/users/")

        self.assertEqual(response.status_code, 401)

    def test_users_list_contains_only_public_data(self):
        """В списке пользователей нет личных данных."""

        self.client.force_authenticate(user=self.user)

        response = self.client.get("/api/users/")

        self.assertEqual(response.status_code, 200)

        for profile in response.data:
            self.assertNotIn("password", profile)
            self.assertNotIn("email", profile)
            self.assertNotIn("last_name", profile)
            self.assertNotIn("payments", profile)

    def test_cannot_update_other_user(self):
        """Нельзя изменить чужой профиль."""

        self.client.force_authenticate(user=self.user)

        response = self.client.patch(
            f"/api/users/{self.other_user.id}/",
            {"first_name": "Изменённое имя"},
            format="json",
        )

        self.assertEqual(response.status_code, 403)

    def test_cannot_delete_other_user(self):
        """Нельзя удалить чужой профиль."""

        self.client.force_authenticate(user=self.user)

        response = self.client.delete(f"/api/users/{self.other_user.id}/")

        self.assertEqual(response.status_code, 403)

        User = get_user_model()
        self.assertTrue(User.objects.filter(pk=self.other_user.id).exists())

    def test_can_update_own_profile(self):
        """Пользователь может изменить собственный профиль."""

        self.client.force_authenticate(user=self.user)

        response = self.client.patch(
            f"/api/users/{self.user.id}/",
            {"first_name": "Алексей"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)

        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Алексей")

    def test_can_delete_own_profile(self):
        """Пользователь может удалить собственный профиль."""

        self.client.force_authenticate(user=self.user)

        response = self.client.delete(f"/api/users/{self.user.id}/")

        self.assertEqual(response.status_code, 204)

        User = get_user_model()
        self.assertFalse(User.objects.filter(pk=self.user.id).exists())

