from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Worker, Position, TaskType, Project, Tag, Team, Task


@admin.register(Worker)
class WorkerAdmin(UserAdmin):
    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            (
                "Additional info",
                {
                    "fields": (
                        "first_name",
                        "last_name",
                        "position",
                    )
                },
            ),
        )
    )
    fieldsets = UserAdmin.fieldsets + (
        (("Additional info", {"fields": ("position",)}),)
    )
    list_display = UserAdmin.list_display + ("position",)

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("name", "deadline", "priority", "is_completed", "project", "team")
    list_filter = ("priority", "team", "project", "is_completed", "deadline")
    search_fields = ("name",)
    filter_horizontal = ("assignees", "tags")


class TaskInline(admin.TabularInline):
    model = Task
    extra = 1
    fields = ("name", "deadline", "priority", "is_completed")


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    filter_horizontal = ("teams",)

    inlines = [TaskInline]

admin.site.register(Position)
admin.site.register(TaskType)
admin.site.register(Tag)
admin.site.register(Team)




