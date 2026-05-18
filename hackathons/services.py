from django.utils import timezone
from .models import Hackathon, HackathonStage


def update_hackathon_status(hackathon):
    now = timezone.now()

    stages = {
        stage.stage_name: stage.deadline
        for stage in HackathonStage.objects.filter(hackathon=hackathon)
    }

    if "registration" in stages and now <= stages["registration"]:
        new_status = "registration"

    elif "team_building" in stages and now <= stages["team_building"]:
        new_status = "team_building"

    elif "submission" in stages and now <= stages["submission"]:
        new_status = "submission"

    elif "judging" in stages and now <= stages["judging"]:
        new_status = "judging"

    elif "results" in stages and now <= stages["results"]:
        new_status = "finished"

    else:
        new_status = "archived"

    if hackathon.status != new_status:
        hackathon.status = new_status
        hackathon.save(update_fields=["status"])