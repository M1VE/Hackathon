from django.contrib import admin
from .models import Team, TeamMember


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ("id", "team_name", "hackathon", "captain", "mentor", "is_open_for_random_join")
    search_fields = (
        "team_name",
        "captain__email",
        "captain__full_name",
        "mentor__email",
        "mentor__full_name",
        "hackathon__title",
    )
    autocomplete_fields = ("hackathon", "captain", "mentor")


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ("id", "team", "user", "role_in_team")
    search_fields = ("team__team_name", "user__email", "user__full_name")
    autocomplete_fields = ("team", "user")