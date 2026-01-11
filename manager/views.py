from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import render
from django.urls import reverse_lazy, reverse
from django.views import generic

from .forms.task_form import TaskForm
from .models import Worker, Task, Project, Team

def index(request):
    """View function for the home page of the site"""
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

# --- TASK VIEWS ---
class TaskListView(LoginRequiredMixin, generic.ListView):
    model = Task
    template_name = "manager/task_list.html"
    context_object_name = "task_list"
    paginate_by = 10

    def get_queryset(self):
        queryset = Task.objects.select_related("task_type", "project")
        name = self.request.GET.get("name", "")
        if name:
            return queryset.filter(name__icontains=name)
        return queryset

class TaskDetailView(LoginRequiredMixin, generic.DetailView):
    model = Task
    template_name = "manager/task_detail.html"

class TaskCreateView(LoginRequiredMixin, generic.CreateView):
    model = Task
    form_class = TaskForm
    template_name = "manager/forms/task_form.html"
    success_url = reverse_lazy("manager:task-list")

    def get_initial(self):
        initial = super().get_initial()
        project_id = self.request.GET.get("project")
        if project_id:
            initial["project"] = project_id
        worker_id = self.request.GET.get("worker")
        if worker_id:
            initial["assignees"] = [worker_id]
        return initial

class TaskUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Task
    form_class = TaskForm
    template_name = "manager/forms/task_form.html"

    def get_success_url(self):
        return reverse("manager:task-detail", kwargs={"pk": self.object.pk})

class TaskDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Task
    template_name = "manager/forms/confirm_delete.html"
    success_url = reverse_lazy("manager:task-list")

# --- PROJECT VIEWS ---
class ProjectListView(LoginRequiredMixin, generic.ListView):
    model = Project
    template_name = "manager/project_list.html"
    paginate_by = 6

    def get_queryset(self):
        queryset = Project.objects.all()
        name = self.request.GET.get("name", "")
        if name:
            return queryset.filter(name__icontains=name)
        return queryset

class ProjectDetailView(LoginRequiredMixin, generic.DetailView):
    model = Project
    template_name = "manager/project_detail.html"

class ProjectCreateView(LoginRequiredMixin, generic.CreateView):
    model = Project
    fields = "__all__"
    template_name = "manager/forms/task_form.html"
    success_url = reverse_lazy("manager:project-list")

class ProjectUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Project
    fields = "__all__"
    template_name = "manager/forms/task_form.html"

    def get_success_url(self):
        return reverse("manager:project-detail", kwargs={"pk": self.object.pk})

class ProjectDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Project
    template_name = "manager/forms/confirm_delete.html"
    success_url = reverse_lazy("manager:project-list")

# --- TEAM VIEWS ---
class TeamListView(LoginRequiredMixin, generic.ListView):
    model = Team
    paginate_by = 5

    def get_queryset(self):
        return Team.objects.prefetch_related("workers", "projects")

class TeamDetailView(LoginRequiredMixin, generic.DetailView):
    model = Team

class TeamCreateView(LoginRequiredMixin, generic.CreateView):
    model = Team
    fields = "__all__"
    template_name = "manager/forms/task_form.html"
    success_url = reverse_lazy("manager:team-list")

class TeamUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Team
    fields = "__all__"
    template_name = "manager/forms/task_form.html"

    def get_success_url(self):
        return reverse("manager:team-detail", kwargs={"pk": self.object.pk})

class TeamDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Team
    template_name = "manager/forms/confirm_delete.html"
    success_url = reverse_lazy("manager:team-list")

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["all_missions"] = Task.objects.filter(
            Q(assignees=self.object) | Q(team__workers=self.object)
        ).distinct().select_related("project")
        return context


class WorkerCreateView(LoginRequiredMixin, generic.CreateView):
    model = Worker
    fields = ["username", "first_name", "last_name", "position"]
    template_name = "manager/forms/task_form.html"
    success_url = reverse_lazy("manager:worker-list")


class WorkerUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Worker
    fields = ["username", "first_name", "last_name", "position"]
    template_name = "manager/forms/task_form.html"

    def get_success_url(self):
        return reverse("manager:worker-detail", kwargs={"pk": self.object.pk})


class WorkerDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Worker
    template_name = "manager/forms/confirm_delete.html"
    success_url = reverse_lazy("manager:worker-list")