from django.contrib import admin
from .models import Hackathon, HackathonAttachment, HackathonStage, HackathonParticipant


class HackathonAttachmentInline(admin.TabularInline):
    model = HackathonAttachment
    extra = 1


@admin.register(Hackathon)
class HackathonAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "organizer",
        "format",
        "status",
        "is_active",
        "min_team_size",
        "max_team_size",
        "created_at",
    )
    list_filter = (
        "status",
        "format",
        "is_active",
        "allow_random_teaming",
        "allow_mentor_assignment",
    )
    search_fields = (
        "title",
        "description",
        "organizer__email",
        "organizer__full_name",
    )
    autocomplete_fields = ("organizer",)
    ordering = ("-created_at",)
    inlines = [HackathonAttachmentInline]


@admin.register(HackathonAttachment)
class HackathonAttachmentAdmin(admin.ModelAdmin):
    list_display = ("id", "hackathon", "title", "file", "uploaded_at")
    search_fields = ("hackathon__title", "title")
    autocomplete_fields = ("hackathon",)


@admin.register(HackathonStage)
class HackathonStageAdmin(admin.ModelAdmin):
    list_display = ("id", "hackathon", "stage_name", "deadline")
    list_filter = ("stage_name",)
    search_fields = ("hackathon__title",)
    autocomplete_fields = ("hackathon",)
    ordering = ("deadline",)


@admin.register(HackathonParticipant)
class HackathonParticipantAdmin(admin.ModelAdmin):
    list_display = ("id", "hackathon", "user", "registration_date")
    search_fields = ("hackathon__title", "user__email", "user__full_name")
    autocomplete_fields = ("hackathon", "user")
    ordering = ("-registration_date",)