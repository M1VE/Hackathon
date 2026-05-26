from django.urls import path
from .views import team_detail_view, auto_fill

urlpatterns = [
    # Маршрут для страницы команды (/teams/ID/)
    path('<int:pk>/', team_detail_view, name='team_detail'),
    
    # Маршрут для кнопки автодобора
    path('<int:pk>/auto-fill/', auto_fill, name='team_auto_fill'),
    
    # Заглушка для инвайт-кодов, чтобы шаблон не падал по NoReverseMatch
    path('join-by-code/', team_detail_view, name='join_team_by_code_form'),
]