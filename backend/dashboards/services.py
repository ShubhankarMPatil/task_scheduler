from django.db.models import Sum
from django.db.models.functions import TruncDate

from tasks.models import Task, TimeEntry


def dashboard_metrics(*, user):
    if user is not None and getattr(user, "is_authenticated", False):
        task_qs = Task.objects.filter(user=user)
        time_entry_qs = TimeEntry.objects.filter(task__user=user)
    else:
        task_qs = Task.objects.filter(user__isnull=True)
        time_entry_qs = TimeEntry.objects.filter(task__user__isnull=True)

    # Count tasks by completion status
    tasks_by_status = [
        {"status": "completed", "count": task_qs.filter(completed=True).count()},
        {"status": "pending", "count": task_qs.filter(completed=False).count()},
    ]

    time_per_task = (
        time_entry_qs.values("task__title").annotate(total_time=Sum("duration_seconds"))
    )

    productivity_trend = (
        time_entry_qs.annotate(date=TruncDate("start_time"))
        .values("date")
        .annotate(total_time=Sum("duration_seconds"))
        .order_by("date")
    )

    return {
        "tasks_by_status": tasks_by_status,
        "time_per_task": list(time_per_task),
        "productivity_trend": list(productivity_trend),
    }
