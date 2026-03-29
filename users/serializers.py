from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import University

User = get_user_model()


class UniversitySerializer(serializers.ModelSerializer):
    class Meta:
        model = University
        fields = ["id", "name"]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(
        choices=[
            ("participant", "Participant"),
            ("mentor", "Mentor"),
        ]
    )

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "full_name",
            "password",
            "role",
            "university",
            "is_open_for_teaming",
        ]

    def create(self, validated_data):
        return User.objects.create_user(
            email=validated_data["email"],
            username=validated_data["username"],
            full_name=validated_data["full_name"],
            password=validated_data["password"],
            role=validated_data["role"],
            university=validated_data.get("university"),
            is_open_for_teaming=validated_data.get("is_open_for_teaming", False),
        )