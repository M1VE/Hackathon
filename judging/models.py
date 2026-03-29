from django.conf import settings
from django.db import models
from hackathons.models import Hackathon
from projects.models import Project


class Criterion(models.Model):
    hackathon = models.ForeignKey(
        Hackathon,
        on_delete=models.CASCADE,
        related_name="criteria"
    )
    name = models.CharField(max_length=100)
    max_score = models.IntegerField(default=10)
    weight = models.DecimalField(max_digits=5, decimal_places=2, default=1.00)

    class Meta:
        db_table = "criteria"

    def __str__(self):
        return self.name


class Judge(models.Model):
    hackathon = models.ForeignKey(
        Hackathon,
        on_delete=models.CASCADE,
        related_name="judges"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="judge_hackathons"
    )

    class Meta:
        db_table = "judges"
        unique_together = ("hackathon", "user")

    def __str__(self):
        return f"{self.user.email} - {self.hackathon.title}"


class JudgeAssignment(models.Model):
    judge = models.ForeignKey(
        Judge,
        on_delete=models.CASCADE,
        related_name="assignments"
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="judge_assignments"
    )

    class Meta:
        db_table = "judge_assignments"
        unique_together = ("judge", "project")

    def __str__(self):
        return f"{self.judge} -> {self.project}"


class Score(models.Model):
    assignment = models.ForeignKey(
        JudgeAssignment,
        on_delete=models.CASCADE,
        related_name="scores"
    )
    criterion = models.ForeignKey(
        Criterion,
        on_delete=models.CASCADE,
        related_name="scores"
    )
    score_value = models.IntegerField()
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "scores"
        unique_together = ("assignment", "criterion")

    def __str__(self):
        return f"{self.assignment} - {self.criterion.name}: {self.score_value}"