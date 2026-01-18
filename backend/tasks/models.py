from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class HabitTemplate(models.Model):
    """A persisted, reusable template that generates a daily task instance."""

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    # Daily goal (seconds) for tasks generated from this template.
    default_target_seconds = models.IntegerField(default=0)

    is_active = models.BooleanField(default=True)

    # Demo mode allows anonymous data.
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class Task(models.Model):
    """A daily task instance (optionally generated from a HabitTemplate)."""

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    # If present, points back to the template this task came from.
    # Title/description are stored on the task to keep historical days stable.
    habit_template = models.ForeignKey(
        HabitTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tasks",
    )

    date = models.DateField(default=timezone.localdate)

    # Daily goal for this specific day (seconds).
    target_seconds = models.IntegerField(default=0)

    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    # Frontend currently has no auth. Allow anonymous tasks by making user
    # optional. If/when you add auth, you can make this required again.
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({self.date})"


class TimeEntry(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="time_entries")
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Time Entries"
        ordering = ["-start_time"]

    def __str__(self):
        return f"{self.task.title} - {self.start_time}"
