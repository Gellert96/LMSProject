from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from lms.models import Course, Lesson
from users.models import Payment


class PaymentAPITests(APITestCase):
    """Проверки фильтрации, сортировки и безопасности платежей."""

    def setUp(self):
        User = get_user_model()

        self.user = User.objects.create_user(
            email="student@example.com",
            password="TestPassword123!",
        )

        self.client.force_authenticate(user=self.user)

        self.course1 = Course.objects.create(
            owner=self.user,
            title="Python",
            description="Курс Python",
        )

        self.course2 = Course.objects.create(
            owner=self.user,
            title="Django",
            description="Курс Django",
        )

        self.lesson1 = Lesson.objects.create(
            owner=self.user,
            course=self.course1,
            title="Переменные",
            description="Основы переменных",
            video_url="https://example.com/video1",
        )

        self.lesson2 = Lesson.objects.create(
            owner=self.user,
            course=self.course2,
            title="Модели",
            description="Модели Django",
            video_url="https://example.com/video2",
        )

        self.payment1 = Payment.objects.create(
            user=self.user,
            payment_date=date(2026, 10, 1),
            course=self.course1,
            amount=Decimal("15000.00"),
            payment_method="cash",
        )

        self.payment2 = Payment.objects.create(
            user=self.user,
            payment_date=date(2026, 10, 5),
            course=self.course2,
            amount=Decimal("20000.00"),
            payment_method="transfer",
        )

        self.payment3 = Payment.objects.create(
            user=self.user,
            payment_date=date(2026, 10, 10),
            lesson=self.lesson1,
            amount=Decimal("3000.00"),
            payment_method="cash",
        )

        self.payment4 = Payment.objects.create(
            user=self.user,
            payment_date=date(2026, 10, 15),
            lesson=self.lesson2,
            amount=Decimal("4500.00"),
            payment_method="transfer",
        )

    def test_payment_list(self):
        """Возвращаются платежи текущего пользователя."""

        response = self.client.get("/api/payments/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 4)

    def test_ordering_ascending(self):
        """Сортировка по возрастанию даты."""

        response = self.client.get("/api/payments/?ordering=payment_date")

        self.assertEqual(response.status_code, 200)

        dates = [item["payment_date"] for item in response.data]

        self.assertEqual(dates, sorted(dates))

    def test_ordering_descending(self):
        """Сортировка по убыванию даты."""

        response = self.client.get("/api/payments/?ordering=-payment_date")

        self.assertEqual(response.status_code, 200)

        dates = [item["payment_date"] for item in response.data]

        self.assertEqual(
            dates,
            sorted(dates, reverse=True),
        )

    def test_filter_by_course(self):
        """Фильтрация по курсу."""

        response = self.client.get(f"/api/payments/?course={self.course1.id}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

        self.assertEqual(
            response.data[0]["id"],
            self.payment1.id,
        )

    def test_filter_by_lesson(self):
        """Фильтрация по уроку."""

        response = self.client.get(f"/api/payments/?lesson={self.lesson1.id}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

        self.assertEqual(
            response.data[0]["id"],
            self.payment3.id,
        )

    def test_filter_cash(self):
        """Фильтрация наличных платежей."""

        response = self.client.get("/api/payments/?payment_method=cash")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

        for payment in response.data:
            self.assertEqual(
                payment["payment_method"],
                "cash",
            )

    def test_filter_transfer(self):
        """Фильтрация платежей банковским переводом."""

        response = self.client.get("/api/payments/?payment_method=transfer")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

        for payment in response.data:
            self.assertEqual(
                payment["payment_method"],
                "transfer",
            )

    def test_combined_filter_and_ordering(self):
        """Фильтрация и сортировка работают одновременно."""

        response = self.client.get(
            "/api/payments/?payment_method=transfer&ordering=payment_date"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

        self.assertEqual(
            response.data[0]["id"],
            self.payment2.id,
        )

        self.assertEqual(
            response.data[1]["id"],
            self.payment4.id,
        )

    def test_cannot_view_other_users_payments(self):
        """Нельзя просматривать платежи другого пользователя."""

        User = get_user_model()

        other_user = User.objects.create_user(
            email="another@example.com",
            password="TestPassword123!",
        )

        other_payment = Payment.objects.create(
            user=other_user,
            payment_date=date(2026, 10, 25),
            course=self.course1,
            amount=Decimal("7000.00"),
            payment_method="cash",
        )

        response = self.client.get("/api/payments/")

        self.assertEqual(response.status_code, 200)

        # Возвращаются только четыре собственных платежа.
        self.assertEqual(len(response.data), 4)

        returned_ids = [item["id"] for item in response.data]

        self.assertNotIn(
            other_payment.id,
            returned_ids,
        )

        self.assertTrue(all(item["user"] == self.user.id for item in response.data))


class UserProfileAPITests(APITestCase):
    """Проверки профилей и истории платежей."""

    def setUp(self):
        User = get_user_model()

        self.user = User.objects.create_user(
            email="profile@example.com",
            password="TestPassword123!",
        )

        self.other_user = User.objects.create_user(
            email="other@example.com",
            password="TestPassword123!",
        )

        self.client.force_authenticate(user=self.user)

        self.course = Course.objects.create(
            owner=self.user,
            title="Основы Python",
            description="Курс программирования.",
        )

        self.lesson = Lesson.objects.create(
            owner=self.user,
            course=self.course,
            title="Переменные",
            description="Изучение переменных.",
            video_url="https://example.com/video",
        )

        Payment.objects.create(
            user=self.user,
            payment_date=date(2026, 10, 20),
            course=self.course,
            amount=Decimal("15000.00"),
            payment_method="transfer",
        )

        Payment.objects.create(
            user=self.user,
            payment_date=date(2026, 10, 21),
            lesson=self.lesson,
            amount=Decimal("3000.00"),
            payment_method="cash",
        )

    def test_user_profile_contains_payment_history(self):
        """Собственный профиль содержит историю платежей."""

        response = self.client.get(f"/api/users/{self.user.id}/")

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            response.data["email"],
            "profile@example.com",
        )

        self.assertEqual(
            len(response.data["payments"]),
            2,
        )

    def test_payment_history_contains_nested_data(self):
        """История содержит данные оплаченных курсов и уроков."""

        response = self.client.get(f"/api/users/{self.user.id}/")

        self.assertEqual(response.status_code, 200)

        payments = response.data["payments"]

        course_payment = next(
            payment for payment in payments if payment["course"] is not None
        )

        lesson_payment = next(
            payment for payment in payments if payment["lesson"] is not None
        )

        self.assertEqual(
            course_payment["course"]["title"],
            "Основы Python",
        )

        self.assertEqual(
            course_payment["course"]["lessons_count"],
            1,
        )

        self.assertEqual(
            len(course_payment["course"]["lessons"]),
            1,
        )

        self.assertEqual(
            lesson_payment["lesson"]["title"],
            "Переменные",
        )

        # Чужой профиль показывает только публичные сведения.
        other_response = self.client.get(f"/api/users/{self.other_user.id}/")

        self.assertEqual(other_response.status_code, 200)

        self.assertNotIn(
            "payments",
            other_response.data,
        )

        self.assertNotIn(
            "email",
            other_response.data,
        )

        self.assertNotIn(
            "last_name",
            other_response.data,
        )

        self.assertNotIn(
            "password",
            other_response.data,
        )
