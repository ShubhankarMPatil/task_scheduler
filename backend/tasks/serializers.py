from rest_framework import serializers

from .models import Task, TimeEntry


class TaskSerializer(serializers.ModelSerializer):
    # Annotated in TaskViewSet.get_queryset()
    has_active_timer = serializers.BooleanField(read_only=True)
    total_time_seconds = serializers.IntegerField(read_only=True)

    class Meta:
        model = Task
        # The authenticated user is set server-side in TaskViewSet.perform_create.
        # Keeping it out of writable fields prevents validation errors and avoids
        # clients spoofing ownership.
        fields = [
            "id",
            "title",
            "description",
            "completed",
            "created_at",
            "has_active_timer",
            "total_time_seconds",
        ]
        read_only_fields = ["id", "created_at", "has_active_timer", "total_time_seconds"]


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
        read_only_fields = ["id", "task", "start_time", "end_time", "duration_seconds", "created_at"]
