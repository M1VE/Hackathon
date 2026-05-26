import random

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from users.models import User, University
from hackathons.models import (
    Hackathon,
    HackathonParticipant,
    HackathonStage,
    HackathonAttachment,
)
from hackathons.services import update_hackathon_status, get_hackathon_leaderboard
from teams.models import Team, TeamMember
from projects.models import Project
from judging.models import Criterion, Judge, JudgeAssignment, Score
from itertools import cycle


def assign_team_mentor(request, team_id):

    team = get_object_or_404(Team, id=team_id)

    if request.method == "POST":
        mentor_id = request.POST.get("mentor_id")

        mentor = get_object_or_404(User, id=mentor_id, role="mentor")

        team.mentor = mentor
        team.save()

        return redirect("team_detail", team.id)

    mentors = User.objects.filter(role="mentor")

    return render(
        request, "assign_team_mentor.html", {"team": team, "mentors": mentors}
    )


def hackathon_teams_view(request, hackathon_id):

    hackathon = get_object_or_404(Hackathon, id=hackathon_id)

    teams = Team.objects.filter(hackathon=hackathon).select_related("captain", "mentor")

    return render(request, "teams_list.html", {"hackathon": hackathon, "teams": teams})


def leaderboard_view(request, hackathon_id):

    hackathon = get_object_or_404(Hackathon, id=hackathon_id)

    # leaderboard доступен только после завершения

    if hackathon.status not in ["finished", "archived"]:
        return redirect("hackathon_detail", hackathon.id)

    leaderboard = get_hackathon_leaderboard(hackathon)

    return render(
        request,
        "leaderboard.html",
        {"hackathon": hackathon, "leaderboard": leaderboard},
    )


def role_required(allowed_roles):
    def decorator(view_func):
        @login_required
        def wrapper(request, *args, **kwargs):
            if request.user.role not in allowed_roles:
                messages.error(request, "У вас нет доступа к этой странице.")
                return redirect("dashboard")
            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator


def home(request):

    # Получаем все хакатоны кроме draft
    all_hackathons = Hackathon.objects.exclude(status="draft").order_by("-created_at")

    # Обновляем статусы
    for hackathon in all_hackathons:
        update_hackathon_status(hackathon)

    # Активные хакатоны
    active_hackathons = (
        Hackathon.objects.filter(status__in=["active", "registration"], is_active=True)
        .exclude(status="draft")
        .order_by("-created_at")[:6]
    )

    # Завершённые / архивные
    past_hackathons = (
        Hackathon.objects.filter(status__in=["finished", "archived"])
        .exclude(status="draft")
        .order_by("-created_at")[:6]
    )

    return render(
        request,
        "home.html",
        {
            "active_hackathons": active_hackathons,
            "past_hackathons": past_hackathons,
        },
    )


def register_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    universities = University.objects.all().order_by("name")

    if request.method == "POST":
        email = request.POST.get("email")
        username = request.POST.get("username")
        full_name = request.POST.get("full_name")
        password = request.POST.get("password")
        role = request.POST.get("role")
        university_id = request.POST.get("university")

        if role not in ["participant", "mentor"]:
            messages.error(
                request,
                "Через сайт можно зарегистрироваться только как участник или ментор.",
            )
            return redirect("site_register")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Пользователь с таким email уже существует.")
            return redirect("site_register")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Такое имя пользователя уже занято.")
            return redirect("site_register")

        university = University.objects.filter(id=university_id).first()

        if university is None:
            messages.error(request, "Выберите университет.")
            return redirect("site_register")

        user = User.objects.create_user(
            email=email,
            username=username,
            full_name=full_name,
            password=password,
            role=role,
            university=university,
            is_open_for_teaming=request.POST.get("is_open_for_teaming") == "on",
        )

        login(request, user)
        messages.success(request, "Регистрация прошла успешно.")
        return redirect("dashboard")

    return render(
        request,
        "register.html",
        {
            "universities": universities,
        },
    )


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, username=email, password=password)

        if user is None:
            messages.error(request, "Неверный email или пароль.")
            return redirect("site_login")

        login(request, user)
        return redirect("dashboard")

    return render(request, "login.html")


@login_required
def logout_view(request):
    logout(request)
    return redirect("home")


