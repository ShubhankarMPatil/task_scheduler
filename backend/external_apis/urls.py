from django.urls import path

from .views import world_time

urlpatterns = [
    path("world-time/", world_time),
]
