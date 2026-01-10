from django.shortcuts import render
from django.views import generic
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
    num_critical_tasks = Task.objects.filter(priority="Urgent", is_completed=False).count()
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
    paginate_by = 5

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





