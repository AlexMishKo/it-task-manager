from django.shortcuts import render
from .models import Worker, Task, Project, Team

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



