from django.contrib import admin

from .models import Project, Task, TaskComment


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "owner", "created_at")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}


class TaskCommentInline(admin.TabularInline):
    model = TaskComment
    extra = 1


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "project", "status", "priority", "assignee", "due_date", "created_at")
    list_filter = ("status", "priority", "project")
    search_fields = ("title", "description")
    inlines = [TaskCommentInline]


@admin.register(TaskComment)
class TaskCommentAdmin(admin.ModelAdmin):
    list_display = ("task", "author", "created_at")
    search_fields = ("content",)
