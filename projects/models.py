from django.db import models
from teams.models import Team


class Project(models.Model):
    team = models.OneToOneField(
        Team,
        on_delete=models.CASCADE,
        related_name="project"
    )

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    technologies = models.TextField(blank=True, null=True)

    repository_url = models.TextField(blank=True, null=True)

    project_file = models.FileField(upload_to="projects/files/", blank=True, null=True)
    presentation_file = models.FileField(upload_to="projects/presentations/", blank=True, null=True)
    image_file = models.ImageField(upload_to="projects/images/", blank=True, null=True)
    video_file = models.FileField(upload_to="projects/videos/", blank=True, null=True)

    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "projects"

    def __str__(self):
        return self.title