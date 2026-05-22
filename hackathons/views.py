from django.shortcuts import render, redirect
from django.utils import timezone
from django.views import View
from .models import Hackathon, HackathonStage, HackathonAttachment

def get_status_by_deadlines(hackathon):
    """Вычисляет текущий статус хакатона на основе дедлайнов."""
    now = timezone.now()
    # Получаем все этапы хакатона, отсортированные по времени дедлайна
    stages = hackathon.stages.order_by('deadline')
    
    if not stages.exists():
        return hackathon.status

    if hackathon.status == "draft":
        return "draft"

    # Ищем первый этап, дедлайн которого еще не наступил
    current_stage = stages.filter(deadline__gt=now).first()
    
    if current_stage:
        # Возвращаем имя текущего активного этапа
        if current_stage.stage_name == "registration":
            return "registration"
        elif current_stage.stage_name == "team_building":
            return "team_building"
        elif current_stage.stage_name == "submission":
            return "submission"
        elif current_stage.stage_name == "judging":
            return "judging"
    else:
        # Если все дедлайны прошли — хакатон завершен
        return "finished"
        
    return hackathon.status


class HackathonListView(View):
    def get(self, request):
        hackathons = Hackathon.objects.all()
        
        # АВТОСМЕНА ЭТАПОВ: Проверяем каждый хакатон перед показом на странице
        for hackathon in hackathons:
            new_status = get_status_by_deadlines(hackathon)
            if hackathon.status != new_status:
                hackathon.status = new_status
                hackathon.save() # Сохраняем новый статус в базу данных
                
        return render(request, "hackathon_list.html", {"hackathons": hackathons})


class HackathonCreateView(View):
    def get(self, request):
        return render(request, "create_hackathon.html")

    def post(self, request):
        hackathon = Hackathon.objects.create(
            title=request.POST.get("title"),
            description=request.POST.get("description"),
            format=request.POST.get("format", "intra"),
            status=request.POST.get("status", "draft"),
            min_team_size=int(request.POST.get("min_team_size", 2)),
            max_team_size=int(request.POST.get("max_team_size", 5)),
            allow_random_teaming=request.POST.get("allow_random_teaming") == "on",
            allow_mentor_assignment=request.POST.get("allow_mentor_assignment") == "on",
            cover_image=request.FILES.get("cover_image"),
            organizer=request.user if request.user.is_authenticated else None
        )

        if request.FILES.get("rules_file"):
            HackathonAttachment.objects.create(
                hackathon=hackathon,
                title="Правила хакатона",
                file=request.FILES.get("rules_file")
            )

        deadlines = {
            "registration": request.POST.get("registration_deadline"),
            "team_building": request.POST.get("team_building_deadline"),
            "submission": request.POST.get("submission_deadline"),
            "judging": request.POST.get("judging_deadline"),
            "results": request.POST.get("results_deadline"),
        }

        for stage_name, deadline_val in deadlines.items():
            if deadline_val:
                HackathonStage.objects.create(
                    hackathon=hackathon,
                    stage_name=stage_name,
                    deadline=deadline_val
                )

        hackathon.status = get_status_by_deadlines(hackathon)
        hackathon.save()

        return redirect("hackathon_list")