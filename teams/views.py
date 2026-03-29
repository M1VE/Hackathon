import random
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Team, TeamMember
from .serializers import TeamSerializer, TeamMemberSerializer
from users.models import User
from hackathons.models import HackathonParticipant


class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all().order_by("-created_at")
    serializer_class = TeamSerializer
    permission_classes = [permissions.AllowAny]

    @action(detail=True, methods=["post"])
    def auto_fill(self, request, pk=None):
        team = self.get_object()
        hackathon = team.hackathon

        if not hackathon.allow_random_teaming:
            return Response(
                {"detail": "Случайный добор участников отключен для этого хакатона."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not team.is_open_for_random_join:
            return Response(
                {"detail": "Эта команда не открыта для случайного добора."},
                status=status.HTTP_400_BAD_REQUEST
            )

        current_count = TeamMember.objects.filter(team=team).count()
        free_slots = hackathon.max_team_size - current_count

        if free_slots <= 0:
            return Response(
                {"detail": "В команде нет свободных мест."},
                status=status.HTTP_400_BAD_REQUEST
            )

        candidates = User.objects.filter(
            role="participant",
            is_open_for_teaming=True,
            hackathon_participations__hackathon=hackathon
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

        return Response({
            "detail": "Автодобор выполнен.",
            "added_users": created_members
        })


class TeamMemberViewSet(viewsets.ModelViewSet):
    queryset = TeamMember.objects.all()
    serializer_class = TeamMemberSerializer
    permission_classes = [permissions.AllowAny]