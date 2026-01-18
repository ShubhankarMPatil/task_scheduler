from rest_framework.routers import DefaultRouter

from .views import HabitTemplateViewSet, TimeEntryViewSet

router = DefaultRouter()
router.register("templates", HabitTemplateViewSet, basename="templates")
router.register("time-entries", TimeEntryViewSet, basename="time_entries")

urlpatterns = router.urls
