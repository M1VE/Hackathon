from django.shortcuts import render, get_object_or_404
from django.views import View
from django.contrib.auth import get_user_model
from rest_framework import generics, permissions
from .serializers import RegisterSerializer
from hackathons.models import Hackathon

User = get_user_model()

# 1. Возвращаем класс регистрации, который случайно стерся
class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


# 2. Твой рабочий класс профиля пользователя
class UserProfileView(View):
    def get(self, request, username):
        # Находим пользователя по username без учета регистра
        profile_user = get_object_or_404(User, username__iexact=username)
        
        # Фильтруем хакатоны через поле связи во внутренней модели TeamMember
        total_hackathons = Hackathon.objects.filter(teams__members__user=profile_user).distinct().count()
        
        active_hackathons = Hackathon.objects.filter(
            teams__members__user=profile_user
        ).exclude(status__in=['draft', 'finished', 'archived']).distinct()
        
        context = {
            "profile_user": profile_user,
            "total_hackathons": total_hackathons,
            "active_hackathons": active_hackathons,
            "wins_count": 0,
        }
        return render(request, "profile.html", context)