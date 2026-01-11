from django.db.models import Q
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import generic

from .forms.task_form import TaskForm

from .models import (
    Worker,
    Task,
    Project,
    Team
)

def index(request):
    """View function for the home page of the site"""

    #counting main objects
    num_workers = Worker.objects.count()
    num_tasks = Task.objects.count()
    num_projects = Project.objects.count()
    num_teams = Team.objects.count()

    #advanced statistics
    num_critical_tasks = Task.objects.filter(priority__iexact="urgent", is_completed=False).count()
    num_completed_tasks = Task.objects.filter(is_completed=True).count()

    context = {
        "num_workers": num_workers,
        "num_tasks": num_tasks,
        "num_projects": num_projects,
        "num_teams": num_teams,
        "num_critical_tasks": num_critical_tasks,
        "num_completed_tasks": num_completed_tasks,
    }

    return render(request, "manager/index.html", context=context)


class TaskListView(generic.ListView):
    model = Task
    template_name = "manager/task_list.html"
    context_object_name = "task_list"
    paginate_by = 10

    def get_queryset(self):
        queryset = Task.objects.select_related("task_type", "project")
        form_name = self.request.GET.get("name", "")
        if form_name:
            return queryset.filter(name__icontains=form_name)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_name"] = self.request.GET.get("name", "")
        return context


class TaskDetailView(generic.DetailView):
    model = Task
    template_name = "manager/task_detail.html"
    context_object_name = "task"

    def get_queryset(self):
        return Task.objects.select_related(
            "task_type",
            "project",
            "team",
        ).prefetch_related("assignees", "tags")


class TaskCreateView(generic.CreateView):
    model = Task
    form_class = TaskForm
    template_name = "manager/forms/task_form.html"
    success_url = reverse_lazy("manager:task-list")

    def get_initial(self):
        initial = super().get_initial()
        project_id = self.request.GET.get("project")
        worker_id = self.request.GET.get("worker")

        if project_id:
            initial["project"] = project_id
        if worker_id:
            initial["assignees"] = [worker_id]

        return initial


class TaskUpdateView(generic.UpdateView):
    model = Task
    form_class = TaskForm
    template_name = "manager/forms/task_form.html"

    def get_success_url(self):
        return reverse_lazy("manager:task-detail", kwargs={"pk": self.object.pk})


class WorkerListView(generic.ListView):
    model = Worker
    template_name = "manager/worker_list.html"
    context_object_name = "worker_list"
    paginate_by = 10

    def get_queryset(self):
        queryset = Worker.objects.select_related("position")
        username = self.request.GET.get("username", "")
        if username:
            return queryset.filter(username__icontains=username)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_username"] = self.request.GET.get("username", "")
        return context


class WorkerDetailView(generic.DetailView):
    model = Worker
    template_name = "manager/worker_detail.html"
    context_object_name = "worker"

    def get_queryset(self):
        return Worker.objects.prefetch_related(
            "tasks__project",
            "tasks__task_type",
            "teams__projects"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        worker = self.object
        all_missions = Task.objects.filter(
            Q(assignees=worker) | Q(team__in=worker.teams.all())
        ).distinct().select_related("project", "task_type")
        context["all_missions"] = all_missions
        return context


class ProjectListView(generic.ListView):
    model = Project
    template_name = "manager/project_list.html"
    context_object_name = "project_list"
    paginate_by = 10

    def get_queryset(self):
        queryset = Project.objects.prefetch_related("teams")
        name = self.request.GET.get("name", "")
        if name:
            return queryset.filter(name__icontains=name)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_name"] = self.request.GET.get("name", "")
        return context


class ProjectDetailView(generic.DetailView):
    model = Project
    template_name = "manager/project_detail.html"
    context_object_name = "project"

    def get_queryset(self):
        return Project.objects.prefetch_related(
            "teams__workers",
            "tasks__assignees",
        )


class TeamListView(generic.ListView):
    model = Team
    template_name = "manager/team_list.html"
    context_object_name = "team_list"
    paginate_by = 5

    def get_queryset(self):
        return Team.objects.prefetch_related("workers", "projects")


class TeamDetailView(generic.DetailView):
    model = Team
    template_name = "manager/team_detail.html"
    context_object_name = "team"

    def get_queryset(self):
        return Team.objects.prefetch_related(
            "workers__position",
            "projects"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        team = self.object

        context["team_tasks"] = Task.objects.filter(team=team).select_related(
            "project", "task_type"
        )
        return context









