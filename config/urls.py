from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse


def home(request):
    return HttpResponse("API работает")


urlpatterns = [
    path("", home),
    path("admin/", admin.site.urls),
    path("api/auth/", include("users.urls")),
    path("api/", include("hackathons.urls")),
    path("api/teams/", include("teams.urls")),
    path("api/projects/", include("projects.urls")),
    path("api/judging/", include("judging.urls")),
    path("api/announcements/", include("announcements.urls")),
]