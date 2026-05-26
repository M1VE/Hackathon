from django.utils import timezone
from .models import Hackathon, HackathonStage
from projects.models import Project, calculate_project_score


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

        if new_status == "finished":
            award_winners(hackathon)


def get_hackathon_leaderboard(hackathon):
    leaderboard = []
    projects = Project.objects.filter(team__hackathon=hackathon).select_related("team")

    for project in projects:
        total_score = calculate_project_score(project)
        leaderboard.append(
            {"team": project.team, "project": project, "score": total_score}
        )

    leaderboard.sort(key=lambda x: x["score"], reverse=True)

    for index, item in enumerate(leaderboard, start=1):
        item["place"] = index

    return leaderboard


def award_winners(hackathon):
    from teams.models import TeamMember
    from django.contrib.auth import get_user_model

    User = get_user_model()
    leaderboard = get_hackathon_leaderboard(hackathon)
    top3 = [item for item in leaderboard if item["place"] <= 3]

    for item in top3:
        team = item["team"]
        members = TeamMember.objects.filter(team=team).select_related("user")
        for member in members:
            member.user.wins += 1
            member.user.save(update_fields=["wins"])