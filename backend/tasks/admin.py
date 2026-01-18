from django.contrib import admin

from .models import HabitTemplate, Task, TimeEntry


@admin.register(HabitTemplate)
class HabitTemplateAdmin(admin.ModelAdmin):
    list_display = ["title", "user", "default_target_seconds", "is_active", "created_at"]
    list_filter = ["is_active", "created_at", "user"]
    search_fields = ["title", "description"]
    date_hierarchy = "created_at"


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "date",
        "target_seconds",
        "user",
        "habit_template",
        "completed",
        "created_at",
    ]
    list_filter = ["date", "completed", "created_at", "user", "habit_template"]
    search_fields = ["title", "description"]
    date_hierarchy = "date"


@admin.register(TimeEntry)
class TimeEntryAdmin(admin.ModelAdmin):
    list_display = ["task", "start_time", "end_time", "duration_seconds"]
    list_filter = ["start_time", "task"]
    search_fields = ["task__title"]
    date_hierarchy = "start_time"
    readonly_fields = ["created_at"]
