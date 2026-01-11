from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.shortcuts import render
from django.urls import reverse_lazy, reverse
from django.views import generic

from .forms.task_form import TaskForm
from .forms.worker_form import WorkerCreationForm
from .models import Worker, Task, Project, Team


def index(request):
    if not request.user.is_authenticated:
        return render(request, "registration/login.html")

    num_workers = Worker.objects.count()
    num_tasks = Task.objects.count()
    num_projects = Project.objects.count()
    num_teams = Team.objects.count()

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


class TaskListView(LoginRequiredMixin, generic.ListView):
    model = Task
    template_name = "manager/task_list.html"
    context_object_name = "task_list"
    paginate_by = 5

    def get_queryset(self):
        queryset = Task.objects.select_related("project").prefetch_related("assignees")
        name = self.request.GET.get("name", "")
        if name:
            return queryset.filter(name__icontains=name)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_name"] = self.request.GET.get("name", "")
        return context


class TaskDetailView(LoginRequiredMixin, generic.DetailView):
    model = Task
    template_name = "manager/task_detail.html"
    context_object_name = "task"

    def get_queryset(self):
        return Task.objects.select_related("project").prefetch_related("assignees", "team__workers")


class TaskCreateView(LoginRequiredMixin, generic.CreateView):
    model = Task
    form_class = TaskForm
    template_name = "manager/forms/task_form.html"
    success_url = reverse_lazy("manager:task-list")


class TaskUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Task
    form_class = TaskForm
    template_name = "manager/forms/task_form.html"
    success_url = reverse_lazy("manager:task-list")


class TaskDeleteView(LoginRequiredMixin, UserPassesTestMixin, generic.DeleteView):
    model = Task
    template_name = "manager/forms/confirm_delete.html"
    success_url = reverse_lazy("manager:task-list")

    def test_func(self):
        return self.request.user.is_superuser


class ProjectListView(LoginRequiredMixin, generic.ListView):
    model = Project
    template_name = "manager/project_list.html"
    context_object_name = "project_list"
    paginate_by = 6

    def get_queryset(self):
        queryset = Project.objects.all()
        name = self.request.GET.get("name", "")
        if name:
            return queryset.filter(name__icontains=name)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_name"] = self.request.GET.get("name", "")
        return context


class ProjectDetailView(LoginRequiredMixin, generic.DetailView):
    model = Project
    template_name = "manager/project_detail.html"
    context_object_name = "project"

    def get_queryset(self):
        return Project.objects.prefetch_related("teams__workers", "tasks__assignees")


class ProjectCreateView(LoginRequiredMixin, generic.CreateView):
    model = Project
    fields = "__all__"
    template_name = "manager/forms/task_form.html"
    success_url = reverse_lazy("manager:project-list")


class ProjectUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Project
    fields = "__all__"
    template_name = "manager/forms/task_form.html"
    success_url = reverse_lazy("manager:project-list")


class ProjectDeleteView(LoginRequiredMixin, UserPassesTestMixin, generic.DeleteView):
    model = Project
    template_name = "manager/forms/confirm_delete.html"
    success_url = reverse_lazy("manager:project-list")

    def test_func(self):
        return self.request.user.is_superuser


class TeamListView(LoginRequiredMixin, generic.ListView):
    model = Team
    template_name = "manager/team_list.html"
    context_object_name = "team_list"
    paginate_by = 5

    def get_queryset(self):
        return Team.objects.prefetch_related("workers", "projects")


class TeamDetailView(LoginRequiredMixin, generic.DetailView):
    model = Team
    template_name = "manager/team_detail.html"
    context_object_name = "team"

    def get_queryset(self):
        return Team.objects.prefetch_related("workers__position", "projects")


class TeamCreateView(LoginRequiredMixin, generic.CreateView):
    model = Team
    fields = "__all__"
    template_name = "manager/forms/task_form.html"
    success_url = reverse_lazy("manager:team-list")


class TeamUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Team
    fields = "__all__"
    template_name = "manager/forms/task_form.html"
    success_url = reverse_lazy("manager:team-list")


class TeamDeleteView(LoginRequiredMixin, UserPassesTestMixin, generic.DeleteView):
    model = Team
    template_name = "manager/forms/confirm_delete.html"
    success_url = reverse_lazy("manager:team-list")

    def test_func(self):
        return self.request.user.is_superuser


class WorkerListView(LoginRequiredMixin, generic.ListView):
    model = Worker
    paginate_by = 12

    def get_queryset(self):
        queryset = Worker.objects.select_related("position")
        username = self.request.GET.get("username", "")
        if username:
            return queryset.filter(username__icontains=username)
        return queryset


class WorkerDetailView(LoginRequiredMixin, generic.DetailView):
    model = Worker

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["all_missions"] = Task.objects.filter(
            Q(assignees=self.request.user) | Q(team__workers=self.request.user)
        ).distinct().select_related("project")
        return context


class WorkerCreateView(LoginRequiredMixin, generic.CreateView):
    model = Worker
    form_class = WorkerCreationForm
    template_name = "manager/forms/task_form.html"
    success_url = reverse_lazy("manager:worker-list")


class WorkerUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Worker
    fields = ["username", "first_name", "last_name", "position", "email"]
    template_name = "manager/forms/task_form.html"

    def get_success_url(self):
        return reverse("manager:worker-detail", kwargs={"pk": self.object.pk})


class WorkerDeleteView(LoginRequiredMixin, UserPassesTestMixin, generic.DeleteView):
    model = Worker
    template_name = "manager/forms/confirm_delete.html"
    success_url = reverse_lazy("manager:worker-list")

    def test_func(self):
        return self.request.user.is_superuser