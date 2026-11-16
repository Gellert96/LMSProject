from celery import shared_task
from django.conf import settings
from django.core.mail import send_mass_mail

from lms.models import Course


@shared_task(ignore_result=True)
def notify_course_subscribers(course_id):
    """Отправляет подписчикам уведомление об обновлении курса."""

    course = Course.objects.filter(pk=course_id).first()
    if course is None:
        return 0

    emails = (
        course.subscriptions.filter(user__is_active=True)
        .exclude(user__email="")
        .values_list("user__email", flat=True)
    )
    messages = [
        (
            f"Обновление курса «{course.title}»",
            f"В курсе «{course.title}» обновились учебные материалы.",
            settings.DEFAULT_FROM_EMAIL,
            [email],
        )
        for email in emails
    ]

    return send_mass_mail(messages) if messages else 0