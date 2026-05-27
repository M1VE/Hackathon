from django.urls import path

from . import views


urlpatterns = [
    path("", views.home, name="home"),
    path(
        "hackathons/<int:hackathon_id>/leaderboard/",
        views.leaderboard_view,
        name="leaderboard",
    ),
    path(
        "projects/<int:project_id>/",
        views.project_detail,
        name="project_detail",
    ),
    path(
        "hackathons/<int:hackathon_id>/teams/",
        views.hackathon_teams_view,
        name="hackathon_teams",
    ),
    path(
        "hackathons/<int:hackathon_id>/teams/<int:team_id>/join/",
        views.join_open_team,
        name="join_open_team",
    ),
    path(
        "hackathons/<int:hackathon_id>/auto-assign-mentors/",
        views.auto_assign_mentors,
        name="auto_assign_mentors",
    ),
    path(
        "teams/<int:team_id>/assign-mentor/",
        views.assign_team_mentor,
        name="assign_team_mentor",
    ),
    # Авторизация и регистрация
    path("register/", views.register_view, name="site_register"),
    path("login/", views.login_view, name="site_login"),
    path("logout/", views.logout_view, name="site_logout"),
    # Личные кабинеты (Dashboards)
    path("dashboard/", views.dashboard, name="dashboard"),
    path(
        "dashboard/participant/",
        views.participant_dashboard,
        name="participant_dashboard",
    ),
    path("dashboard/mentor/", views.mentor_dashboard, name="mentor_dashboard"),
    path("dashboard/organizer/", views.organizer_dashboard, name="organizer_dashboard"),
    path("dashboard/judge/", views.judge_dashboard, name="judge_dashboard"),
    # Хакатоны (общий доступ)
    path("hackathons/", views.hackathon_list, name="hackathon_list"),
    path("hackathons/<int:pk>/", views.hackathon_detail, name="hackathon_detail"),
    path("hackathons/<int:pk>/join/", views.join_hackathon, name="join_hackathon"),
    # Команды
    path("hackathons/<int:pk>/create-team/", views.create_team, name="create_team"),
    path(
        "hackathons/<int:pk>/join-random-team/",
        views.join_random_team,
        name="join_random_team",
    ),
    path(
        "hackathons/<int:pk>/join-team-by-code/",
        views.join_team_by_code_form,
        name="join_team_by_code",
    ),
    path(
        "hackathons/<int:pk>/join-open-team/<int:team_id>/",
        views.join_open_team,
        name="join_open_team",
    ),
    path("teams/<int:team_id>/", views.team_detail, name="team_detail"),
    # Проекты и оценка
    path(
        "participant/hackathons/<int:pk>/submit-project/",
        views.submit_project,
        name="submit_project",
    ),
    path(
        "judge/projects/<int:project_id>/score/",
        views.score_project,
        name="score_project",
    ),
    # Функционал организатора
    path(
        "organizer/hackathons/create/", views.create_hackathon, name="create_hackathon"
    ),
    path(
        "organizer/hackathons/<int:pk>/manage/",
        views.manage_hackathon,
        name="manage_hackathon",
    ),
    path(
        "organizer/hackathons/<int:pk>/edit/",
        views.edit_hackathon,
        name="edit_hackathon",
    ),
    path(
        "organizer/hackathons/<int:pk>/delete/",
        views.delete_hackathon,
        name="delete_hackathon",
    ),
    path(
        "organizer/hackathons/<int:pk>/criteria/create/",
        views.create_criterion,
        name="create_criterion",
    ),
    path(
        "organizer/hackathons/<int:pk>/assign-judge/",
        views.assign_judge,
        name="assign_judge",
    ),
    path(
        "organizer/hackathons/<int:pk>/assign-project/",
        views.assign_project_to_judge,
        name="assign_project",
    ),
]
