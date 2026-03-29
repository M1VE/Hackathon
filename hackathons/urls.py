from rest_framework.routers import DefaultRouter
from .views import HackathonViewSet, HackathonStageViewSet, HackathonParticipantViewSet

router = DefaultRouter()
router.register(r"hackathons", HackathonViewSet, basename="hackathon")
router.register(r"stages", HackathonStageViewSet, basename="hackathon-stage")
router.register(r"participants", HackathonParticipantViewSet, basename="hackathon-participant")

urlpatterns = router.urls