@login_required
def dashboard(request):
    if request.user.role == "participant":
        return redirect("participant_dashboard")

    if request.user.role == "mentor":
        return redirect("mentor_dashboard")

    if request.user.role == "organizer":
        return redirect("organizer_dashboard")

    if request.user.role == "judge":
        return redirect("judge_dashboard")

    if request.user.role == "admin" or request.user.is_superuser:
        return redirect("/admin/")

    messages.error(request, "Для вашей роли не найден кабинет.")
    return redirect("home")


@role_required(["participant"])
def participant_dashboard(request):
    from django.db.models import Case, When, IntegerField

    participations = HackathonParticipant.objects.filter(
        user=request.user
    ).select_related("hackathon")

    hackathons = sorted(
        [p.hackathon for p in participations],
        key=lambda h: (h.status in ["archived", "finished"]),
    )

    status_order = Case(
        When(team__hackathon__status="registration", then=0),
        When(team__hackathon__status="team_building", then=1),
        When(team__hackathon__status="submission", then=2),
        When(team__hackathon__status="judging", then=3),
        When(team__hackathon__status="finished", then=4),
        When(team__hackathon__status="archived", then=5),
        default=6,
        output_field=IntegerField(),
    )

    teams = TeamMember.objects.filter(user=request.user).select_related(
        "team", "team__hackathon"
    ).annotate(status_order=status_order).order_by("status_order")

    return render(
        request,
        "participant_dashboard.html",
        {
            "participations": participations,
            "teams": teams,
            "hackathons": hackathons,
        },
    )


@role_required(["mentor"])
def mentor_dashboard(request):
    teams = Team.objects.filter(mentor=request.user).select_related(
        "hackathon", "captain"
    )

    return render(
        request,
        "mentor_dashboard.html",
        {
            "teams": teams,
        },
    )


@role_required(["organizer"])
def organizer_dashboard(request):
    hackathons = Hackathon.objects.filter(organizer=request.user).order_by(
        "-created_at"
    )

    for hackathon in hackathons:
        update_hackathon_status(hackathon)

    return render(
        request,
        "organizer_dashboard.html",
        {
            "hackathons": hackathons,
        },
    )


@role_required(["judge"])
def judge_dashboard(request):
    judge_records = Judge.objects.filter(user=request.user).select_related("hackathon")

    for judge_record in judge_records:
        update_hackathon_status(judge_record.hackathon)

    hackathons = [judge_record.hackathon for judge_record in judge_records]

    projects = Project.objects.filter(
        team__hackathon__in=hackathons, team__hackathon__status="judging"
    ).select_related("team", "team__hackathon")

    return render(
        request,
        "judge_dashboard.html",
        {
            "judge_records": judge_records,
            "projects": projects,
        },
    )


def hackathon_list(request):
    hackathons = Hackathon.objects.filter(is_active=True).order_by("-created_at")

    for hackathon in hackathons:
        update_hackathon_status(hackathon)

    visible_hackathons = []

    for hackathon in hackathons:
        if hackathon.status != "draft":
            visible_hackathons.append(hackathon)
        elif (
            request.user.is_authenticated
            and request.user.role == "organizer"
            and hackathon.organizer == request.user
        ):
            visible_hackathons.append(hackathon)

    return render(
        request,
        "hackathon_list.html",
        {
            "hackathons": visible_hackathons,
        },
    )


def hackathon_detail(request, pk):
    hackathon = get_object_or_404(Hackathon, pk=pk)
    update_hackathon_status(hackathon)

    if hackathon.status == "draft":
        if not request.user.is_authenticated or hackathon.organizer != request.user:
            messages.error(request, "Этот хакатон пока находится в черновике.")
            return redirect("hackathon_list")

    is_joined = False
    user_team = None
    project = None

    if request.user.is_authenticated:
        is_joined = HackathonParticipant.objects.filter(
            hackathon=hackathon, user=request.user
        ).exists()

        membership = (
            TeamMember.objects.filter(team__hackathon=hackathon, user=request.user)
            .select_related("team")
            .first()
        )

        if membership:
            user_team = membership.team
            project = Project.objects.filter(team=user_team).first()

    open_teams = Team.objects.filter(
        hackathon=hackathon, is_open_for_random_join=True
    ).select_related("captain", "mentor", "captain__university")

    attachments = HackathonAttachment.objects.filter(hackathon=hackathon)

    return render(
        request,
        "hackathon_detail.html",
        {
            "hackathon": hackathon,
            "is_joined": is_joined,
            "user_team": user_team,
            "project": project,
            "open_teams": open_teams,
            "attachments": attachments,
        },
    )


