from django.core.management import BaseCommand
from users.models import User


class Command(BaseCommand):
    help = "Добавление суперюзера"

    def handle(self, *args, **options):
        # Проверяем, не существует ли уже суперпользователь
        if User.objects.filter(email="admin@admin.com").exists():
            self.stdout.write(
                self.style.WARNING("⚠️ Суперпользователь уже существует!")
            )
            return

        # Создаем суперпользователя
        super_user = User.objects.create(
            email="admin@admin.com",
            username="admin",
            first_name="Admin",
            last_name="Admin",
            is_staff=True,
            is_active=True,
            is_superuser=True,
            is_employee=True,
        )
        super_user.set_password("1234qwer")
        super_user.save()

        self.stdout.write(
            self.style.SUCCESS("✅ Суперпользователь успешно создан!")
        )
