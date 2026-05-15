from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from users.models import User
from hackathons.models import Hackathon, HackathonParticipant, HackathonStage
from teams.models import Team, TeamMember
from projects.models import Project
from judging.models import Criterion, Judge, JudgeAssignment, Score


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
    hackathons = Hackathon.objects.filter(is_active=True).order_by("-created_at")[:6]
    return render(request, "home.html", {"hackathons": hackathons})


def register_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        username = request.POST.get("username")
        full_name = request.POST.get("full_name")
        password = request.POST.get("password")
        role = request.POST.get("role")

        if role not in ["participant", "mentor"]:
            messages.error(request, "Через сайт можно зарегистрироваться только как участник или ментор.")
            return redirect("site_register")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Пользователь с таким email уже существует.")
            return redirect("site_register")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Такое имя пользователя уже занято.")
            return redirect("site_register")

        user = User.objects.create_user(
            email=email,
            username=username,
            full_name=full_name,
            password=password,
            role=role,
            is_open_for_teaming=request.POST.get("is_open_for_teaming") == "on",
        )

        login(request, user)
        return redirect("dashboard")

    return render(request, "register.html")


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

    return redirect("home")


@role_required(["participant"])
def participant_dashboard(request):
    participations = HackathonParticipant.objects.filter(
        user=request.user
    ).select_related("hackathon")

    teams = TeamMember.objects.filter(
        user=request.user
    ).select_related("team", "team__hackathon")

    return render(request, "participant_dashboard.html", {
        "participations": participations,
        "teams": teams,
    })


@role_required(["mentor"])
def mentor_dashboard(request):
    teams = Team.objects.filter(mentor=request.user).select_related("hackathon")
    return render(request, "mentor_dashboard.html", {"teams": teams})


@role_required(["organizer"])
def organizer_dashboard(request):
    hackathons = Hackathon.objects.filter(organizer=request.user).order_by("-created_at")
    return render(request, "organizer_dashboard.html", {"hackathons": hackathons})


@role_required(["judge"])
def judge_dashboard(request):
    judge_records = Judge.objects.filter(user=request.user).select_related("hackathon")

    assignments = JudgeAssignment.objects.filter(
        judge__in=judge_records
    ).select_related(
        "project",
        "project__team",
        "judge",
        "judge__hackathon"
    )

    return render(request, "judge_dashboard.html", {
        "judge_records": judge_records,
        "assignments": assignments,
    })


def hackathon_list(request):
    hackathons = Hackathon.objects.all().order_by("-created_at")
    return render(request, "hackathon_list.html", {"hackathons": hackathons})


def hackathon_detail(request, pk):
    hackathon = get_object_or_404(Hackathon, pk=pk)

    is_joined = False
    user_team = None
    project = None

    if request.user.is_authenticated:
        is_joined = HackathonParticipant.objects.filter(
            hackathon=hackathon,
            user=request.user
        ).exists()

        membership = TeamMember.objects.filter(
            team__hackathon=hackathon,
            user=request.user
        ).select_related("team").first()

        if membership:
            user_team = membership.team
            project = Project.objects.filter(team=user_team).first()

    return render(request, "hackathon_detail.html", {
        "hackathon": hackathon,
        "is_joined": is_joined,
        "user_team": user_team,
        "project": project,
    })


@login_required
def join_hackathon(request, pk):
    hackathon = get_object_or_404(Hackathon, pk=pk)

    if request.user.role not in ["participant", "mentor"]:
        messages.error(request, "На хакатон могут регистрироваться только участники и менторы.")
        return redirect("hackathon_detail", pk=pk)

    HackathonParticipant.objects.get_or_create(
        hackathon=hackathon,
        user=request.user
    )

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
            is_published=request.POST.get("is_published") == "on",
            is_active=True,
            min_team_size=request.POST.get("min_team_size") or 2,
            max_team_size=request.POST.get("max_team_size") or 5,
            allow_random_teaming=request.POST.get("allow_random_teaming") == "on",
            allow_mentor_assignment=request.POST.get("allow_mentor_assignment") == "on",
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
                    deadline=deadline
                )

        messages.success(request, "Хакатон создан.")
        return redirect("organizer_dashboard")

    return render(request, "create_hackathon.html")


@role_required(["organizer"])
def manage_hackathon(request, pk):
    hackathon = get_object_or_404(Hackathon, pk=pk, organizer=request.user)

    criteria = Criterion.objects.filter(hackathon=hackathon)
    teams = Team.objects.filter(hackathon=hackathon)
    projects = Project.objects.filter(team__hackathon=hackathon)
    judges = Judge.objects.filter(hackathon=hackathon).select_related("user")
    assignments = JudgeAssignment.objects.filter(
        judge__hackathon=hackathon
    ).select_related("judge", "judge__user", "project", "project__team")

    return render(request, "manage_hackathon.html", {
        "hackathon": hackathon,
        "criteria": criteria,
        "teams": teams,
        "projects": projects,
        "judges": judges,
        "assignments": assignments,
    })


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

    return render(request, "create_criterion.html", {"hackathon": hackathon})


