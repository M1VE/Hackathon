import os

from django.core.management.base import BaseCommand

from users.models import University, User


class Command(BaseCommand):
    help = "Создаёт тестовые аккаунты в локальной SQLite (не трогает PostgreSQL команды)."

    def handle(self, *args, **options):
        if os.getenv("USE_SQLITE", "False") != "True":
            self.stdout.write(
                self.style.WARNING(
                    "Команда только для локальной разработки. В .env должно быть USE_SQLITE=True"
                )
            )
            return

        university, _ = University.objects.get_or_create(name="Demo University")

        accounts = [
            {
                "email": "participant@demo.local",
                "full_name": "Demo Participant",
                "role": "participant",
                "password": "demo1234",
            },
            {
                "email": "mentor@demo.local",
                "full_name": "Demo Mentor",
                "role": "mentor",
                "password": "demo1234",
            },
            {
                "email": "organizer@demo.local",
                "full_name": "Demo Organizer",
                "role": "organizer",
                "password": "demo1234",
            },
        ]

        for data in accounts:
            user, created = User.objects.get_or_create(
                email=data["email"],
                defaults={
                    "username": data["email"],
                    "full_name": data["full_name"],
                    "role": data["role"],
                    "university": university,
                },
            )
            if created:
                user.set_password(data["password"])
                user.save()
                self.stdout.write(self.style.SUCCESS(f"Создан: {data['email']}"))
            else:
                user.set_password(data["password"])
                user.role = data["role"]
                user.university = university
                user.save()
                self.stdout.write(self.style.WARNING(f"Обновлён: {data['email']}"))

        admin_email = "admin@demo.local"
        if User.objects.filter(email=admin_email).exists():
            admin = User.objects.get(email=admin_email)
            admin.set_password("admin1234")
            admin.is_staff = True
            admin.is_superuser = True
            admin.save()
            self.stdout.write(self.style.WARNING(f"Обновлён админ: {admin_email}"))
        else:
            admin = User.objects.create_user(
                email=admin_email,
                username=admin_email,
                password="admin1234",
                full_name="Demo Admin",
                role="admin",
                university=university,
            )
            admin.is_staff = True
            admin.is_superuser = True
            admin.save()
            self.stdout.write(self.style.SUCCESS(f"Создан админ: {admin_email}"))

        self.stdout.write("")
        self.stdout.write("Локальные аккаунты для входа на /login/:")
        self.stdout.write("  participant@demo.local / demo1234")
        self.stdout.write("  mentor@demo.local      / demo1234")
        self.stdout.write("  organizer@demo.local   / demo1234")
        self.stdout.write("  admin@demo.local       / admin1234  (Django admin: /admin/)")
