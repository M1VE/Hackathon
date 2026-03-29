from rest_framework import serializers
from .models import Team, TeamMember
from users.models import User
from hackathons.models import HackathonParticipant


class TeamSerializer(serializers.ModelSerializer):
    captain = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role="participant")
    )
    mentor = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role="mentor"),
        allow_null=True,
        required=False
    )
    captain_email = serializers.ReadOnlyField(source="captain.email")
    mentor_email = serializers.ReadOnlyField(source="mentor.email")

    class Meta:
        model = Team
        fields = [
            "id",
            "hackathon",
            "team_name",
            "captain",
            "captain_email",
            "mentor",
            "mentor_email",
            "invite_code",
            "is_open_for_random_join",
            "created_at",
        ]
        read_only_fields = ["invite_code", "created_at"]

    def validate(self, attrs):
        hackathon = attrs.get("hackathon")
        captain = attrs.get("captain")
        mentor = attrs.get("mentor")

        if hackathon and captain:
            is_registered = HackathonParticipant.objects.filter(
                hackathon=hackathon,
                user=captain
            ).exists()
            if not is_registered:
                raise serializers.ValidationError("Капитан должен быть зарегистрирован на этот хакатон.")

            already_in_other_team = TeamMember.objects.filter(
                team__hackathon=hackathon,
                user=captain
            ).exists()
            if already_in_other_team:
                raise serializers.ValidationError("Капитан уже состоит в другой команде этого хакатона.")

        if mentor:
            if mentor.role != "mentor":
                raise serializers.ValidationError("Можно назначить только mentor.")

            if hackathon and not hackathon.allow_mentor_assignment:
                raise serializers.ValidationError("На этом хакатоне назначение ментора отключено.")

        return attrs

    def create(self, validated_data):
        team = Team.objects.create(**validated_data)
        TeamMember.objects.create(
            team=team,
            user=team.captain,
            role_in_team="captain"
        )
        return team


class TeamMemberSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role="participant")
    )
    user_email = serializers.ReadOnlyField(source="user.email")

    class Meta:
        model = TeamMember
        fields = ["id", "team", "user", "user_email", "role_in_team"]

    def validate(self, attrs):
        team = attrs.get("team")
        user = attrs.get("user")

        if not team or not user:
            return attrs

        is_registered = HackathonParticipant.objects.filter(
            hackathon=team.hackathon,
            user=user
        ).exists()
        if not is_registered:
            raise serializers.ValidationError("Пользователь должен быть зарегистрирован на этот хакатон.")

        already_in_other_team = TeamMember.objects.filter(
            team__hackathon=team.hackathon,
            user=user
        ).exclude(team=team).exists()
        if already_in_other_team:
            raise serializers.ValidationError("Пользователь уже состоит в другой команде этого хакатона.")

        current_members_count = TeamMember.objects.filter(team=team).count()
        if current_members_count >= team.hackathon.max_team_size:
            raise serializers.ValidationError("Команда уже достигла максимального размера.")

        return attrs