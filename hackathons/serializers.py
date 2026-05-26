from rest_framework import serializers
from .models import Hackathon, HackathonStage, HackathonParticipant, HackathonAttachment
from users.models import User
from django.utils import timezone


class HackathonStageSerializer(serializers.ModelSerializer):
    class Meta:
        model = HackathonStage
        fields = [
            "id",
            "hackathon",
            "stage_name",
            "deadline",
        ]


class HackathonAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = HackathonAttachment
        fields = ["id", "title", "file", "uploaded_at"]


class HackathonSerializer(serializers.ModelSerializer):
    organizer = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role__in=["organizer", "admin"])
    )
    organizer_email = serializers.ReadOnlyField(source="organizer.email")
    status = serializers.CharField(required=False)
    
    # Новые поля для фронтенда (главной страницы)
    stages = HackathonStageSerializer(many=True, read_only=True)
    attachments = HackathonAttachmentSerializer(many=True, read_only=True)
    next_deadline = serializers.SerializerMethodField()

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
            "is_active",
            "min_team_size",
            "max_team_size",
            "allow_random_teaming",
            "allow_mentor_assignment",
            "max_mentors_per_team",
            "created_at",
            "stages",
            "attachments",
            "next_deadline",
        ]
        read_only_fields = ["created_at"]

    def get_next_deadline(self, instance):
        """Возвращает ближайший дедлайн и название этапа для таймера обратного отсчета."""
        now = timezone.now()
        upcoming_stage = instance.stages.filter(deadline__gt=now).order_by("deadline").first()
        if upcoming_stage:
            return {
                "stage_name": upcoming_stage.stage_name,
                "deadline": upcoming_stage.deadline,
            }
        return None

    def to_representation(self, instance):
        """Автоматически обновляет статус при чтении данных хакатона."""
        instance.update_status()
        return super().to_representation(instance)

    def create(self, validated_data):
        """Сохраняет хакатон, файлы правил и дедлайны из запроса."""
        request = self.context.get('request')
        rules_file = request.FILES.get('rules_file') if request else None
        
        hackathon = Hackathon.objects.create(**validated_data)

        if rules_file:
            HackathonAttachment.objects.create(
                hackathon=hackathon,
                title="Правила хакатона",
                file=rules_file
            )

        if request:
            deadlines = {
                "registration": request.data.get("registration_deadline"),
                "team_building": request.data.get("team_building_deadline"),
                "submission": request.data.get("submission_deadline"),
                "judging": request.data.get("judging_deadline"),
                "results": request.data.get("results_deadline"),
            }

            for stage_name, deadline_val in deadlines.items():
                if deadline_val:
                    HackathonStage.objects.create(
                        hackathon=hackathon,
                        stage_name=stage_name,
                        deadline=deadline_val
                    )
            
            hackathon.update_status()

        return hackathon


class HackathonParticipantSerializer(serializers.ModelSerializer):
    user_email = serializers.ReadOnlyField(source="user.email")

    class Meta:
        model = HackathonParticipant
        fields = [
            "id",
            "hackathon",
            "user",
            "user_email",
            "registration_date",
        ]
        read_only_fields = ["registration_date"]