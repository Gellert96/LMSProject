from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Создаёт группу модераторов."

    def handle(self, *args, **options):
        _group, created = Group.objects.get_or_create(name="moderators")

        if created:
            self.stdout.write(self.style.SUCCESS("Группа moderators успешно создана."))
        else:
            self.stdout.write(self.style.WARNING("Группа moderators уже существует."))
