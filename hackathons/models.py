from django.conf import settings
from django.db import models


class Hackathon(models.Model):
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("registration", "Registration"),
        ("team_building", "Team Building"),
        ("submission", "Submission"),
        ("judging", "Judging"),
        ("finished", "Finished"),
        ("archived", "Archived"),
    ]

    FORMAT_CHOICES = [
        ("intra", "Intra-university"),
        ("inter", "Inter-university"),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="organized_hackathons",
    )

    format = models.CharField(
        max_length=20,
        choices=FORMAT_CHOICES,
        default="intra",
    )

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default="draft",
    )

    is_active = models.BooleanField(default=True)

    min_team_size = models.PositiveIntegerField(default=2)
    max_team_size = models.PositiveIntegerField(default=5)

    allow_random_teaming = models.BooleanField(default=True)
    allow_mentor_assignment = models.BooleanField(default=True)
    max_mentors_per_team = models.PositiveIntegerField(default=1)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "hackathons"

    def __str__(self):
        return self.title


class HackathonStage(models.Model):
    STAGE_CHOICES = [
        ("registration", "Registration"),
        ("team_building", "Team Building"),
        ("submission", "Submission"),
        ("judging", "Judging"),
        ("results", "Results"),
    ]

    hackathon = models.ForeignKey(
        Hackathon,
        on_delete=models.CASCADE,
        related_name="stages",
    )

    stage_name = models.CharField(
        max_length=100,
        choices=STAGE_CHOICES,
    )

    deadline = models.DateTimeField()

    class Meta:
        db_table = "hackathon_stages"
        unique_together = ("hackathon", "stage_name")

    def __str__(self):
        return f"{self.hackathon.title} - {self.stage_name}"


class HackathonParticipant(models.Model):
    hackathon = models.ForeignKey(
        Hackathon,
        on_delete=models.CASCADE,
        related_name="participants",
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="hackathon_participations",
    )

    registration_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "hackathon_participants"
        unique_together = ("hackathon", "user")

    def __str__(self):
        return f"{self.user.email} -> {self.hackathon.title}"