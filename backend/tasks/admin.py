from django.contrib import admin
from .models import Task, TimeEntry


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'completed', 'created_at']
    list_filter = ['completed', 'created_at', 'user']
    search_fields = ['title', 'description']
    date_hierarchy = 'created_at'


@admin.register(TimeEntry)
class TimeEntryAdmin(admin.ModelAdmin):
    list_display = ['task', 'start_time', 'end_time', 'duration_seconds']
    list_filter = ['start_time', 'task']
    search_fields = ['task__title']
    date_hierarchy = 'start_time'
    readonly_fields = ['created_at']