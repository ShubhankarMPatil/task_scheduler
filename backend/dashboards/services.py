from django.db.models import Sum
from django.db.models.functions import Coalesce, TruncDate

from tasks.models import Task, TimeEntry


def dashboard_metrics(*, user, date):
    # Scope to user bucket
    if user is not None and getattr(user, "is_authenticated", False):
        task_qs = Task.objects.filter(user=user)
        time_entry_qs = TimeEntry.objects.filter(task__user=user)
    else:
        task_qs = Task.objects.filter(user__isnull=True)
        time_entry_qs = TimeEntry.objects.filter(task__user__isnull=True)

    # Scope to the selected day
    task_qs = task_qs.filter(date=date)
    time_entry_qs = time_entry_qs.filter(task__date=date)

    tasks_completed = task_qs.filter(completed=True).count()

    total_target_seconds = int(task_qs.aggregate(total=Coalesce(Sum("target_seconds"), 0))["total"])
    total_tracked_seconds = int(time_entry_qs.aggregate(total=Coalesce(Sum("duration_seconds"), 0))["total"])

    # Count tasks by completion status
    tasks_by_status = [
        {"status": "completed", "count": tasks_completed},
        {"status": "pending", "count": task_qs.filter(completed=False).count()},
    ]

    time_per_task = (
        time_entry_qs.values("task_id", "task__title", "task__target_seconds")
        .annotate(total_time=Coalesce(Sum("duration_seconds"), 0))
        .order_by("task__title")
    )

    # targets reached (based on completed entries only; running timers are excluded)
    targets_reached = 0
    for row in time_per_task:
        target = int(row.get("task__target_seconds") or 0)
        total = int(row.get("total_time") or 0)
        if target > 0 and total >= target:
            targets_reached += 1

    productivity_trend = (
        time_entry_qs.annotate(date=TruncDate("start_time"))
        .values("date")
        .annotate(total_time=Coalesce(Sum("duration_seconds"), 0))
        .order_by("date")
    )

    return {
        "date": str(date),
        "summary": {
            "tasks_count": task_qs.count(),
            "tasks_completed": tasks_completed,
            "targets_reached": targets_reached,
            "total_target_seconds": total_target_seconds,
            "total_tracked_seconds": total_tracked_seconds,
        },
        "tasks_by_status": tasks_by_status,
        "time_per_task": list(time_per_task),
        "productivity_trend": list(productivity_trend),
    }
