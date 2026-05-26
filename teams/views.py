import random
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Team, TeamMember
from users.models import User
from hackathons.models import HackathonParticipant

def team_detail_view(request, pk):
    """Отображение HTML-страницы конкретной команды"""
    team = get_object_or_404(Team, pk=pk)
    members = team.members.all()
    return render(request, 'team_detail.html', {'team': team, 'members': members})

def auto_fill(request, pk):
    """Функция автоматического добора участников в команду"""
    if request.method != "POST":
        return JsonResponse({"detail": "Метод не разрешен"}, status=405)
        
    team = get_object_or_404(Team, pk=pk)
    hackathon = team.hackathon

    if not hackathon.allow_random_teaming:
        return JsonResponse({"detail": "Случайный добор участников отключен."}, status=400)

    if not team.is_open_for_random_join:
        return JsonResponse({"detail": "Эта команда не открыта для случайного добора."}, status=400)

    current_count = TeamMember.objects.filter(team=team).count()
    free_slots = hackathon.max_team_size - current_count

    if free_slots <= 0:
        return JsonResponse({"detail": "В команде нет свободных мест."}, status=400)

    # Находим ID всех зарегистрированных на хакатон пользователей
    registered_user_ids = HackathonParticipant.objects.filter(
        hackathon=hackathon
    ).values_list('user_id', flat=True)

    # Ищем участников без команд
    candidates = User.objects.filter(
        id__in=registered_user_ids,
        role="participant",
        is_open_for_teaming=True
    ).exclude(
        team_memberships__team__hackathon=hackathon
    ).distinct()

    candidates = list(candidates)
    random.shuffle(candidates)
    selected = candidates[:free_slots]

    created_members = []
    for user in selected:
        member = TeamMember.objects.create(
            team=team,
            user=user,
            role_in_team="member"
        )
        created_members.append(member.user.email)

    return JsonResponse({"detail": "Автодобор выполнен.", "added_users": created_members})