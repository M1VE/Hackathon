from django.shortcuts import render, get_object_or_404
from django.views import View
from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import generics, permissions
from .serializers import RegisterSerializer
from hackathons.models import Hackathon

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class UserProfileView(View):
    def get(self, request, username):
        profile_user = get_object_or_404(User, username__iexact=username)

        user_participating_filter = (
            Q(participants__user=profile_user) | Q(teams__members__user=profile_user)
        )

        try:
            total_hackathons = (
                Hackathon.objects.filter(user_participating_filter).distinct().count()
            )
            active_hackathons = (
                Hackathon.objects.filter(user_participating_filter)
                .exclude(status__in=["draft", "finished", "archived"])
                .distinct()
            )
        except Exception:
            fallback_filter = Q(teams__members__user=profile_user)
            total_hackathons = (
                Hackathon.objects.filter(fallback_filter).distinct().count()
            )
            active_hackathons = (
                Hackathon.objects.filter(fallback_filter)
                .exclude(status__in=["draft", "finished", "archived"])
                .distinct()
            )

        created_hackathons_count = Hackathon.objects.filter(
            organizer=profile_user
        ).count()

        context = {
            "profile_user": profile_user,
            "total_hackathons": total_hackathons,
            "active_hackathons": active_hackathons,
            "wins_count": profile_user.wins,
            "created_hackathons_count": created_hackathons_count,
        }

        return render(request, "profile.html", context)