@login_required
def join_hackathon(request, pk):
    hackathon = get_object_or_404(Hackathon, pk=pk)
    update_hackathon_status(hackathon)

    if hackathon.status not in ["registration"]:
        messages.error(request, "Регистрация на этот хакатон сейчас закрыта.")
        return redirect("hackathon_detail", pk=pk)

    if request.user.role not in ["participant", "mentor"]:
        messages.error(
            request, "На хакатон могут регистрироваться только участники и менторы."
        )
        return redirect("hackathon_detail", pk=pk)

    if hackathon.format == "intra":
        organizer_university = hackathon.organizer.university
        if organizer_university and request.user.university != organizer_university:
            messages.error(
                request,
                "Этот хакатон внутривузовский. Участвовать могут только студенты университета-организатора.",
            )
            return redirect("hackathon_detail", pk=pk)
    HackathonParticipant.objects.get_or_create(hackathon=hackathon, user=request.user)

    messages.success(request, "Вы зарегистрировались на хакатон.")
    return redirect("hackathon_detail", pk=pk)


@role_required(["organizer"])
def create_hackathon(request):
    if request.method == "POST":
        hackathon = Hackathon.objects.create(
            title=request.POST.get("title"),
            description=request.POST.get("description"),
            organizer=request.user,
            format=request.POST.get("format"),
            status=request.POST.get("status", "draft"),
            is_active=True,
            min_team_size=request.POST.get("min_team_size") or 2,
            max_team_size=request.POST.get("max_team_size") or 5,
            allow_random_teaming=request.POST.get("allow_random_teaming") == "on",
            allow_mentor_assignment=request.POST.get("allow_mentor_assignment") == "on",
            cover_image=request.FILES.get("cover_image"),
        )

        attachment_files = request.FILES.getlist("attachments")
        for file in attachment_files:
            HackathonAttachment.objects.create(
                hackathon=hackathon, title=file.name, file=file
            )

        stages = {
            "registration": request.POST.get("registration_deadline"),
            "team_building": request.POST.get("team_building_deadline"),
            "submission": request.POST.get("submission_deadline"),
            "judging": request.POST.get("judging_deadline"),
            "results": request.POST.get("results_deadline"),
        }

        for stage_name, deadline in stages.items():
            if deadline:
                HackathonStage.objects.create(
                    hackathon=hackathon,
                    stage_name=stage_name,
                    deadline=deadline,
                )

        messages.success(request, "Хакатон создан.")
        return redirect("organizer_dashboard")

    return render(request, "create_hackathon.html")


@role_required(["organizer"])
def edit_hackathon(request, pk):
    hackathon = get_object_or_404(Hackathon, pk=pk, organizer=request.user)

    if request.method == "POST":
        hackathon.title = request.POST.get("title")
        hackathon.description = request.POST.get("description")
        hackathon.format = request.POST.get("format")
        hackathon.status = request.POST.get("status")
        hackathon.is_active = request.POST.get("is_active") == "on"
        hackathon.min_team_size = request.POST.get("min_team_size") or 2
        hackathon.max_team_size = request.POST.get("max_team_size") or 5
        hackathon.allow_random_teaming = (
            request.POST.get("allow_random_teaming") == "on"
        )
        hackathon.allow_mentor_assignment = (
            request.POST.get("allow_mentor_assignment") == "on"
        )
        hackathon.max_mentors_per_team = request.POST.get("max_mentors_per_team") or 1

        if request.FILES.get("cover_image"):
            hackathon.cover_image = request.FILES.get("cover_image")

        hackathon.save()

        attachment_files = request.FILES.getlist("attachments")
        for file in attachment_files:
            HackathonAttachment.objects.create(
                hackathon=hackathon, title=file.name, file=file
            )

        for stage_name in [
            "registration",
            "team_building",
            "submission",
            "judging",
            "results",
        ]:
            deadline = request.POST.get(f"{stage_name}_deadline")

            if deadline:
                HackathonStage.objects.update_or_create(
                    hackathon=hackathon,
                    stage_name=stage_name,
                    defaults={"deadline": deadline},
                )

        messages.success(request, "Хакатон обновлён.")
        return redirect("manage_hackathon", pk=hackathon.id)

    stage_map = {
        stage.stage_name: stage.deadline
        for stage in HackathonStage.objects.filter(hackathon=hackathon)
    }

    attachments = HackathonAttachment.objects.filter(hackathon=hackathon)

    return render(
        request,
        "edit_hackathon.html",
        {
            "hackathon": hackathon,
            "stage_map": stage_map,
            "attachments": attachments,
        },
    )


