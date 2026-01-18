from rest_framework.routers import DefaultRouter

from .views import TaskViewSet

router = DefaultRouter()
# Mount the viewset at /api/tasks/ so GET /api/tasks/ returns a list of tasks.
router.register("", TaskViewSet, basename="tasks")

urlpatterns = router.urls
