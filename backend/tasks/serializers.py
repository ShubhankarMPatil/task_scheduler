from django.utils import timezone
from rest_framework import serializers

from .models import HabitTemplate, Task, TimeEntry


class HabitTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = HabitTemplate
        fields = [
            "id",
            "title",
            "description",
            "default_target_seconds",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class TaskSerializer(serializers.ModelSerializer):
    # Annotated in TaskViewSet.get_queryset()
    has_active_timer = serializers.BooleanField(read_only=True)
    total_time_seconds = serializers.IntegerField(read_only=True)
    active_entry_start_time = serializers.DateTimeField(read_only=True, allow_null=True)

    habit_template_id = serializers.IntegerField(read_only=True)

    progress_seconds = serializers.SerializerMethodField()
    remaining_seconds = serializers.SerializerMethodField()
    progress_percent = serializers.SerializerMethodField()
    target_reached = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "description",
            "habit_template_id",
            "date",
            "target_seconds",
            "completed",
            "created_at",
            "has_active_timer",
            "active_entry_start_time",
            "total_time_seconds",
            "progress_seconds",
            "remaining_seconds",
            "progress_percent",
            "target_reached",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "habit_template_id",
            "has_active_timer",
            "active_entry_start_time",
            "total_time_seconds",
            "progress_seconds",
            "remaining_seconds",
            "progress_percent",
            "target_reached",
        ]

    def _running_seconds(self, obj: Task) -> int:
        if not obj.active_entry_start_time:
            return 0
        now = timezone.now()
        delta = now - obj.active_entry_start_time
        return max(0, int(delta.total_seconds()))

    def get_progress_seconds(self, obj: Task) -> int:
        return int(obj.total_time_seconds or 0) + self._running_seconds(obj)

    def get_remaining_seconds(self, obj: Task) -> int:
        target = int(obj.target_seconds or 0)
        return max(0, target - self.get_progress_seconds(obj))

    def get_progress_percent(self, obj: Task) -> float:
        target = int(obj.target_seconds or 0)
        if target <= 0:
            return 0.0
        return min(100.0, (self.get_progress_seconds(obj) / target) * 100.0)

    def get_target_reached(self, obj: Task) -> bool:
        target = int(obj.target_seconds or 0)
        return target > 0 and self.get_progress_seconds(obj) >= target


class TimeEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeEntry
        fields = [
            "id",
            "task",
            "start_time",
            "end_time",
            "duration_seconds",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "task",
            "start_time",
            "end_time",
            "duration_seconds",
            "created_at",
        ]
