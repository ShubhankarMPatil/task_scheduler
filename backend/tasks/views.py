from django.db.models import Exists, OuterRef, Sum
from django.db.models.functions import Coalesce
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import Task, TimeEntry
from .serializers import TaskSerializer, TimeEntrySerializer
from .services import start_task_timer, stop_task_timer


class TaskViewSet(ModelViewSet):
    serializer_class = TaskSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            qs = Task.objects.filter(user=user)
        else:
            qs = Task.objects.filter(user__isnull=True)

        return (
            qs.annotate(
                has_active_timer=Exists(
                    TimeEntry.objects.filter(task=OuterRef("pk"), end_time__isnull=True)
                ),
                total_time_seconds=Coalesce(Sum("time_entries__duration_seconds"), 0),
            ).order_by("-created_at")
        )

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(user=user if user.is_authenticated else None)

    @action(detail=True, methods=["post"], url_path="start-timer")
    def start_timer(self, request, pk=None):
        task = self.get_object()
        entry = start_task_timer(task)
        return Response(TimeEntrySerializer(entry).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="stop-timer")
    def stop_timer(self, request, pk=None):
        task = self.get_object()
        entry = stop_task_timer(task)
        if entry is None:
            return Response(
                {"detail": "No active timer for this task."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(TimeEntrySerializer(entry).data)

    @action(detail=True, methods=["get"], url_path="time-entries")
    def time_entries(self, request, pk=None):
        task = self.get_object()
        entries = TimeEntry.objects.filter(task=task).order_by("-start_time")
        return Response(TimeEntrySerializer(entries, many=True).data)
