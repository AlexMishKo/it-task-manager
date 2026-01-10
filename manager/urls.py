from django.urls import path
from .views import (
    index,
    TaskListView,
    WorkerListView,
    ProjectListView,
)

urlpatterns = [
    path("", index, name="index"),
    path("tasks/", TaskListView.as_view(), name="task-list"),
    path("workers/", WorkerListView.as_view(), name="worker-list"),
    path("projects/", ProjectListView.as_view(), name="project-list"),
]

app_name = "manager"