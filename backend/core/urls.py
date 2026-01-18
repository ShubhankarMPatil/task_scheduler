from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path


def api_index(_request):
    return JsonResponse(
        {
            "name": "Task Time Tracker API",
            "endpoints": {
                "tasks": "/api/tasks/",
                "tasks_populate": "/api/tasks/populate/?date=YYYY-MM-DD",
                "templates": "/api/templates/",
                "time_entries": "/api/time-entries/?task=<task_id>",
                "dashboard": "/api/dashboard/?date=YYYY-MM-DD",
                "world_time": "/api/world-time/",
            },
        }
    )


urlpatterns = [
    path("", api_index),
    path("admin/", admin.site.urls),

    path("api/tasks/", include("tasks.urls")),
    path("api/dashboard/", include("dashboards.urls")),

    # Shared /api/... endpoints
    path("api/", include("tasks.api_urls")),
    path("api/", include("external_apis.urls")),
]
