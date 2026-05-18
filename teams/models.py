import uuid
from django.conf import settings
from django.db import models
from hackathons.models import Hackathon


class Team(models.Model):
    hackathon = models.ForeignKey(
        Hackathon,
        on_delete=models.CASCADE,
        related_name="teams"
    )

    team_name = models.CharField(max_length=100)

    captain = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="captain_teams"
    )

    mentor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="mentored_teams"
    )

    invite_code = models.CharField(max_length=20, unique=True, blank=True)
    mentor_invite_code = models.CharField(max_length=20, unique=True, blank=True)

    is_open_for_random_join = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "teams"
        unique_together = ("hackathon", "team_name")

    def save(self, *args, **kwargs):
        if not self.invite_code:
            self.invite_code = uuid.uuid4().hex[:10].upper()

        if not self.mentor_invite_code:
            self.mentor_invite_code = "M-" + uuid.uuid4().hex[:8].upper()

        super().save(*args, **kwargs)

    def __str__(self):
        return self.team_name


class TeamMember(models.Model):
    ROLE_IN_TEAM_CHOICES = [
        ("captain", "Captain"),
        ("member", "Member"),
    ]

    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name="members"
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="team_memberships"
    )

    role_in_team = models.CharField(
        max_length=50,
        default="member",
        choices=ROLE_IN_TEAM_CHOICES
    )

    class Meta:
        db_table = "team_members"
        unique_together = ("team", "user")

    def __str__(self):
        return f"{self.user.email} - {self.team.team_name}"