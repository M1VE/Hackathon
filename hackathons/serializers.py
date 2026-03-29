from rest_framework import serializers
from .models import Hackathon, HackathonStage, HackathonParticipant
from users.models import User


class HackathonSerializer(serializers.ModelSerializer):
    organizer = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role__in=["organizer", "admin"])
    )
    organizer_email = serializers.ReadOnlyField(source="organizer.email")

    class Meta:
        model = Hackathon
        fields = [
            "id",
            "title",
            "description",
            "organizer",
            "organizer_email",
            "format",
            "status",
            "is_published",
            "is_active",
            "min_team_size",
            "max_team_size",
            "allow_random_teaming",
            "allow_mentor_assignment",
            "max_mentors_per_team",
            "created_at",
        ]
        read_only_fields = ["created_at"]


class HackathonStageSerializer(serializers.ModelSerializer):
    class Meta:
        model = HackathonStage
        fields = ["id", "hackathon", "stage_name", "deadline"]


class HackathonParticipantSerializer(serializers.ModelSerializer):
    user_email = serializers.ReadOnlyField(source="user.email")

    class Meta:
        model = HackathonParticipant
        fields = ["id", "hackathon", "user", "user_email", "registration_date"]
        read_only_fields = ["registration_date"]