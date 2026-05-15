from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),

    path("register/", views.register_view, name="site_register"),
    path("login/", views.login_view, name="site_login"),
    path("logout/", views.logout_view, name="site_logout"),

    path("dashboard/", views.dashboard, name="dashboard"),
    path("dashboard/participant/", views.participant_dashboard, name="participant_dashboard"),
    path("dashboard/mentor/", views.mentor_dashboard, name="mentor_dashboard"),
    path("dashboard/organizer/", views.organizer_dashboard, name="organizer_dashboard"),
    path("dashboard/judge/", views.judge_dashboard, name="judge_dashboard"),

    path("hackathons/", views.hackathon_list, name="hackathon_list"),
    path("hackathons/<int:pk>/", views.hackathon_detail, name="hackathon_detail"),
    path("hackathons/<int:pk>/join/", views.join_hackathon, name="join_hackathon"),

    path("organizer/hackathons/create/", views.create_hackathon, name="create_hackathon"),
    path("organizer/hackathons/<int:pk>/manage/", views.manage_hackathon, name="manage_hackathon"),
    path("organizer/hackathons/<int:pk>/edit/", views.edit_hackathon, name="edit_hackathon"),
    path("organizer/hackathons/<int:pk>/criteria/create/", views.create_criterion, name="create_criterion"),
    path("organizer/hackathons/<int:pk>/assign-judge/", views.assign_judge, name="assign_judge"),
    path("organizer/hackathons/<int:pk>/assign-project/", views.assign_project_to_judge, name="assign_project"),

    path("hackathons/<int:pk>/create-team/", views.create_team, name="create_team"),
    path("teams/<int:team_id>/", views.team_detail, name="team_detail"),
    path("teams/<int:team_id>/invite/", views.invite_member, name="invite_member"),
    path("teams/<int:team_id>/join/<str:invite_code>/", views.join_team_by_code, name="join_team_by_code"),

    path("participant/hackathons/<int:pk>/submit-project/", views.submit_project, name="submit_project"),

    path("judge/assignments/<int:assignment_id>/score/", views.score_project, name="score_project"),
]