@role_required(["organizer"])
def assign_judge(request, pk):
    hackathon = get_object_or_404(Hackathon, pk=pk, organizer=request.user)

    if request.method == "POST":
        judge_id = request.POST.get("judge_id")

        judge_user = User.objects.filter(
            id=judge_id,
            role="judge"
        ).first()

        if judge_user:
            Judge.objects.get_or_create(
                hackathon=hackathon,
                user=judge_user
            )
            messages.success(request, "Жюри назначено.")
            return redirect("manage_hackathon", pk=hackathon.id)

        messages.error(request, "Жюри не найдено.")
        return redirect("assign_judge", pk=hackathon.id)

    judges = User.objects.filter(role="judge")

    return render(request, "assign_judge.html", {
        "hackathon": hackathon,
        "judges": judges,
    })


@role_required(["organizer"])
def assign_project_to_judge(request, pk):
    hackathon = get_object_or_404(Hackathon, pk=pk, organizer=request.user)

    if request.method == "POST":
        judge_record_id = request.POST.get("judge_record_id")
        project_id = request.POST.get("project_id")

        judge_record = Judge.objects.filter(
            id=judge_record_id,
            hackathon=hackathon
        ).first()

        project = Project.objects.filter(
            id=project_id,
            team__hackathon=hackathon
        ).first()

        if judge_record and project:
            JudgeAssignment.objects.get_or_create(
                judge=judge_record,
                project=project
            )
            messages.success(request, "Проект назначен жюри.")
            return redirect("manage_hackathon", pk=hackathon.id)

        messages.error(request, "Не удалось назначить проект.")
        return redirect("assign_project", pk=hackathon.id)

    judges = Judge.objects.filter(hackathon=hackathon).select_related("user")
    projects = Project.objects.filter(team__hackathon=hackathon)

    return render(request, "assign_project.html", {
        "hackathon": hackathon,
        "judges": judges,
        "projects": projects,
    })


@role_required(["participant"])
def create_team(request, pk):
    hackathon = get_object_or_404(Hackathon, pk=pk)

    is_registered = HackathonParticipant.objects.filter(
        hackathon=hackathon,
        user=request.user
    ).exists()

    if not is_registered:
        messages.error(request, "Сначала зарегистрируйтесь на хакатон.")
        return redirect("hackathon_detail", pk=pk)

    already_in_team = TeamMember.objects.filter(
        team__hackathon=hackathon,
        user=request.user
    ).exists()

    if already_in_team:
        messages.error(request, "Вы уже состоите в команде этого хакатона.")
        return redirect("hackathon_detail", pk=pk)

    if request.method == "POST":
        team_name = request.POST.get("team_name")
        mentor_id = request.POST.get("mentor")

        mentor = None
        if mentor_id:
            mentor = User.objects.filter(id=mentor_id, role="mentor").first()

        team = Team.objects.create(
            hackathon=hackathon,
            team_name=team_name,
            captain=request.user,
            mentor=mentor,
            is_open_for_random_join=request.POST.get("is_open_for_random_join") == "on",
        )

        TeamMember.objects.create(
            team=team,
            user=request.user,
            role_in_team="captain"
        )

        messages.success(request, "Команда создана.")
        return redirect("team_detail", team_id=team.id)

    mentors = User.objects.filter(role="mentor")

    return render(request, "create_team.html", {
        "hackathon": hackathon,
        "mentors": mentors,
    })


@role_required(["participant", "mentor"])
def team_detail(request, team_id):
    team = get_object_or_404(Team, id=team_id)

    membership = TeamMember.objects.filter(
        team=team,
        user=request.user
    ).exists()

    is_mentor = team.mentor == request.user

    if not membership and not is_mentor:
        messages.error(request, "У вас нет доступа к этой команде.")
        return redirect("dashboard")

    members = TeamMember.objects.filter(team=team).select_related("user")

    available_participants = User.objects.filter(
        role="participant",
        is_open_for_teaming=True,
        hackathon_participations__hackathon=team.hackathon
    ).exclude(
        team_memberships__team__hackathon=team.hackathon
    ).distinct()

    return render(request, "team_detail.html", {
        "team": team,
        "members": members,
        "available_participants": available_participants,
    })


