from __future__ import annotations

from datetime import date

from django.db.models import Exists, OuterRef, Subquery, Sum
from django.db.models.functions import Coalesce
from django.utils import timezone
from requests import RequestException
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from external_apis.world_time import fetch_current_time

from .models import HabitTemplate, Task, TimeEntry
from .serializers import HabitTemplateSerializer, TaskSerializer, TimeEntrySerializer
from .services import start_task_timer, stop_task_timer


def _bucket_user(request):
    user = request.user
    return user if user.is_authenticated else None


def _parse_date_param(value: str | None) -> date:
    if not value:
        return timezone.localdate()
    try:
        return date.fromisoformat(value)
    except ValueError:
        return timezone.localdate()


class HabitTemplateViewSet(ModelViewSet):
    serializer_class = HabitTemplateSerializer

    def get_queryset(self):
        user = _bucket_user(self.request)
        qs = HabitTemplate.objects.all()
        if user is None:
            return qs.filter(user__isnull=True)
        return qs.filter(user=user)

    def perform_create(self, serializer):
        user = _bucket_user(self.request)
        serializer.save(user=user)


class TaskViewSet(ModelViewSet):
    serializer_class = TaskSerializer

    def _scoped_queryset(self):
        user = _bucket_user(self.request)
        qs = Task.objects.all()
        if user is None:
            return qs.filter(user__isnull=True)
        return qs.filter(user=user)

    @action(detail=False, methods=["get"], url_path="stats")
    def stats(self, request):
        """Simple report endpoint used by the frontend chart.

        Returns counts of completed vs pending tasks, optionally scoped to a date.
        """

        qs = self._scoped_queryset()

        date_param = request.query_params.get("date")
        selected_date = None
        if date_param is not None:
            selected_date = _parse_date_param(date_param)
            qs = qs.filter(date=selected_date)

        completed = qs.filter(completed=True).count()
        pending = qs.filter(completed=False).count()

        return Response(
            {
                "date": str(selected_date) if selected_date else None,
                "total": completed + pending,
                "completed": completed,
                "pending": pending,
            }
        )

    @action(detail=False, methods=["get"], url_path="world-time")
    def world_time(self, _request):
        """Proxy World Time API through the backend.

        This endpoint exists to satisfy the assignment requirement:
        GET /api/tasks/world-time/
        """

        try:
            data = fetch_current_time()
        except RequestException as exc:
            return Response(
                {"detail": "Failed to fetch world time.", "error": str(exc)},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        return Response(
            {
                "timezone": data.get("timezone"),
                "datetime": data.get("datetime"),
                "utc_offset": data.get("utc_offset"),
            }
        )

    def get_queryset(self):
        qs = self._scoped_queryset()

        # Only list is date-scoped; detail actions address an explicit task id.
        if self.action == "list":
            selected_date = _parse_date_param(self.request.query_params.get("date"))
            qs = qs.filter(date=selected_date)

        active_entry_qs = (
            TimeEntry.objects.filter(task=OuterRef("pk"), end_time__isnull=True)
            .order_by("-start_time")
        )

        return qs.annotate(
            has_active_timer=Exists(active_entry_qs),
            active_entry_start_time=Subquery(active_entry_qs.values("start_time")[:1]),
            total_time_seconds=Coalesce(Sum("time_entries__duration_seconds"), 0),
        ).order_by("-created_at")

    def perform_create(self, serializer):
        user = _bucket_user(self.request)
        serializer.save(user=user)

    @action(detail=False, methods=["post"], url_path="populate")
    def populate(self, request):
        """Create missing daily tasks from active templates for the given date."""

        user = _bucket_user(request)
        selected_date = _parse_date_param(request.query_params.get("date"))

        template_qs = HabitTemplate.objects.filter(is_active=True)
        if user is None:
            template_qs = template_qs.filter(user__isnull=True)
            task_qs = Task.objects.filter(user__isnull=True)
        else:
            template_qs = template_qs.filter(user=user)
            task_qs = Task.objects.filter(user=user)

        template_ids = list(template_qs.values_list("id", flat=True))
        existing = set(
            task_qs.filter(date=selected_date, habit_template_id__in=template_ids).values_list(
                "habit_template_id", flat=True
            )
        )

        created = 0
        for tmpl in template_qs:
            if tmpl.id in existing:
                continue
            Task.objects.create(
                user=user,
                habit_template=tmpl,
                title=tmpl.title,
                description=tmpl.description,
                date=selected_date,
                target_seconds=tmpl.default_target_seconds,
            )
            created += 1

        return Response({"created": created, "date": str(selected_date)})

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


class TimeEntryViewSet(mixins.ListModelMixin, mixins.DestroyModelMixin, GenericViewSet):
    serializer_class = TimeEntrySerializer

    def get_queryset(self):
        user = _bucket_user(self.request)
        qs = TimeEntry.objects.select_related("task")
        if user is None:
            qs = qs.filter(task__user__isnull=True)
        else:
            qs = qs.filter(task__user=user)

        task_id = self.request.query_params.get("task")
        if task_id:
            qs = qs.filter(task_id=task_id)

        return qs.order_by("-start_time")
