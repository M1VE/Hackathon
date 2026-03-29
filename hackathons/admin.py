from django.contrib import admin
from .models import Hackathon, HackathonStage, HackathonParticipant


@admin.register(Hackathon)
class HackathonAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "organizer", "format", "status", "is_published", "is_active")
    search_fields = ("title", "organizer__email", "organizer__full_name")
    autocomplete_fields = ("organizer",)


@admin.register(HackathonStage)
class HackathonStageAdmin(admin.ModelAdmin):
    list_display = ("id", "hackathon", "stage_name", "deadline")
    autocomplete_fields = ("hackathon",)


@admin.register(HackathonParticipant)
class HackathonParticipantAdmin(admin.ModelAdmin):
    list_display = ("id", "hackathon", "user", "registration_date")
    search_fields = ("user__email", "user__full_name", "hackathon__title")
    autocomplete_fields = ("hackathon", "user")