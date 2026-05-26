from django.contrib.auth.models import AbstractUser
from django.db import models


class University(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        db_table = "universities"
        verbose_name = "University"
        verbose_name_plural = "Universities"

    def __str__(self):
        return self.name


class User(AbstractUser):
    ROLE_CHOICES = [
        ("participant", "Participant"),
        ("organizer", "Organizer"),
        ("judge", "Judge"),
        ("mentor", "Mentor"),
        ("admin", "Admin"),
    ]

    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="participant")
    university = models.ForeignKey(
        University,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users",
    )

    wins = models.IntegerField(default=0)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "full_name"]

    class Meta:
        db_table = "users"

    def __str__(self):
        return self.email
