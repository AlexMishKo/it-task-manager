from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Worker, Position, TaskType

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
    admin.site.register(Position)
    admin.site.register(TaskType)


