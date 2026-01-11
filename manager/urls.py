from django.urls import path
from .views import (
    index,
    TaskListView,
    WorkerListView,
    ProjectListView,
    TaskDetailView,
    WorkerDetailView,
    TeamListView,
    ProjectDetailView,
    TeamDetailView,
    TaskCreateView,
    TaskUpdateView,
)

urlpatterns = [
    path("", index, name="index"),
    path("tasks/", TaskListView.as_view(), name="task-list"),
    path("workers/", WorkerListView.as_view(), name="worker-list"),
    path("projects/", ProjectListView.as_view(), name="project-list"),
    path("tasks/<int:pk>/", TaskDetailView.as_view(), name="task-detail"),
    path("workers/<int:pk>/", WorkerDetailView.as_view(), name="worker-detail"),
    path("teams/", TeamListView.as_view(), name="team-list"),
    path("projects/<int:pk>/", ProjectDetailView.as_view(), name="project-detail"),
    path("teams/<int:pk>", TeamDetailView.as_view(), name="team-detail"),
    path("tasks/create/", TaskCreateView.as_view(), name="task-create"),
    path("tasks/<int:pk>/update/", TaskUpdateView.as_view(), name="task-update"),
]

app_name = "manager"