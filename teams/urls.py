from rest_framework.routers import DefaultRouter
from .views import TeamViewSet, TeamMemberViewSet

router = DefaultRouter()
router.register(r"", TeamViewSet, basename="team")
router.register(r"members", TeamMemberViewSet, basename="team-member")

urlpatterns = router.urls