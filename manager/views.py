from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
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

    num_critical_tasks = Task.objects.filter(
        priority__iexact="urgent",
        is_completed=False
    ).count()

    my_tasks = Task.objects.filter(
        assignees=request.user,
        is_completed=False
    ).select_related("project").order_by("deadline")[:5]

    context = {
        "num_workers": num_workers,
        "num_tasks": num_tasks,
        "num_projects": num_projects,
        "num_teams": num_teams,
        "num_critical_tasks": num_critical_tasks,
        "my_tasks": my_tasks,
    }

    return render(request, "manager/index.html", context=context)


# --- TASK VIEWS ---

class TaskListView(LoginRequiredMixin, generic.ListView):
    model = Task
    template_name = "manager/task_list.html"
    context_object_name = "task_list"
    paginate_by = 10

    def get_queryset(self):
        queryset = Task.objects.select_related("task_type", "project")
        name = self.request.GET.get("name", "")

        if name.lower() == "urgent":
            return queryset.filter(priority__iexact="urgent", is_completed=False)

        if name:
            return queryset.filter(name__icontains=name)
        return queryset


class TaskDetailView(LoginRequiredMixin, generic.DetailView):
    model = Task


class TaskCreateView(LoginRequiredMixin, generic.CreateView):
    model = Task
    form_class = TaskForm
    template_name = "manager/forms/task_form.html"
    success_url = reverse_lazy("manager:task-list")


class TaskUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Task
    form_class = TaskForm
    template_name = "manager/forms/task_form.html"

    def get_success_url(self):
        return reverse("manager:task-detail", kwargs={"pk": self.object.pk})


class TaskDeleteView(LoginRequiredMixin, UserPassesTestMixin, generic.DeleteView):
    model = Task
    template_name = "manager/forms/confirm_delete.html"
    success_url = reverse_lazy("manager:task-list")

    def test_func(self):
        return self.request.user.is_superuser


def toggle_task_completion(request, pk):
    task = get_object_or_404(Task, id=pk)
    task.is_completed = not task.is_completed
    task.save()
    return redirect(request.META.get('HTTP_REFERER', 'manager:task-list'))


# --- PROJECT VIEWS ---

class ProjectListView(LoginRequiredMixin, generic.ListView):
    model = Project
    paginate_by = 6

    def get_queryset(self):
        queryset = Project.objects.prefetch_related("teams__workers")
        name = self.request.GET.get("name", "")
        if name:
            return queryset.filter(name__icontains=name)
        return queryset


class ProjectDetailView(LoginRequiredMixin, generic.DetailView):
    model = Project
    queryset = Project.objects.prefetch_related("teams__workers", "tasks")


class ProjectCreateView(LoginRequiredMixin, UserPassesTestMixin, generic.CreateView):
    model = Project
    fields = "__all__"
    template_name = "manager/forms/task_form.html"
    success_url = reverse_lazy("manager:project-list")

    def test_func(self):
        return self.request.user.is_superuser


class ProjectUpdateView(LoginRequiredMixin, UserPassesTestMixin, generic.UpdateView):
    model = Project
    fields = "__all__"
    template_name = "manager/forms/task_form.html"

    def get_success_url(self):
        return reverse("manager:project-detail", kwargs={"pk": self.object.pk})

    def test_func(self):
        return self.request.user.is_superuser


class ProjectDeleteView(LoginRequiredMixin, UserPassesTestMixin, generic.DeleteView):
    model = Project
    template_name = "manager/forms/confirm_delete.html"
    success_url = reverse_lazy("manager:project-list")

    def test_func(self):
        return self.request.user.is_superuser


# --- TEAM VIEWS ---

class TeamListView(LoginRequiredMixin, generic.ListView):
    model = Team
    paginate_by = 6

    def get_queryset(self):
        return Team.objects.prefetch_related(
            "projects",
            "workers__position"
        )


class TeamDetailView(LoginRequiredMixin, generic.DetailView):
    model = Team

    def get_queryset(self):
        return Team.objects.prefetch_related(
            "projects",
            "workers__position",
            "tasks__task_type"
        )


class TeamCreateView(LoginRequiredMixin, UserPassesTestMixin, generic.CreateView):
    model = Team
    fields = "__all__"
    template_name = "manager/forms/task_form.html"
    success_url = reverse_lazy("manager:team-list")

    def test_func(self):
        return self.request.user.is_superuser


class TeamUpdateView(LoginRequiredMixin, UserPassesTestMixin, generic.UpdateView):
    model = Team
    fields = "__all__"
    template_name = "manager/forms/task_form.html"

    def get_success_url(self):
        return reverse("manager:team-detail", kwargs={"pk": self.object.pk})

    def test_func(self):
        return self.request.user.is_superuser


class TeamDeleteView(LoginRequiredMixin, UserPassesTestMixin, generic.DeleteView):
    model = Team
    template_name = "manager/forms/confirm_delete.html"
    success_url = reverse_lazy("manager:team-list")

    def test_func(self):
        return self.request.user.is_superuser


# --- WORKER VIEWS ---

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
    queryset = Worker.objects.select_related("position")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["assigned_tasks"] = Task.objects.filter(
            Q(assignees=self.object) | Q(team__workers=self.object)
        ).distinct().select_related(
            "project",
            "task_type",
            "team"
        ).prefetch_related("assignees__position")

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

