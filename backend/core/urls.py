from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path


def api_index(_request):
    return JsonResponse(
        {
            "name": "Task Time Tracker API",
            "endpoints": {
                "tasks": "/api/tasks/",
                "dashboard": "/api/dashboard/",
                "world_time": "/api/world-time/",
            },
        }
    )


urlpatterns = [
    path("", api_index),
    path("admin/", admin.site.urls),
    path("api/tasks/", include("tasks.urls")),
    path("api/dashboard/", include("dashboards.urls")),
    path("api/", include("external_apis.urls")),
]
