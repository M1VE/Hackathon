from rest_framework.routers import DefaultRouter
from .views import CriterionViewSet, JudgeViewSet, JudgeAssignmentViewSet, ScoreViewSet

router = DefaultRouter()
router.register(r"criteria", CriterionViewSet, basename="criterion")
router.register(r"judges", JudgeViewSet, basename="judge")
router.register(r"assignments", JudgeAssignmentViewSet, basename="judge-assignment")
router.register(r"scores", ScoreViewSet, basename="score")

urlpatterns = router.urls