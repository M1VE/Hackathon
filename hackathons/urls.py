from django.urls import path
from .views import HackathonCreateView, HackathonListView  # Импортируем твои HTML вьюхи

urlpatterns = [
    # Главная страница со списком хакатонов
    path("", HackathonListView.as_view(), name="hackathon_list"),
    # Страница создания
    path("create/", HackathonCreateView.as_view(), name="create_hackathon"),
]