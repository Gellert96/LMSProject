from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase

from lms.models import Course, Subscription


class SubscriptionModelTests(TestCase):
    """Проверки модели подписок."""

    def setUp(self):
        User = get_user_model()

        self.user = User.objects.create_user(
            email="subscriptionmodel@example.com",
            password="TestPassword123!",
        )

        self.course = Course.objects.create(
            owner=self.user,
            title="Основы Python",
            description="Учебный курс",
        )

    def test_create_subscription(self):
        """Подписка связывает пользователя и курс."""

        subscription = Subscription.objects.create(
            user=self.user,
            course=self.course,
        )

        self.assertEqual(subscription.user, self.user)
        self.assertEqual(subscription.course, self.course)

    def test_subscription_deleted_with_course(self):
        """Подписка удаляется вместе с курсом."""

        Subscription.objects.create(
            user=self.user,
            course=self.course,
        )

        self.course.delete()

        self.assertEqual(Subscription.objects.count(), 0)


class SubscriptionAPITests(APITestCase):
    """Проверки API добавления и удаления подписок."""

    def setUp(self):
        User = get_user_model()

        self.user = User.objects.create_user(
            email="subscriber@example.com",
            password="TestPassword123!",
        )

        self.course = Course.objects.create(
            owner=self.user,
            title="Django REST Framework",
            description="Разработка REST API",
        )

        self.url = reverse("subscription-toggle")

        self.client.force_authenticate(user=self.user)

    def test_subscribe_to_course(self):
        """Первый POST создаёт подписку."""

        response = self.client.post(
            self.url,
            {"course_id": self.course.id},
            format="json",
        )

        self.assertEqual(response.status_code, 201)

        self.assertEqual(
            response.data["message"],
            "Подписка добавлена.",
        )

        self.assertTrue(
            Subscription.objects.filter(
                user=self.user,
                course=self.course,
            ).exists()
        )

    def test_unsubscribe_from_course(self):
        """Повторный POST удаляет подписку."""

        Subscription.objects.create(
            user=self.user,
            course=self.course,
        )

        response = self.client.post(
            self.url,
            {"course_id": self.course.id},
            format="json",
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            response.data["message"],
            "Подписка удалена.",
        )

        self.assertFalse(
            Subscription.objects.filter(
                user=self.user,
                course=self.course,
            ).exists()
        )

    def test_subscription_toggle(self):
        """Два последовательных запроса переключают подписку."""

        self.client.post(
            self.url,
            {"course_id": self.course.id},
            format="json",
        )

        self.assertEqual(Subscription.objects.count(), 1)

        self.client.post(
            self.url,
            {"course_id": self.course.id},
            format="json",
        )

        self.assertEqual(Subscription.objects.count(), 0)

    def test_subscribe_without_course_id(self):
        """Нельзя подписаться без идентификатора курса."""

        response = self.client.post(
            self.url,
            {},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Subscription.objects.count(), 0)

    def test_subscribe_to_nonexistent_course(self):
        """Несуществующий курс возвращает 404."""

        response = self.client.post(
            self.url,
            {"course_id": 999999},
            format="json",
        )

        self.assertEqual(response.status_code, 404)

    def test_unauthorized_user_cannot_subscribe(self):
        """Для подписки нужна авторизация."""

        self.client.force_authenticate(user=None)

        response = self.client.post(
            self.url,
            {"course_id": self.course.id},
            format="json",
        )

        self.assertIn(response.status_code, (401, 403))
        self.assertEqual(Subscription.objects.count(), 0)

    def test_course_has_is_subscribed_field(self):
        """Сериализатор показывает активную подписку."""

        Subscription.objects.create(
            user=self.user,
            course=self.course,
        )

        response = self.client.get(f"/api/courses/{self.course.id}/")

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["is_subscribed"])

    def test_course_without_subscription(self):
        """При отсутствии подписки возвращается False."""

        response = self.client.get(f"/api/courses/{self.course.id}/")

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.data["is_subscribed"])

    def test_subscribe_to_another_users_course(self):
        """Пользователь может подписаться на чужой курс."""

        User = get_user_model()

        other_user = User.objects.create_user(
            email="anotherowner@example.com",
            password="TestPassword123!",
        )

        other_course = Course.objects.create(
            owner=other_user,
            title="Курс другого автора",
            description="Описание",
        )

        response = self.client.post(
            self.url,
            {"course_id": other_course.id},
            format="json",
        )

        self.assertEqual(response.status_code, 201)

        self.assertTrue(
            Subscription.objects.filter(
                user=self.user,
                course=other_course,
            ).exists()
        )