@role_required(["participant"])
def invite_member(request, team_id):
    team = get_object_or_404(Team, id=team_id)

    is_captain = TeamMember.objects.filter(
        team=team,
        user=request.user,
        role_in_team="captain"
    ).exists()

    if not is_captain:
        messages.error(request, "Только капитан может приглашать участников.")
        return redirect("team_detail", team_id=team.id)

    user_id = request.POST.get("user_id")

    user = User.objects.filter(
        id=user_id,
        role="participant"
    ).first()

    if user is None:
        messages.error(request, "Участник не найден.")
        return redirect("team_detail", team_id=team.id)

    already_in_team = TeamMember.objects.filter(
        team__hackathon=team.hackathon,
        user=user
    ).exists()

    if already_in_team:
        messages.error(request, "Этот участник уже состоит в другой команде.")
        return redirect("team_detail", team_id=team.id)

    current_members = TeamMember.objects.filter(team=team).count()

    if current_members >= team.hackathon.max_team_size:
        messages.error(request, "Команда уже заполнена.")
        return redirect("team_detail", team_id=team.id)

    TeamMember.objects.create(
        team=team,
        user=user,
        role_in_team="member"
    )

    messages.success(request, "Участник добавлен.")
    return redirect("team_detail", team_id=team.id)


@role_required(["participant"])
def join_team_by_code(request, team_id, invite_code):
    team = get_object_or_404(Team, id=team_id, invite_code=invite_code)

    already_in_team = TeamMember.objects.filter(
        team__hackathon=team.hackathon,
        user=request.user
    ).exists()

    if already_in_team:
        messages.error(request, "Вы уже состоите в команде.")
        return redirect("dashboard")

    current_members = TeamMember.objects.filter(team=team).count()

    if current_members >= team.hackathon.max_team_size:
        messages.error(request, "Команда уже заполнена.")
        return redirect("dashboard")

    TeamMember.objects.create(
        team=team,
        user=request.user,
        role_in_team="member"
    )

    messages.success(request, "Вы присоединились к команде.")
    return redirect("team_detail", team_id=team.id)


@role_required(["participant"])
def submit_project(request, pk):
    hackathon = get_object_or_404(Hackathon, pk=pk)

    membership = TeamMember.objects.filter(
        team__hackathon=hackathon,
        user=request.user
    ).select_related("team").first()

    if not membership:
        messages.error(request, "Сначала нужно состоять в команде этого хакатона.")
        return redirect("hackathon_detail", pk=pk)

    submission_stage = HackathonStage.objects.filter(
        hackathon=hackathon,
        stage_name="submission"
    ).first()

    if submission_stage and timezone.now() > submission_stage.deadline:
        messages.error(request, "Дедлайн подачи проектов уже прошёл.")
        return redirect("hackathon_detail", pk=pk)

    project = Project.objects.filter(team=membership.team).first()

    if request.method == "POST":
        if project is None:
            project = Project(team=membership.team)

        project.title = request.POST.get("title")
        project.description = request.POST.get("description")
        project.technologies = request.POST.get("technologies")
        project.repository_url = request.POST.get("repository_url")
        project.demo_url = request.POST.get("demo_url")
        project.video_url = request.POST.get("video_url")
        project.project_url = request.POST.get("project_url")
        project.save()

        messages.success(request, "Проект сохранён.")
        return redirect("hackathon_detail", pk=pk)

    return render(request, "submit_project.html", {
        "hackathon": hackathon,
        "project": project,
    })


@role_required(["judge"])
def score_project(request, assignment_id):
    assignment = get_object_or_404(
        JudgeAssignment,
        id=assignment_id,
        judge__user=request.user
    )

    criteria = Criterion.objects.filter(hackathon=assignment.judge.hackathon)

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
                    messages.error(request, f"Балл по критерию '{criterion.name}' выше максимума.")
                    return redirect("score_project", assignment_id=assignment.id)

                Score.objects.update_or_create(
                    assignment=assignment,
                    criterion=criterion,
                    defaults={
                        "score_value": value,
                        "comment": comment or "",
                    }
                )

        messages.success(request, "Оценки сохранены.")
        return redirect("judge_dashboard")

    return render(request, "score_project.html", {
        "assignment": assignment,
        "criteria": criteria,
        "existing_scores": existing_scores,
    })

@role_required(["organizer"])
def edit_hackathon(request, pk):

    hackathon = get_object_or_404(
        Hackathon,
        pk=pk,
        organizer=request.user
    )

    if request.method == "POST":

        hackathon.title = request.POST.get("title")

        hackathon.description = request.POST.get("description")

        hackathon.format = request.POST.get("format")

        hackathon.status = request.POST.get("status")

        hackathon.min_team_size = request.POST.get("min_team_size") or 2

        hackathon.max_team_size = request.POST.get("max_team_size") or 5

        hackathon.allow_random_teaming = (
            request.POST.get("allow_random_teaming") == "on"
        )

        hackathon.allow_mentor_assignment = (
            request.POST.get("allow_mentor_assignment") == "on"
        )

        hackathon.save()

        messages.success(request, "Хакатон обновлён.")

        return redirect(
            "manage_hackathon",
            pk=hackathon.id
        )

    return render(
        request,
        "edit_hackathon.html",
        {"hackathon": hackathon}
    )