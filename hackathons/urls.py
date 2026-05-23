from django.urls import path
from .views import HackathonListView, HackathonCreateView, HackathonDetailView

urlpatterns = [
    # Список хакатонов (/hackathons/)
    path('', HackathonListView.as_view(), name='hackathon_list'),

    # Создание хакатона (/hackathons/create/)
    path('create/', HackathonCreateView.as_view(), name='create_hackathon'),

    # Детальная страница конкретного хакатона (/hackathons/ID/)
    path('<int:pk>/', HackathonDetailView.as_view(), name='hackathon_detail'),
]