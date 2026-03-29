from rest_framework import viewsets, permissions
from .models import Criterion, Judge, JudgeAssignment, Score
from .serializers import (
    CriterionSerializer,
    JudgeSerializer,
    JudgeAssignmentSerializer,
    ScoreSerializer,
)


class CriterionViewSet(viewsets.ModelViewSet):
    queryset = Criterion.objects.all().order_by("id")
    serializer_class = CriterionSerializer
    permission_classes = [permissions.AllowAny]


class JudgeViewSet(viewsets.ModelViewSet):
    queryset = Judge.objects.all().order_by("id")
    serializer_class = JudgeSerializer
    permission_classes = [permissions.AllowAny]


class JudgeAssignmentViewSet(viewsets.ModelViewSet):
    queryset = JudgeAssignment.objects.all().order_by("id")
    serializer_class = JudgeAssignmentSerializer
    permission_classes = [permissions.AllowAny]


class ScoreViewSet(viewsets.ModelViewSet):
    queryset = Score.objects.all().order_by("-created_at")
    serializer_class = ScoreSerializer
    permission_classes = [permissions.AllowAny]