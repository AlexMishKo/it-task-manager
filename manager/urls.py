from django.urls import path
from .views import (
    index,
    TaskListView,
    WorkerListView,
    ProjectListView,
    TaskDetailView,
    WorkerDetailView,
    TeamListView,
)

urlpatterns = [
    path("", index, name="index"),
    path("tasks/", TaskListView.as_view(), name="task-list"),
    path("workers/", WorkerListView.as_view(), name="worker-list"),
    path("projects/", ProjectListView.as_view(), name="project-list"),
    path("tasks/<int:pk>/", TaskDetailView.as_view(), name="task-detail"),
    path("workers/<int:pk>/", WorkerDetailView.as_view(), name="worker-detail"),
    path("teams/", TeamListView.as_view(), name="team-list"),
]

app_name = "manager"