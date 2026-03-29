from rest_framework import serializers
from .models import Criterion, Judge, JudgeAssignment, Score


class CriterionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Criterion
        fields = "__all__"


class JudgeSerializer(serializers.ModelSerializer):
    user_email = serializers.ReadOnlyField(source="user.email")
    hackathon_title = serializers.ReadOnlyField(source="hackathon.title")

    class Meta:
        model = Judge
        fields = ["id", "hackathon", "hackathon_title", "user", "user_email"]


class JudgeAssignmentSerializer(serializers.ModelSerializer):
    judge_email = serializers.ReadOnlyField(source="judge.user.email")
    project_title = serializers.ReadOnlyField(source="project.title")

    class Meta:
        model = JudgeAssignment
        fields = ["id", "judge", "judge_email", "project", "project_title"]


class ScoreSerializer(serializers.ModelSerializer):
    criterion_name = serializers.ReadOnlyField(source="criterion.name")
    project_title = serializers.ReadOnlyField(source="assignment.project.title")
    judge_email = serializers.ReadOnlyField(source="assignment.judge.user.email")

    class Meta:
        model = Score
        fields = [
            "id",
            "assignment",
            "project_title",
            "judge_email",
            "criterion",
            "criterion_name",
            "score_value",
            "comment",
            "created_at",
        ]
        read_only_fields = ["created_at"]

    def validate(self, attrs):
        assignment = attrs.get("assignment")
        criterion = attrs.get("criterion")

        if assignment and criterion:
            if assignment.judge.hackathon_id != criterion.hackathon_id:
                raise serializers.ValidationError(
                    "Criterion и assignment должны относиться к одному hackathon."
                )

        return attrs