@role_required(["organizer"])
def delete_hackathon(request, pk):
    hackathon = get_object_or_404(Hackathon, pk=pk, organizer=request.user)

    if request.method == "POST":
        hackathon.delete()
        messages.success(request, "Хакатон удалён.")
        return redirect("organizer_dashboard")

    return render(
        request,
        "delete_hackathon.html",
        {
            "hackathon": hackathon,
        },
    )


@role_required(["organizer"])
def manage_hackathon(request, pk):
    hackathon = get_object_or_404(Hackathon, pk=pk, organizer=request.user)

    update_hackathon_status(hackathon)

    criteria = Criterion.objects.filter(hackathon=hackathon)
    teams = Team.objects.filter(hackathon=hackathon)
    projects = Project.objects.filter(team__hackathon=hackathon)
    judges = Judge.objects.filter(hackathon=hackathon).select_related("user")
    assignments = JudgeAssignment.objects.filter(
        judge__hackathon=hackathon
    ).select_related("judge", "judge__user", "project", "project__team")
    attachments = HackathonAttachment.objects.filter(hackathon=hackathon)

    return render(
        request,
        "manage_hackathon.html",
        {
            "hackathon": hackathon,
            "criteria": criteria,
            "teams": teams,
            "projects": projects,
            "judges": judges,
            "assignments": assignments,
            "attachments": attachments,
        },
    )


@role_required(["organizer"])
def create_criterion(request, pk):
    hackathon = get_object_or_404(Hackathon, pk=pk, organizer=request.user)

    if request.method == "POST":
        Criterion.objects.create(
            hackathon=hackathon,
            name=request.POST.get("name"),
            max_score=request.POST.get("max_score") or 10,
            weight=request.POST.get("weight") or 1,
        )

        messages.success(request, "Критерий создан.")
        return redirect("manage_hackathon", pk=hackathon.id)

    return render(
        request,
        "create_criterion.html",
        {
            "hackathon": hackathon,
        },
    )


@role_required(["organizer"])
def assign_judge(request, pk):
    hackathon = get_object_or_404(Hackathon, pk=pk, organizer=request.user)

    if request.method == "POST":
        judge_id = request.POST.get("judge_id")

        judge_user = User.objects.filter(id=judge_id, role="judge").first()

        if judge_user:
            Judge.objects.get_or_create(hackathon=hackathon, user=judge_user)
            messages.success(request, "Жюри назначено.")
            return redirect("manage_hackathon", pk=hackathon.id)

        messages.error(request, "Жюри не найдено.")
        return redirect("assign_judge", pk=hackathon.id)

    judges = User.objects.filter(role="judge")

    return render(
        request,
        "assign_judge.html",
        {
            "hackathon": hackathon,
            "judges": judges,
        },
    )


@role_required(["organizer"])
def assign_project_to_judge(request, pk):
    hackathon = get_object_or_404(Hackathon, pk=pk, organizer=request.user)

    if request.method == "POST":
        judge_record_id = request.POST.get("judge_record_id")
        project_id = request.POST.get("project_id")

        judge_record = Judge.objects.filter(
            id=judge_record_id, hackathon=hackathon
        ).first()

        project = Project.objects.filter(
            id=project_id, team__hackathon=hackathon
        ).first()

        if judge_record and project:
            JudgeAssignment.objects.get_or_create(judge=judge_record, project=project)
            messages.success(request, "Проект назначен жюри.")
            return redirect("manage_hackathon", pk=hackathon.id)

        messages.error(request, "Не удалось назначить проект.")
        return redirect("assign_project", pk=hackathon.id)

    judges = Judge.objects.filter(hackathon=hackathon).select_related("user")
    projects = Project.objects.filter(team__hackathon=hackathon)

    return render(
        request,
        "assign_project.html",
        {
            "hackathon": hackathon,
            "judges": judges,
            "projects": projects,
        },
    )


