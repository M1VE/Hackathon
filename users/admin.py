from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, University


@admin.register(University)
class UniversityAdmin(admin.ModelAdmin):
    search_fields = ("name",)
    list_display = ("id", "name")


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        "id",
        "username",
        "email",
        "full_name",
        "role",
        "university",
        "is_active",
        "is_staff",
    )
    list_filter = ("role", "university", "is_active", "is_staff")
    search_fields = ("username", "email", "full_name")
    ordering = ("id",)

    fieldsets = (
        ("Основное", {"fields": ("username", "password")}),
        (
            "Профиль",
            {
                "fields": (
                    "email",
                    "full_name",
                    "role",
                    "university",
                )
            },
        ),
        ("Доступ", {"fields": ("is_active", "is_staff", "is_superuser")}),
    )

    add_fieldsets = (
        (
            "Создание пользователя",
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "email",
                    "full_name",
                    "role",
                    "university",
                    "password1",
                    "password2",
                    "is_active",
                    "is_staff",
                ),
            },
        ),
    )
