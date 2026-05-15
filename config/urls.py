from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("", include("frontend.urls")),

    path("admin/", admin.site.urls),

    path("api/auth/", include("users.urls")),
    path("api/", include("hackathons.urls")),
    path("api/teams/", include("teams.urls")),
    path("api/projects/", include("projects.urls")),
    path("api/judging/", include("judging.urls")),
    path("api/announcements/", include("announcements.urls")),
]