@role_required(["participant"])
def create_team(request, pk):
    hackathon = get_object_or_404(Hackathon, pk=pk)
    update_hackathon_status(hackathon)

    if hackathon.status not in ["team_building", "registration"]:
        messages.error(request, "Сейчас нельзя создавать команды.")
        return redirect("hackathon_detail", pk=pk)

    is_registered = HackathonParticipant.objects.filter(
        hackathon=hackathon, user=request.user
    ).exists()

    if not is_registered:
        messages.error(request, "Сначала зарегистрируйтесь на хакатон.")
        return redirect("hackathon_detail", pk=pk)

    already_in_team = TeamMember.objects.filter(
        team__hackathon=hackathon, user=request.user
    ).exists()

    if already_in_team:
        messages.error(request, "Вы уже состоите в команде этого хакатона.")
        return redirect("hackathon_detail", pk=pk)

    if request.method == "POST":
        team_name = request.POST.get("team_name")

        # Проверка: не превышено ли максимальное число команд по участникам
        # (капитан = 1 участник, минимум должен быть достижим)
        total_participants = HackathonParticipant.objects.filter(
            hackathon=hackathon
        ).count()
        existing_teams = Team.objects.filter(hackathon=hackathon).count()

        if existing_teams * hackathon.min_team_size >= total_participants:
            messages.error(
                request,
                f"Нельзя создать команду: недостаточно свободных участников. "
                f"Минимум в команде: {hackathon.min_team_size}."
            )
            return redirect("hackathon_detail", pk=pk)

        team = Team.objects.create(
            hackathon=hackathon,
            team_name=team_name,
            captain=request.user,
            is_open_for_random_join=request.POST.get("is_open_for_random_join") == "on",
        )

        TeamMember.objects.create(team=team, user=request.user, role_in_team="captain")

        messages.success(request, f"Команда создана. Максимум участников: {hackathon.max_team_size}.")
        return redirect("team_detail", team_id=team.id)

    return render(
        request,
        "create_team.html",
        {
            "hackathon": hackathon,
            "min_team_size": hackathon.min_team_size,
            "max_team_size": hackathon.max_team_size,
        },
    )


@role_required(["participant"])
def create_random_team(request, pk):
    hackathon = get_object_or_404(Hackathon, pk=pk)
    update_hackathon_status(hackathon)

    if hackathon.status not in ["team_building", "registration"]:
        messages.error(request, "Сейчас нельзя создавать команды.")
        return redirect("hackathon_detail", pk=pk)

    if not hackathon.allow_random_teaming:
        messages.error(
            request, "Случайное формирование команд отключено для этого хакатона."
        )
        return redirect("hackathon_detail", pk=pk)

    is_registered = HackathonParticipant.objects.filter(
        hackathon=hackathon, user=request.user
    ).exists()

    if not is_registered:
        messages.error(request, "Сначала зарегистрируйтесь на хакатон.")
        return redirect("hackathon_detail", pk=pk)

    if not request.user.is_open_for_teaming:
        messages.error(request, "Включите согласие на случайный подбор в профиле.")
        return redirect("hackathon_detail", pk=pk)

    already_in_team = TeamMember.objects.filter(
        team__hackathon=hackathon, user=request.user
    ).exists()

    if already_in_team:
        messages.error(request, "Вы уже состоите в команде этого хакатона.")
        return redirect("hackathon_detail", pk=pk)

    if not request.user.university:
        messages.error(request, "Для случайного подбора нужно указать университет.")
        return redirect("hackathon_detail", pk=pk)

    candidates = (
        User.objects.filter(
            role="participant",
            is_open_for_teaming=True,
            university=request.user.university,
            hackathon_participations__hackathon=hackathon,
        )
        .exclude(id=request.user.id)
        .exclude(team_memberships__team__hackathon=hackathon)
        .distinct()
    )

    candidates = list(candidates)
    random.shuffle(candidates)

    needed_members = hackathon.min_team_size - 1

    if len(candidates) < needed_members:
        messages.error(
            request,
            "Недостаточно свободных участников из вашего университета для случайной команды.",
        )
        return redirect("hackathon_detail", pk=pk)

    selected = candidates[: hackathon.max_team_size - 1]

    team = Team.objects.create(
        hackathon=hackathon,
        team_name=f"Random Team {request.user.username}",
        captain=request.user,
        is_open_for_random_join=True,
    )

    TeamMember.objects.create(team=team, user=request.user, role_in_team="captain")

    for user in selected:
        TeamMember.objects.create(team=team, user=user, role_in_team="member")

    messages.success(request, "Случайная команда создана.")
    return redirect("team_detail", team_id=team.id)


