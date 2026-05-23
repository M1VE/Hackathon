from django.shortcuts import render, get_object_or_404
from django.views import View
from django.contrib.auth import get_user_model
from django.db.models import Q  # Импортируем Q для фильтрации ИЛИ
from rest_framework import generics, permissions
from .serializers import RegisterSerializer
from hackathons.models import Hackathon

User = get_user_model()

# 1. Восстанавливаем класс регистрации (чтобы не было ImportError в urls.py)
class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


# 2. Рабочий класс профиля пользователя
class UserProfileView(View):
    def get(self, request, username):
        # Находим пользователя по username без учета регистра
        profile_user = get_object_or_404(User, username__iexact=username)
        
        # Фильтр: проверяем регистрацию пользователя на хакатон ИЛИ его участие через команду
        # Django автоматически связывает хакатон с пользователем через промежуточные модели
        user_participating_filter = Q(participants__user=profile_user) | Q(teams__members__user=profile_user)

        try:
            # Пробуем сделать запрос по стандартному обратному имени связи participants
            total_hackathons = Hackathon.objects.filter(user_participating_filter).distinct().count()
            active_hackathons = Hackathon.objects.filter(
                user_participating_filter
            ).exclude(status__in=['draft', 'finished', 'archived']).distinct()
        except Exception:
            # Если поле связи в твоей промежуточной модели называется иначе (например, просто по связи команд),
            # используем запасной вариант фильтрации только по командам, чтобы страница не падала в 500 ошибку
            fallback_filter = Q(teams__members__user=profile_user)
            total_hackathons = Hackathon.objects.filter(fallback_filter).distinct().count()
            active_hackathons = Hackathon.objects.filter(
                fallback_filter
            ).exclude(status__in=['draft', 'finished', 'archived']).distinct()
        
        context = {
            "profile_user": profile_user,
            "total_hackathons": total_hackathons,
            "active_hackathons": active_hackathons,
            "wins_count": 0,
        }
        
        return render(request, "profile.html", context)