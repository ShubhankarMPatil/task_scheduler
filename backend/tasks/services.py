from django.utils import timezone
from .models import Task, TimeEntry


def start_task_timer(task: Task):
    # Stop any running timers for this task
    TimeEntry.objects.filter(task=task, end_time__isnull=True).update(
        end_time=timezone.now()
    )

    return TimeEntry.objects.create(
        task=task,
        start_time=timezone.now(),
    )


def stop_task_timer(task: Task):
    active_entry = TimeEntry.objects.filter(
        task=task, end_time__isnull=True
    ).first()

    if not active_entry:
        return None

    end_time = timezone.now()
    duration = int((end_time - active_entry.start_time).total_seconds())

    active_entry.end_time = end_time
    active_entry.duration_seconds = duration
    active_entry.save()

    return active_entry