@role_required(["participant", "mentor", "organizer"])
def team_detail(request, team_id):
    team = get_object_or_404(Team, id=team_id)

    membership = TeamMember.objects.filter(team=team, user=request.user).exists()

    is_mentor = team.mentor == request.user

    if not membership and not is_mentor and request.user.role != "organizer":
        messages.error(request, "У вас нет доступа к этой команде.")
        return redirect("dashboard")

    members = TeamMember.objects.filter(team=team).select_related("user")

    return render(
        request,
        "team_detail.html",
        {
            "team": team,
            "members": members,
        },
    )


@role_required(["participant"])
def join_open_team(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    update_hackathon_status(team.hackathon)

    if team.hackathon.status not in ["team_building", "registration"]:
        messages.error(request, "Сейчас нельзя вступать в команды.")
        return redirect("hackathon_detail", pk=team.hackathon.id)

    if not team.is_open_for_random_join:
        messages.error(request, "Эта команда не открыта для вступления.")
        return redirect("hackathon_detail", pk=team.hackathon.id)

    is_registered = HackathonParticipant.objects.filter(
        hackathon=team.hackathon, user=request.user
    ).exists()

    if not is_registered:
        messages.error(request, "Сначала зарегистрируйтесь на хакатон.")
        return redirect("hackathon_detail", pk=team.hackathon.id)

    if request.user.university != team.captain.university:
        messages.error(
            request,
            "В эту команду могут вступать только участники из того же университета.",
        )
        return redirect("hackathon_detail", pk=team.hackathon.id)

    already_in_team = TeamMember.objects.filter(
        team__hackathon=team.hackathon, user=request.user
    ).exists()

    if already_in_team:
        messages.error(request, "Вы уже состоите в команде этого хакатона.")
        return redirect("hackathon_detail", pk=team.hackathon.id)

    current_count = TeamMember.objects.filter(team=team).count()

    if current_count >= team.hackathon.max_team_size:
        messages.error(request, "Команда уже заполнена.")
        return redirect("hackathon_detail", pk=team.hackathon.id)

    TeamMember.objects.create(team=team, user=request.user, role_in_team="member")

    messages.success(request, "Вы вступили в команду.")
    return redirect("team_detail", team_id=team.id)


@role_required(["participant", "mentor"])
def join_team_by_code_form(request, pk):
    hackathon = get_object_or_404(Hackathon, pk=pk)
    update_hackathon_status(hackathon)

    if request.method == "POST":
        invite_code = request.POST.get("invite_code")

        if request.user.role == "participant":
            team = Team.objects.filter(
                hackathon=hackathon, invite_code=invite_code
            ).first()

            if team is None:
                messages.error(request, "Команда с таким invite code не найдена.")
                return redirect("hackathon_detail", pk=pk)

            if request.user.university != team.captain.university:
                messages.error(
                    request, "Вы не можете вступить в команду другого университета."
                )
                return redirect("hackathon_detail", pk=pk)

            already_in_team = TeamMember.objects.filter(
                team__hackathon=hackathon, user=request.user
            ).exists()

            if already_in_team:
                messages.error(request, "Вы уже состоите в команде этого хакатона.")
                return redirect("hackathon_detail", pk=pk)

            current_count = TeamMember.objects.filter(team=team).count()

            if current_count >= hackathon.max_team_size:
                messages.error(request, "Команда уже заполнена.")
                return redirect("hackathon_detail", pk=pk)

            TeamMember.objects.create(
                team=team, user=request.user, role_in_team="member"
            )

            messages.success(request, "Вы вступили в команду.")
            return redirect("team_detail", team_id=team.id)

        if request.user.role == "mentor":
            team = Team.objects.filter(
                hackathon=hackathon, mentor_invite_code=invite_code
            ).first()

            if team is None:
                messages.error(
                    request, "Команда с таким mentor invite code не найдена."
                )
                return redirect("hackathon_detail", pk=pk)

            if (
                team.captain.university
                and request.user.university != team.captain.university
            ):
                messages.error(request, "Ментор должен быть из того же университета.")
                return redirect("hackathon_detail", pk=pk)

            team.mentor = request.user
            team.save()

            messages.success(request, "Вы добавлены как ментор команды.")
            return redirect("team_detail", team_id=team.id)

    return render(
        request,
        "join_team_by_code.html",
        {
            "hackathon": hackathon,
        },
    )


@role_required(["participant"])
def submit_project(request, pk):
    hackathon = get_object_or_404(Hackathon, pk=pk)
    update_hackathon_status(hackathon)

    if hackathon.status != "submission":
        messages.error(request, "Сейчас нельзя подавать или редактировать проект.")
        return redirect("hackathon_detail", pk=pk)

    membership = (
        TeamMember.objects.filter(team__hackathon=hackathon, user=request.user)
        .select_related("team")
        .first()
    )

    if not membership:
        messages.error(request, "Сначала нужно состоять в команде этого хакатона.")
        return redirect("hackathon_detail", pk=pk)

    project = Project.objects.filter(team=membership.team).first()

    if request.method == "POST":
        if project is None:
            project = Project(team=membership.team)

        project.title = request.POST.get("title")
        project.description = request.POST.get("description")
        project.technologies = request.POST.get("technologies")
        project.repository_url = request.POST.get("repository_url")

        if request.FILES.get("project_file"):
            project.project_file = request.FILES.get("project_file")

        if request.FILES.get("presentation_file"):
            project.presentation_file = request.FILES.get("presentation_file")

        if request.FILES.get("image_file"):
            project.image_file = request.FILES.get("image_file")

        if request.FILES.get("video_file"):
            project.video_file = request.FILES.get("video_file")

        project.save()

        messages.success(request, "Проект сохранён.")
        return redirect("hackathon_detail", pk=pk)

    return render(
        request,
        "submit_project.html",
        {
            "hackathon": hackathon,
            "project": project,
        },
    )


@role_required(["judge"])
def score_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    hackathon = project.team.hackathon

    update_hackathon_status(hackathon)

    if hackathon.status != "judging":
        messages.error(request, "Оценивание сейчас закрыто.")
        return redirect("judge_dashboard")

    judge_record = Judge.objects.filter(user=request.user, hackathon=hackathon).first()

    if not judge_record:
        messages.error(request, "Вы не назначены жюри этого хакатона.")
        return redirect("judge_dashboard")

    assignment, _ = JudgeAssignment.objects.get_or_create(
        judge=judge_record, project=project
    )

    criteria = Criterion.objects.filter(hackathon=hackathon)

    if not criteria.exists():
        messages.error(request, "Организатор ещё не создал критерии оценивания.")
        return redirect("judge_dashboard")

    existing_scores = {
        score.criterion_id: score
        for score in Score.objects.filter(assignment=assignment)
    }

    if request.method == "POST":
        for criterion in criteria:
            value = request.POST.get(f"score_{criterion.id}")
            comment = request.POST.get(f"comment_{criterion.id}")

            if value:
                if int(value) > criterion.max_score:
                    messages.error(
                        request, f"Балл по критерию '{criterion.name}' выше максимума."
                    )
                    return redirect("score_project", project_id=project.id)

                Score.objects.update_or_create(
                    assignment=assignment,
                    criterion=criterion,
                    defaults={
                        "score_value": value,
                        "comment": comment or "",
                    },
                )

        messages.success(request, "Оценки сохранены.")
        return redirect("judge_dashboard")

    return render(
        request,
        "score_project.html",
        {
            "assignment": assignment,
            "project": project,
            "criteria": criteria,
            "existing_scores": existing_scores,
        },
    )


@role_required(["organizer"])
def auto_assign_mentors(request, hackathon_id):

    hackathon = get_object_or_404(Hackathon, id=hackathon_id)

    teams = Team.objects.filter(hackathon=hackathon, mentor__isnull=True)

    mentors = User.objects.filter(role="mentor")

    if not mentors.exists():
        messages.error(request, "Нет доступных менторов.")

        return redirect("hackathon_detail", hackathon.id)

    mentor_cycle = cycle(mentors)

    assigned_count = 0

    for team in teams:
        mentor = next(mentor_cycle)

        team.mentor = mentor
        team.save()

        assigned_count += 1

    messages.success(request, f"Автоматически назначено менторов: {assigned_count}")

    return redirect("hackathon_teams", hackathon.id)
