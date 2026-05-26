from django import template
from django.utils import timezone

register = template.Library()

@register.filter
def get_deadline(hackathon, stage_name):
    """Возвращает временную метку дедлайна в секундах."""
    stage = hackathon.stages.filter(stage_name=stage_name).first()
    if stage:
        return int(stage.deadline.timestamp())
    return ""

@register.filter
def get_current_deadline(hackathon):
    """Находит ближайший будущий дедлайн для таймера (в секундах)."""
    now = timezone.now()
    next_stage = hackathon.stages.filter(deadline__gt=now).order_by('deadline').first()
    if next_stage:
        return int(next_stage.deadline.timestamp())
    return ""

@register.filter
def get_current_stage_title(hackathon):
    """Возвращает читаемое название текущего/следующего этапа."""
    now = timezone.now()
    next_stage = hackathon.stages.filter(deadline__gt=now).order_by('deadline').first()
    
    titles = {
        "registration": "Регистрация",
        "team_building": "Формирование команд",
        "submission": "Подача проектов",
        "judging": "Оценивание жюри",
        "results": "Публикация результатов"
    }
    
    if next_stage:
        return titles.get(next_stage.stage_name, next_stage.stage_name)
    return "Завершен"