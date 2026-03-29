from django.db import models
from hackathons.models import Hackathon


class Announcement(models.Model):
    hackathon = models.ForeignKey(
        Hackathon,
        on_delete=models.CASCADE,
        related_name="announcements"
    )
    title = models.CharField(max_length=255)
    content = models.TextField()
    published_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "announcements"

    def __str__(self):
        return self.title