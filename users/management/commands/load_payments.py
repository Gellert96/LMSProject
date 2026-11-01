from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from lms.models import Course, Lesson
from users.models import Payment


class Command(BaseCommand):
    help = "Создаёт тестовые курсы, уроки и платежи."

    def handle(self, *args, **options):
        User = get_user_model()

        user = User.objects.filter(is_superuser=True).first()

        if user is None:
            raise CommandError(
                "Сначала создайте суперпользователя командой createsuperuser."
            )

        course_python, _ = Course.objects.get_or_create(
            title="Python для начинающих",
            defaults={
                "description": "Базовый курс программирования на Python.",
                "owner": user,
            },
        )

        course_django, _ = Course.objects.get_or_create(
            title="Разработка на Django",
            defaults={
                "description": "Создание веб-приложений на Django.",
            },
        )

        lesson_python, _ = Lesson.objects.get_or_create(
            course=course_python,
            title="Переменные и типы данных",
            defaults={
                "description": "Изучение переменных Python.",
                "video_url": "https://example.com/python-variables",
            },
        )

        lesson_django, _ = Lesson.objects.get_or_create(
            course=course_django,
            title="Модели Django",
            defaults={
                "description": "Работа с моделями Django.",
                "video_url": "https://example.com/django-models",
            },
        )

        payments = [
            {
                "payment_date": date(2026, 10, 1),
                "course": course_python,
                "lesson": None,
                "amount": Decimal("15000.00"),
                "payment_method": Payment.PaymentMethod.CASH,
            },
            {
                "payment_date": date(2026, 10, 5),
                "course": course_django,
                "lesson": None,
                "amount": Decimal("20000.00"),
                "payment_method": Payment.PaymentMethod.TRANSFER,
            },
            {
                "payment_date": date(2026, 10, 10),
                "course": None,
                "lesson": lesson_python,
                "amount": Decimal("3000.00"),
                "payment_method": Payment.PaymentMethod.CASH,
            },
            {
                "payment_date": date(2026, 10, 15),
                "course": None,
                "lesson": lesson_django,
                "amount": Decimal("4500.00"),
                "payment_method": Payment.PaymentMethod.TRANSFER,
            },
            {
                "payment_date": date(2026, 10, 20),
                "course": course_python,
                "lesson": None,
                "amount": Decimal("15000.00"),
                "payment_method": Payment.PaymentMethod.TRANSFER,
            },
        ]

        created_count = 0

        for payment_data in payments:
            _, created = Payment.objects.get_or_create(
                user=user,
                **payment_data,
            )

            if created:
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Добавлено платежей: {created_count}. "
                f"Всего платежей: {Payment.objects.count()}."
            )
        )
