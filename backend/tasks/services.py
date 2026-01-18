from django.utils import timezone

from .models import Task, TimeEntry


def _running_entries_for_user(*, user):
    qs = TimeEntry.objects.filter(end_time__isnull=True)
    if user is None:
        return qs.filter(task__user__isnull=True)
    return qs.filter(task__user=user)


def stop_all_running_timers(*, user):
    """Enforce a single active timer per user/anonymous bucket."""

    now = timezone.now()
    entries = list(_running_entries_for_user(user=user).select_related("task"))

    for entry in entries:
        duration = int((now - entry.start_time).total_seconds())
        entry.end_time = now
        entry.duration_seconds = max(0, duration)
        entry.save(update_fields=["end_time", "duration_seconds"])

    return entries


def start_task_timer(task: Task):
    # Only one running timer across all tasks.
    stop_all_running_timers(user=task.user)

    return TimeEntry.objects.create(
        task=task,
        start_time=timezone.now(),
    )


def stop_task_timer(task: Task):
    active_entry = TimeEntry.objects.filter(task=task, end_time__isnull=True).first()

    if not active_entry:
        return None

    end_time = timezone.now()
    duration = int((end_time - active_entry.start_time).total_seconds())

    active_entry.end_time = end_time
    active_entry.duration_seconds = max(0, duration)
    active_entry.save(update_fields=["end_time", "duration_seconds"])

    return active_entry
