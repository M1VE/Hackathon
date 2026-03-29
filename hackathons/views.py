from rest_framework import viewsets, permissions
from .models import Hackathon, HackathonStage, HackathonParticipant
from .serializers import (
    HackathonSerializer,
    HackathonStageSerializer,
    HackathonParticipantSerializer,
)


class HackathonViewSet(viewsets.ModelViewSet):
    queryset = Hackathon.objects.all().order_by("-created_at")
    serializer_class = HackathonSerializer
    permission_classes = [permissions.AllowAny]


class HackathonStageViewSet(viewsets.ModelViewSet):
    queryset = HackathonStage.objects.all().order_by("deadline")
    serializer_class = HackathonStageSerializer
    permission_classes = [permissions.AllowAny]


class HackathonParticipantViewSet(viewsets.ModelViewSet):
    queryset = HackathonParticipant.objects.all().order_by("-registration_date")
    serializer_class = HackathonParticipantSerializer
    permission_classes = [permissions.AllowAny]